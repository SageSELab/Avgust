from general_KNN_updated import GeneralKNNClassifier
import os
import torch
import numpy as np
import json

def get_app_names(embeddings_directory):
    app_names = []
    with open(os.path.join(embeddings_directory, "AllNamesOld.json")) as name_old_file:
        names_old_str = name_old_file.read()
        names_old = names_old_str.split(",")
        for name in names_old:
            name = name.split("/")[-1].split(".")[0]
            app_name = name.split("-")[0].lower()
            if app_name not in app_names:
                app_names.append(app_name)

    with open(os.path.join(embeddings_directory, "AllNames_augmented.json")) as name_augmented_file:
        names_augmented_str = name_augmented_file.read()
        names_augmented = names_augmented_str.split(",")
        for name in names_augmented:
            name = name.split("/")[-1][:-19]
            app_name = name.split("-")[0].lower()
            if app_name not in app_names:
                app_names.append(app_name)

    print(app_names)
    return app_names


class KNN_screen_classifier:
    def __init__(self, query_app, embeddings_path, labels_path, k, n_accuracy):
        self.query_app = query_app
        self.embeddings_path = embeddings_path
        self.train_test_split_dict = self.generate_train_test_data()
        self.train_embeddings, self.train_id_dict, self.test_embeddings, self.test_id_dict = self.read_data()
        self.classifier = GeneralKNNClassifier(self.train_embeddings, self.train_id_dict, labels_path, k, n_accuracy)

    def read_data(self):
        embeddings_old = torch.load(os.path.join(self.embeddings_path, "AllEmbeddingsOld"), map_location='cpu')
        embeddings_augmented = torch.load(os.path.join(self.embeddings_path, "AllEmbeddings_augmented"), map_location='cpu')
        all_embeddings = np.concatenate((embeddings_old, embeddings_augmented), axis=0)
        embedding_id_dict = {}
        idx = 0
        with open(os.path.join(self.embeddings_path, "AllNamesOld.json")) as name_old_file:
            names_old_str = name_old_file.read()
            names_old = names_old_str.split(",")
            for name in names_old:
                name = name.split("/")[-1].split(".")[0]
                embedding_id_dict[idx] = name
                idx += 1
        with open(os.path.join(self.embeddings_path, "AllNames_augmented.json")) as name_augmented_file:
            names_augmented_str = name_augmented_file.read()
            names_augmented = names_augmented_str.split(",")
            for name in names_augmented:
                name = name.split("/")[-1][:-19]
                embedding_id_dict[idx] = name
                idx += 1

        all_training_embeddings_lst = []
        all_testing_embeddings_lst = []
        training_idx = 0
        testing_idx = 0
        training_id_dict = {}
        testing_id_dict = {}
        for i in range(idx):
            if self.train_test_split_dict[i] == "train":
                all_training_embeddings_lst.append(all_embeddings[i])
                training_id_dict[training_idx] = embedding_id_dict[i]
                training_idx += 1
            else:
                all_testing_embeddings_lst.append(all_embeddings[i])
                testing_id_dict[testing_idx] = embedding_id_dict[i]
                testing_idx += 1

        all_training_embeddings_mat = np.vstack(all_training_embeddings_lst)
        all_testing_embeddings_mat = np.vstack(all_testing_embeddings_lst)

        return all_training_embeddings_mat, training_id_dict, all_testing_embeddings_mat, testing_id_dict

    def generate_train_test_data(self):
        train_test_split_dict = {}
        idx = 0
        with open(os.path.join(self.embeddings_path, "AllNamesOld.json")) as name_old_file:
            names_old_str = name_old_file.read()
            names_old = names_old_str.split(",")
            for name in names_old:
                name = name.split("/")[-1].split(".")[0]
                app_name = name.split("-")[0]
                if app_name == self.query_app:
                    train_test_split_dict[idx] = "test"
                else:
                    train_test_split_dict[idx] = "train"
                idx += 1

        with open(os.path.join(self.embeddings_path, "AllNames_augmented.json")) as name_augmented_file:
            names_augmented_str = name_augmented_file.read()
            names_augmented = names_augmented_str.split(",")
            for name in names_augmented:
                name = name.split("/")[-1][:-19]
                app_name = name.split("-")[0]
                if app_name == self.query_app:
                    train_test_split_dict[idx] = "test"
                else:
                    train_test_split_dict[idx] = "train"
                idx += 1

        return train_test_split_dict

    def run_all_queries_and_get_percision(self):
        correct_cntr = 0
        correct_top_n_cntr = 0
        all_cntr = 0
        self.test_embeddings
        self.test_id_dict
        for i in range(len(self.test_id_dict.keys())):
            try:
                prediction, gt, top_n = self.classifier.run_knn_query(self.test_embeddings[i], self.test_id_dict[i])
                all_cntr += 1
                if prediction == gt:
                    correct_cntr += 1
                if gt in top_n:
                    correct_top_n_cntr += 1
            except:
                pass
        return correct_cntr/all_cntr, correct_top_n_cntr/all_cntr

    def run_knn_query(self, query_embedding):
        prediction, top_n = self.classifier.run_dynamic_knn_query(query_embedding)
        return prediction, top_n

    def run_knn_query_states(self, query_embedding, states):
        prediction, top_n = self.classifier.run_dynamic_knn_query_states(query_embedding, states)
        return prediction, top_n

if __name__ == "__main__":
    # get directory of this file
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    embeddings_path = os.path.join(current_dir_path, "autoencoder_embeddings")
    app_names = get_app_names(embeddings_path)
    k = 5
    n = 5
    labels_path = ["final_labels_all.csv", "augmented_labels.csv"]
    screen_classifier = KNN_screen_classifier('etsy', embeddings_path, labels_path, k, n)
    KNN_screen_classifier.run_knn_query()
    # precisions_sum = 0
    # top_n_percision_sum = 0
    # for app in app_names:
    #     screen_classifier = KNN_screen_classifier(app, embeddings_path, labels_path, k, n)
    #     precision, top_n_precision = screen_classifier.run_all_queries_and_get_percision()
    #     print(app + ": " + str(precision))
    #     print(app + " top-5 :" + str(top_n_precision))
    #     print("---------------")
    #     precisions_sum += precision
    #     top_n_percision_sum += top_n_precision
    # print("average precisions:" + str(precisions_sum/len(app_names)))
    # print("average top-n precisions:" + str(top_n_percision_sum/len(app_names)))