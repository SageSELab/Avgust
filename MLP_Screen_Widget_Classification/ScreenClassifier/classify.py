from sklearn.neural_network import MLPClassifier
import numpy as np
import os
from data_reader import prepare_app_fold_data, prepare_autoencoder_data, prepare_data, prepare_app_fold_autoencoder_data
from sklearn.metrics import confusion_matrix
import collections
import pytesseract
from PIL import Image
import cv2
import nltk
from numpy import dot
from numpy.linalg import norm
from text_similarity_calculator import SimilarityCalculator
from os.path import exists

# requires installation of pytesseract for OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
nltk.download('words')

def warn(*args, **kwargs): # hides sklearn warnings
    pass
import warnings
warnings.warn = warn

k = 5

def prepare_clas():
    clas = MLPClassifier(hidden_layer_sizes=(40,),
                         early_stopping=False, verbose=False, max_iter=600,
                         solver='adam', activation='relu', n_iter_no_change=20)
    return clas

# top-1 accuracy
def accuracy(confusion_matrix):
    diagonal_sum = confusion_matrix.trace()
    sum_of_all_elements = confusion_matrix.sum()
    return diagonal_sum / sum_of_all_elements

# filters extracted text
def get_extracted_text(filename):
    path = r'C:\Users\HyoJP\Desktop\Screen_Widget_Classification\ScreenClassifier\OCR_text\\'+ filename.split('\\')[-1][:-4] + '.txt'
    with open(path) as f:
        text = f.read()
    extracted_text = text.split()

    # all words in the dictionary
    words = set(nltk.corpus.words.words())
    return [word.lower() for word in extracted_text if word.lower() in words and not len(word) == 1] # gets rid of numbers, nonwords, and single letters


class ScreenClassifier(object):
    def __init__(self, autoencoder=False, divide_by_app=False, path=None):
        if path is not None:
            self.load(path)
        else:
            self.clas = prepare_clas()
            self.autoencoder = autoencoder
            self.divide_by_app = divide_by_app
            self.similarity_calculator = SimilarityCalculator()

    def learn(self, app_name=None):
        training_set = None
        validation_set = None
        input_size = None

        if self.autoencoder:
            input_size = 4608
            if self.divide_by_app:
                training_set, validation_set = prepare_app_fold_autoencoder_data(
                    r'C:\Users\HyoJP\Desktop\Screen_Widget_Classification\ScreenClassifier\\' + r'autoencoder_embeddings\embeddings(1)',
                    "comp-LS-annotations.csv", app_name, remove_wrong_dimensions=True)
            else:
                data = prepare_autoencoder_data(
                    r'C:\Users\HyoJP\Desktop\Screen_Widget_Classification\ScreenClassifier\\' + r'autoencoder_embeddings\embeddings(1)',
                    "comp-LS-annotations.csv", remove_wrong_dimensions=True)

                size = len(data)
                training_set = data[:int(size*0.9)]
                validation_set = data[int(size*0.9):]

        else:
            input_size = 768
            if self.divide_by_app:
                training_set, validation_set = prepare_app_fold_data("screen2vec_screen_embeddings", "comp-LS-annotations.csv", app_name, remove_wrong_dimensions=True)
            else:
                data = prepare_data("screen2vec_screen_embeddings", "comp-LS-annotations.csv", remove_wrong_dimensions=True)

                size = len(data)
                training_set = data[:int(size * 0.9)]
                validation_set = data[int(size * 0.9):]

        X_train = np.empty((0, input_size), np.float32)
        for row in training_set.embedding:
            # print(row.shape)
            row = row.reshape(1, row.shape[0])
            X_train = np.append(X_train, row, axis=0)

        # get path and labels
        values = training_set.iloc[:, -1].values
        Y_train = np.array([v[0] for v in values])
        X_train_paths = [v[1] for v in values]


        X_val = np.empty((0, input_size), float)
        for row in validation_set.embedding:
            row = row.reshape(1, row.shape[0])
            X_val = np.append(X_val, row, axis=0)
        values = validation_set.iloc[:, -1].values
        y_val = np.array([v[0] for v in values])
        X_val_paths = [v[1] for v in values]

        # save OCR text to text files
        #for path in X_val_paths:
        #    print(path)
        #    if exists(path) and not exists(r'C:\Users\HyoJP\Desktop\Screen_Widget_Classification\ScreenClassifier\OCR_text\\' + path.split('\\')[-1][:-4] + '.txt'):
        #        extracted_text = OCR(path)
        #        textfile = open(r'C:\Users\HyoJP\Desktop\Screen_Widget_Classification\ScreenClassifier\OCR_text\\' + path.split('\\')[-1][:-4] + '.txt', "w")
        #        for e in extracted_text:
        #            textfile.write(e + "\n")
        #return

        if len(y_val) == 0:
            print("NO TESTING DATA:", app_name)
            return

        #train
        self.clas.fit(X_train, Y_train)
        self.classes = self.clas.classes_


        print("Training size:", len(Y_train))
        print("Testing size:", len(y_val))

        # output information about app data
        if self.divide_by_app:
            training_count = collections.defaultdict(int)
            for label in Y_train:
                training_count[label] += 1
            print("Training IRs:", training_count)

            testing_count = collections.defaultdict(int)
            for label in y_val:
                testing_count[label] += 1
            print("Testing IRs:", testing_count)
            print("Number of testing labels:", len(testing_count))

            missing_count = []
            for label in testing_count.keys():
                if label not in training_count:
                    missing_count.append(label)
            print("No labels in training:", missing_count)

            missing_count = []
            for label in testing_count.keys():
                if testing_count[label] > training_count[label]:
                    missing_count.append(label)
            print("Less training labels than testing labels:", missing_count)

        # classify
        y_pred = self.clas.predict(X_val)
        y_pred_proba = self.clas.predict_proba(X_val)

        # step 1 and 2 of OCR
        text_for_each_label = collections.defaultdict(list)
        for i in range(len(X_train_paths)):
            if not exists(X_train_paths[i]):
                print("COULD NOT FIND FILE: ", X_train_paths[i])
                continue
            text_for_each_label[Y_train[i]] += get_extracted_text(X_train_paths[i])

        common_words = ['selected', 'tab', 'not', 'selected', 'bar', 'button',
                        'menubar', 'icon', 'view', 'ub', 'container', 'row',
                        'scroll', 'horizontal', 'imageview', 'icn', 'btn']
        for key in text_for_each_label:
            text_for_each_label[key] = set(text_for_each_label[key])

            # remove common words
            for word in text_for_each_label[key].copy():
                if word.lower() in common_words:
                    text_for_each_label[key].remove(word)
            #print(key, text_for_each_label[key])


        # step 4
        text_from_OCR = []
        for path in X_val_paths:
            if not exists(path):
                print("COULD NOT FIND INPUT FILE: ", path)
                continue
            extracted_text = set(get_extracted_text(path))
            for word in extracted_text.copy():
                if word.lower() in common_words:
                    extracted_text.remove(word)
            text_from_OCR.append(extracted_text)
        #print(text_from_OCR[:2])


        # get top-1 and top-5 accuracy
        cm = confusion_matrix(y_val, y_pred)
        print("Number of training labels:", len(self.classes))

        # replaces label to index of that label in self.classes
        for i in range(len(y_val)):
            loc = np.where(self.classes == y_val[i])[0]
            if len(loc) != 0:
                y_val[i] = loc[0]
            else:
                y_val[i] = -1
        y_val = y_val.astype('int16')

        prob_sort = np.argsort(y_pred_proba, 1)
        #print(prob_sort.shape)
        #print(y_val.shape)
        #print(prob_sort[0, :].shape)

        counter = 0
        top_k_classification = prob_sort[:, -k:]
        for i in range(len(y_val)):
            if y_val[i] in top_k_classification[i]:
                counter += 1
        print("Top-1: ", accuracy(cm), " Top-", k, ": ", counter/len(y_val))


        # step 5
        top_k_labels = self.classes[top_k_classification]

        OCR_accuracy = 0
        label_accuracy = collections.defaultdict(int)
        label_counter = collections.defaultdict(int)

        for i in range(len(top_k_labels)):
            text_of_input = text_from_OCR[i]
            text_of_input_str = ''
            for word in text_from_OCR[i]:
                text_of_input_str += word + ' '

            # get text for each of top 5 label and store as list
            label_texts = []
            for j in range(k):
                label_text = text_for_each_label[top_k_labels[i][j]]
                if label_text:
                    label_texts.append(label_text)
                else:
                    print('missing label for:', top_k_labels[i][j])
            #print(len(label_texts))
            # convert each list into a string and calculate similarity
            label_texts_str = []
            similarity_value = []
            for text in label_texts:
                label_texts_str.append('')
                for word in text:
                    label_texts_str[-1] += word + ' '
                similarity_value.append(self.similarity_calculator.calc_similarity(label_texts_str[-1], text_of_input_str))

            # find the index of label with greatest similarity value
            matched_label_index = max(enumerate(similarity_value), key=lambda x: x[1])[0]

            label_accuracy[self.classes[y_val[i]]] += 0

            # if classified correctly
            if top_k_classification[i, matched_label_index] == y_val[i]:
                OCR_accuracy += 1
                label_accuracy[self.classes[y_val[i]]] += 1

                print("CLASSIFIED CORRECTLY:", self.classes[y_val[i]])
                print("\tFILE:", X_val_paths[i])
                print("\tINPUT TEXT:", text_of_input)
                print("\tLABEL TEXT:", label_texts_str[matched_label_index])
                print("\tSIMILARITY VALUE:", similarity_value[matched_label_index])
                print("\tALL SIMILARITY VALUES:", similarity_value)
                print()
            # if classified incorrectly
            else:
                print("CLASSIFIED INCORRECTLY:", self.classes[y_val[i]])
                print("\tFILE:", X_val_paths[i])
                print("\tCLASSIFIED AS:", self.classes[top_k_classification[i, matched_label_index]])
                print("\tINPUT TEXT:", text_of_input)
                print("\tPREDICTED LABEL TEXT:", label_texts_str[matched_label_index])
                print("\tCORRECT LABEL TEXT:", text_for_each_label[self.classes[y_val[i]]])
                print("\tSIMILARITY VALUE:", similarity_value[matched_label_index])
                print("\tALL SIMILARITY VALUES:", similarity_value)
                print()

            label_counter[self.classes[y_val[i]]] += 1

        print("OCR ACCURACY: ", OCR_accuracy/len(top_k_labels))
        for label in label_accuracy.keys():
            print(label, " ACCURACY:", label_accuracy[label]/label_counter[label])

def get_app_names(embeddings_directory):
    app_names = []
    for embedding_file in os.listdir(embeddings_directory):
        app_name = embedding_file.split("-")[0].lower()
        if app_name not in app_names:
            app_names.append(app_name)
    return app_names


def OCR(path, words_only=True):
    image = cv2.imread(path)
    image = cv2.medianBlur(image, 3) # try turning to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(Image.fromarray(image))
    text = text.split()

    return [word.lower() for word in text]


if __name__ == "__main__":
    # classify everything
    #screen_classifier_all = ScreenClassifier()
    #print("Training with screen2vec:")
    #screen_classifier_all.learn()

    #screen_classifier_all_auto = ScreenClassifier(autoencoder=True)
    #print("Training with autoencoder:")
    #screen_classifier_all_auto.learn()

    # classify specific apps
    screen_classifier_dimensions_fixed = ScreenClassifier(divide_by_app=True)
    screen_classifier_auto_dimensions_fixed = ScreenClassifier(autoencoder=True, divide_by_app=True)
    app_names = get_app_names("screen2vec_screen_embeddings")

    for app in app_names:
        if app == '6pm':
            print("Classifying:", app)
            print("Training with (screen2vec):")
            screen_classifier_dimensions_fixed.learn(app)
            print()
            print("Training with (autoencoder):")
            screen_classifier_auto_dimensions_fixed.learn(app)
            print()
            print()