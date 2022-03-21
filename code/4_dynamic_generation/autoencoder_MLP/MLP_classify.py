from sklearn.neural_network import MLPClassifier
import numpy as np
import os
from data_reader import *
from sklearn.metrics import confusion_matrix
import collections
import pytesseract
from PIL import Image
import cv2
import nltk
import pickle
from text_similarity_calculator import SimilarityCalculator_W2V
from os.path import exists

# requires installation of pytesseract for OCR
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# nltk.download('words')

def warn(*args, **kwargs): # hides sklearn warnings
    pass
import warnings
warnings.warn = warn


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



class MLP_ScreenClassifierForAUT(object):
    def __init__(self, autoencoder=False, path=None):
        if path is not None:
            self.load(path)
        else:
            self.clas = prepare_clas()
            self.autoencoder = autoencoder
            # self.similarity_calculator = SimilarityCalculator()

    def learn(self, app_name=None):
        training_set = None
        # validation_set = None
        input_size = None

        if self.autoencoder:
            input_size = 4608
            current_dir_path = os.path.dirname(os.path.realpath(__file__))
            autoencoder_embedding_dir = os.path.join(current_dir_path, '..', 'autoencoder_KNN', 'autoencoder_embeddings')
            if app_name is not None:
                training_set = prepare_autoencoder_data_for_AUT(
                    os.path.join(autoencoder_embedding_dir, 'AllEmbeddingsOld'),
                    os.path.join(autoencoder_embedding_dir, 'AllEmbeddings_augmented'),
                    os.path.join(autoencoder_embedding_dir, '..', 'final_labels_all.csv'),
                    os.path.join(autoencoder_embedding_dir, '..', 'augmented_labels.csv'),
                    app_name, remove_wrong_dimensions=False)
            else:
                print('AUT is None...')

        else:
            print('autoencoder is set False...')

        X_train = np.empty((0, input_size), np.float32)
        for row in training_set.embedding:
            # print(row.shape)
            row = row.reshape(1, row.shape[0])
            X_train = np.append(X_train, row, axis=0)

        # get path and labels
        values = training_set.iloc[:, -1].values
        Y_train = np.array([v[0] for v in values])
        # X_train_paths = [v[1] for v in values]

        #train
        self.clas.fit(X_train, Y_train)
        self.classes = self.clas.classes_
        print("Training size for AUT", app_name, len(Y_train))
        with open(app_name + '_trained_MLP.pickle', 'wb') as file:
            pickle.dump(self.clas, file)
            print('saved MLP model to', app_name + '_trained_MLP.pickle')


    # embedding is (1, 4608)
    def classify(self, embedding_to_predict, AUT, N):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        trained_model_path = os.path.join(current_dir_path, AUT + '_trained_MLP.pickle')
        # input_size = 4608
        self.clas = pickle.load(open(trained_model_path, 'rb'))
        self.classes = self.clas.classes_

        # classify
        y_pred = self.clas.predict(embedding_to_predict)
        y_pred_proba = self.clas.predict_proba(embedding_to_predict)

        prob_sort = np.argsort(y_pred_proba, 1)

        top_k_classification = prob_sort[:, -N:]

        top_n_labels = self.classes[top_k_classification]
        # print('top n labels', top_n_labels)
        return str(y_pred[0]), list(top_n_labels[0])

    def classify_allapp_as_training(self, embedding_to_predict, N):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        trained_model_path = os.path.join(current_dir_path, 'allapps_trained_MLP.pickle')
        # input_size = 4608
        self.clas = pickle.load(open(trained_model_path, 'rb'))
        self.classes = self.clas.classes_

        # classify
        y_pred = self.clas.predict(embedding_to_predict)
        y_pred_proba = self.clas.predict_proba(embedding_to_predict)

        prob_sort = np.argsort(y_pred_proba, 1)

        top_k_classification = prob_sort[:, -N:]

        top_n_labels = self.classes[top_k_classification]
        # print('top n labels', top_n_labels)
        return str(y_pred[0]), list(top_n_labels[0])

    # train the model on the fly with only the states in the usage model
    def train_and_classify_for_states(self, app_name, embedding_to_predict, N, states):
        training_set = None
        input_size = None

        if self.autoencoder:
            input_size = 4608
            current_dir_path = os.path.dirname(os.path.realpath(__file__))
            autoencoder_embedding_dir = os.path.join(current_dir_path, '..', 'autoencoder_KNN',
                                                     'autoencoder_embeddings')
            if app_name is not None:
                training_set = prepare_autoencoder_data_for_states(
                    os.path.join(autoencoder_embedding_dir, 'AllEmbeddingsOld'),
                    os.path.join(autoencoder_embedding_dir, 'AllEmbeddings_augmented'),
                    os.path.join(autoencoder_embedding_dir, '..', 'final_labels_all.csv'),
                    os.path.join(autoencoder_embedding_dir, '..', 'augmented_labels.csv'),
                    app_name, states, remove_wrong_dimensions=False)
            else:
                print('AUT is None...')

        else:
            print('autoencoder is set False...')

        X_train = np.empty((0, input_size), np.float32)
        for row in training_set.embedding:
            row = row.reshape(1, row.shape[0])
            X_train = np.append(X_train, row, axis=0)

        # get path and labels
        values = training_set.iloc[:, -1].values
        Y_train = np.array([v[0] for v in values])
        # X_train_paths = [v[1] for v in values]

        # train
        self.clas.fit(X_train, Y_train)
        self.classes = self.clas.classes_
        print("Training size for usage states:", len(Y_train))

        # classify
        y_pred = self.clas.predict(embedding_to_predict)
        y_pred_proba = self.clas.predict_proba(embedding_to_predict)

        prob_sort = np.argsort(y_pred_proba, 1)

        top_n_classification = prob_sort[:, -N:]

        top_n_labels = self.classes[top_n_classification]
        return str(y_pred[0]), list(top_n_labels[0])

if __name__ == "__main__":

    screen_classifier_autoencoder = MLP_ScreenClassifierForAUT(autoencoder=True)
    print("Training with autoencoder:")

    screen_classifier_autoencoder.learn('ebay')
    screen_classifier_autoencoder.learn('geek')
    screen_classifier_autoencoder.learn('groupon')
    screen_classifier_autoencoder.learn('wish')
    screen_classifier_autoencoder.learn('zappos')

    # screen_classifier_autoencoder.learn('cbs')
    # screen_classifier_autoencoder.learn('dailyhunt')
    # screen_classifier_autoencoder.learn('fox')
    # screen_classifier_autoencoder.learn('newsbreak')
    # screen_classifier_autoencoder.learn('reuters')
    # screen_classifier_autoencoder.learn('guardian')
    # screen_classifier_autoencoder.learn('usatoday')

    # print('Predicting with autoencoder')
    # embedding_to_predict = torch.load('test_dynamic_embedding', map_location='cpu') # read from autoencoder embedding obtained from dynamic phase
    # top_1, top_n = screen_classifier_autoencoder.classify(embedding_to_predict, 'etsy', 5)
    # print(top_1, top_n)
    print('all done! :)')
