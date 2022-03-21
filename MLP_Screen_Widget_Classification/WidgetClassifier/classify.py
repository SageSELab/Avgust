from sklearn.neural_network import MLPClassifier
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import multiprocessing
import glob
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from data_reader import prepare_data
from data_reader import prepare_app_fold_data
from sklearn.metrics import confusion_matrix
from sklearn.utils import shuffle
from sklearn.model_selection import GridSearchCV
from sklearn import preprocessing
import shutil

random_state = 0
use_rep = False
use_pca = False
n_components = 1000
use_titleinfo = True
use_scaler = False
parameter_space = {
    'hidden_layer_sizes': [(50,), (100,), (40,), (5,)],
    'activation': ['tanh', 'relu'],
    'solver': ['sgd', 'adam'],
    'alpha': [0.0001, 0.05],
    'learning_rate': ['constant', 'adaptive'],
}

thread_count = 1

if use_rep:
    REP_COUNT = {'signin': 5, 'register': 5, 'main': 1, 'checkout': 1, 'addredit': 5,
                 'cardedit': 5, 'filter': 2, 'sort': 2, 'account': 5, 'setting': 5,
                 'address': 3, 'payment': 3, 'search': 5, 'cart': 1, 'detail': 1,
                 'searchret': 1, 'menu': 3, 'cat': 5, 'welcome': 5, 'orders': 5,
                 'about': 5, 'terms': 5, 'help': 5, 'notif': 5, 'contact': 5}
else:
    REP_COUNT = {}


def prepare_clas():
    clas = MLPClassifier(hidden_layer_sizes=(40,), max_iter=10000,
                         early_stopping=False, verbose=False,
                         solver='adam', activation='relu', n_iter_no_change=50)
    return clas




def accuracy(confusion_matrix):
    diagonal_sum = confusion_matrix.trace()
    sum_of_all_elements = confusion_matrix.sum()
    return diagonal_sum / sum_of_all_elements


class ScreenClassifier(object):
    def __init__(self, path=None):
        if path is not None:
            self.load(path)
        else:
            self.clas = prepare_clas()
            self.pca = None

    def learn(self, app_name):
        print(app_name)
        # (datapts, _, _, _) = load_datapts(datadir, appname, extrapath, extrascr)
        # train_lbls = list(map(lambda x: x['tag'], datapts))
        # (train_keys, mydict, self.tree_vec, self.act_vec, self.img_vec, self.title_vec,
        #  self.scaler) = vectorize_train(datapts)

        # if use_pca:
        #     self.pca = PCA(n_components=n_components)
        #     train_keys = self.pca.fit_transform(train_keys)

        # data = prepare_data("signup_screen2vec_embeddings", "SignUp/LS-annotations.csv")
        # data = prepare_data("widget_embeddings", "comp-LS-annotations.csv")

        training_set, validation_set = prepare_app_fold_data("widget_embeddings", "comp-LS-annotations.csv", app_name)

        # class_count = data.groupby('label').count()
        # print(class_count)
        # small_data = data.groupby(['label']).filter(lambda x: len(x) >= 10)

        # print(data.shape)
        # print(small_data.shape)

        # training_set, validation_set = train_test_split(data, test_size=0.2)
        # training_set, validation_set = train_test_split(data, test_size=0.2, shuffle=True)

        # print(training_set.shape)
        # print(validation_set.shape)

        X_train = np.empty((0, 768), np.float32)
        for row in training_set.embedding:
            X_train = np.append(X_train, row, axis=0)
        Y_train = training_set.iloc[:, -1].values

        X_val = np.empty((0, 768), float)
        for row in validation_set.embedding:
            X_val = np.append(X_val, row, axis=0)
        y_val = validation_set.iloc[:, -1].values

        # opt_cls = GridSearchCV(self.clas, parameter_space, n_jobs=-1, cv=3)

        self.clas.fit(X_train, Y_train)
        self.classes = self.clas.classes_
        # print(self.classes)

        y_pred = self.clas.predict(X_val)
        #y_prob_pred = self.clas.predict_log_proba(X_val) (This is for getting the probability of each class.)

        #print(y_val)

        # for i in range(170):
        #     print("---------")
        #     print(y_val[i])
        #     print(y_pred[i])
        #     print(y_prob_pred[i])
        #     print(self.classes)

        cm = confusion_matrix(y_pred, y_val)

        print("Accuracy of MLPClassifier : ", accuracy(cm))
        print("---------------------------")


def get_app_names(embeddings_directory):
    app_names = []
    for embedding_file in os.listdir(embeddings_directory):
        app_name = embedding_file.split("-")[0]
        app_name = app_name.lower()
        if app_name not in app_names:
            app_names.append(app_name)
    return app_names


def get_usage_names(embedding_directory):
    usage_names = []
    for embedding_file in os.listdir(embedding_directory):
        usage_name = embedding_file.split("-")[1]
        usage_name = usage_name.lower()
        if usage_name not in usage_names:
            usage_names.append(usage_name)
    return usage_names


def filter_data_based_on_usage(embedding_directory, dest_dir):
    usage_names = get_usage_names(embedding_directory)
    # for usage in usage_names:
        # os.mkdir(os.path.join(dest_dir,usage))
    for embedding_file in os.listdir(embedding_directory):
        usage_name = embedding_file.split("-")[1]
        shutil.copy(os.path.join(embedding_directory, embedding_file),os.path.join(dest_dir,usage_name))



if __name__ == "__main__":
    app_names = get_app_names("widget_embeddings")
    for app in app_names:
        screen_classifier = ScreenClassifier()
        screen_classifier.learn(app)
