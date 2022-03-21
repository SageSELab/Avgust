import pandas as pd
import numpy as np
import os
import torch
import re
import json

# fine path of image
def get_image_path(filename):
    root_path = r'C:\Users\HyoJP\Desktop\UsageTesting-Artifacts\\'
    info = filename.split('-')
    folder = None
    if info[1] == 'video':
        folder = info[2]
    else:
        folder = info[1]
    if not folder[-1].isalpha():
        folder = folder[:-1]
    if folder == "details":
        folder = "detail"

    stop_until = None
    for counter, word in enumerate(info):
        if word == 'bbox':
            stop_until = counter
    subfolder = ''
    for i in range(stop_until):
        subfolder += info[i] + '-'

    return root_path + folder + r'\\' + subfolder[:-1] + r'\\ir_data_auto\\' + filename + '-screen.jpg'


def prepare_app_fold_data(embeddings_directory, labels_filename, test_app, remove_wrong_dimensions=False):
    counter = 0
    counter2 = 0
    df = pd.read_csv(labels_filename, usecols=['screen', 'tag_screen'])
    df.screen = (df.screen.str.rsplit("/", n=1, expand=True)[1])
    df.screen = (df.screen.str.rsplit("-", n=1, expand=True)[0])
    label_dict = dict(zip(df.screen, df.tag_screen))
    point_label_df_train = pd.DataFrame(columns=['embedding', 'label'])
    point_label_df_test = pd.DataFrame(columns=['embedding', 'label'])

    wrong_dimensions_file = open('weird_dimensions.txt', 'r')
    wrong_dimensions_whole_txt = wrong_dimensions_file.read()
    wrong_file_names = []
    if remove_wrong_dimensions:
        for wrong_file_name in wrong_dimensions_whole_txt.split(' '):
            if len(wrong_file_name) > 0 and wrong_file_name[-1] == ":":
                wrong_file_names.append(wrong_file_name[:-12]) # remove "-screen.jpg:" from file name

    for embedding_file in os.listdir(embeddings_directory):
        try:
            counter = counter + 1
            embedding = torch.load(embeddings_directory + "/" + embedding_file, map_location='cpu')[1].detach()
            np_embedding = embedding.numpy()
            # print(np_embedding)
            app_name = embedding_file.split("-")[0].lower()
            file_name = embedding_file.replace("_", "-")
            # remove files with incorrect dimensions
            if file_name[:-10] in wrong_file_names: # remove "-embedding" from file name
                continue
            file_name = file_name.split(".")[0][:-7]  # remove -screen in the file name

            mo = re.match('.+([0-9])[^0-9]*$', file_name)
            file_name = file_name[0:mo.start(1) + 1]
            if file_name in label_dict.keys():
                label = label_dict[file_name]

                if type(label) == float:
                    continue
                if app_name == test_app:
                    point_label_df_test = point_label_df_test.append({'embedding': np_embedding, 'label_path': [label, get_image_path(file_name)]}, ignore_index=True)
                else:
                    point_label_df_train = point_label_df_train.append({'embedding': np_embedding, 'label_path': [label, get_image_path(file_name)]}, ignore_index=True)
            counter2 = counter2 + 1
        except:
            pass
    return point_label_df_train, point_label_df_test


def prepare_app_fold_autoencoder_data(embedding_file, labels_filename, test_app, remove_wrong_dimensions=False):
    counter = 0
    counter2 = 0
    df = pd.read_csv(labels_filename, usecols=['screen', 'tag_screen'])
    df.screen = (df.screen.str.rsplit("/", n=1, expand=True)[1])
    df.screen = (df.screen.str.rsplit("-", n=1, expand=True)[0])
    label_dict = dict(zip(df.screen, df.tag_screen))
    #print(list(label_dict.keys())[list(label_dict.values()).index('remove')]) # locate incorrect label "remove"
    point_label_df_train = pd.DataFrame(columns=['embedding', 'label'])
    point_label_df_test = pd.DataFrame(columns=['embedding', 'label'])

    np_embedding = torch.load(embedding_file, map_location='cpu')
    np_names = np.array(json.load(open(r"autoencoder_embeddings\names.json")))

    wrong_dimensions_file = open('weird_dimensions.txt', 'r')
    wrong_dimensions_whole_txt = wrong_dimensions_file.read()
    wrong_file_names = []
    if remove_wrong_dimensions:
        for wrong_file_name in wrong_dimensions_whole_txt.split(' '):
            if len(wrong_file_name) > 0 and wrong_file_name[-1] == ":":
                wrong_file_names.append(wrong_file_name[:-1])

    for i in range(len(np_embedding)):
        try:
            # remove files with incorrect dimensions
            file_name = np_names[i].split("/")[-1]
            if file_name in wrong_file_names:
                continue
            file_name = file_name.split(".")[0][:-7]  # remove -screen in the file name
            app_name = file_name.split('-')[0].lower()

            counter = counter + 1
            if file_name in label_dict.keys():
                counter2 = counter2 + 1
                label = label_dict[file_name]
                if type(label) == float:
                    continue
                if app_name == test_app:
                    point_label_df_test = point_label_df_test.append({'embedding': np_embedding[i], 'label_path': [label, get_image_path(file_name)]}, ignore_index=True)
                else:
                    point_label_df_train = point_label_df_train.append({'embedding': np_embedding[i], 'label_path': [label, get_image_path(file_name)]}, ignore_index=True)
            counter2 = counter2 + 1
        except:
            pass
    return point_label_df_train, point_label_df_test

def prepare_autoencoder_data(embedding_file, labels_filename, remove_wrong_dimensions=False):
    counter = 0
    counter2 = 0
    counter3 = 0
    df = pd.read_csv(labels_filename, usecols=['screen', 'tag_screen'])
    df.screen = (df.screen.str.rsplit("/", n=1, expand=True)[1])
    df.screen = (df.screen.str.rsplit("-", n=1, expand=True)[0])
    label_dict = dict(zip(df.screen, df.tag_screen))
    #print(label_dict)

    embedding_dict = {}
    point_label_df = pd.DataFrame(columns=['embedding', 'label'])

    np_embedding = torch.load(embedding_file, map_location='cpu')
    np_names = np.array(json.load(open(r"autoencoder_embeddings\names.json")))

    wrong_dimensions_file = open('weird_dimensions.txt', 'r')
    wrong_dimensions_whole_txt = wrong_dimensions_file.read()
    wrong_file_names = []
    if remove_wrong_dimensions:
        for wrong_file_name in wrong_dimensions_whole_txt.split(' '):
            if len(wrong_file_name) > 0 and wrong_file_name[-1] == ":":
                wrong_file_names.append(wrong_file_name[:-1])

    for i in range(len(np_embedding)):
        try:
            # remove files with incorrect dimensions
            file_name = np_names[i].split("/")[-1]
            if file_name in wrong_file_names:
                continue
            file_name = file_name.split(".")[0][:-7]  # remove -screen in the file name

            counter = counter+1
            if file_name in label_dict.keys():
                counter2 = counter2 + 1
                label = label_dict[file_name]
                if type(label) == float:
                    continue
                embedding_dict[file_name] = np_embedding[i]
                point_label_df = point_label_df.append({'embedding': np_embedding[i], 'label_path': [label, get_image_path(file_name)]}, ignore_index=True)
        except:
            pass
    return point_label_df


def prepare_data(embeddings_directory, labels_filename, remove_wrong_dimensions=False):
    counter = 0
    counter2 = 0
    df = pd.read_csv(labels_filename, usecols=['screen', 'tag_screen'])
    df.screen = (df.screen.str.rsplit("/", n=1, expand=True)[1])
    df.screen = (df.screen.str.rsplit("-", n=1, expand=True)[0])
    label_dict = dict(zip(df.screen, df.tag_screen))

    embedding_dict = {}
    point_label_df = pd.DataFrame(columns=['embedding', 'label'])
    # embeddings_directory = "categoris_screen2vec_embeddings"

    wrong_dimensions_file = open('weird_dimensions.txt', 'r')
    wrong_dimensions_whole_txt = wrong_dimensions_file.read()
    wrong_file_names = []
    if remove_wrong_dimensions:
        for wrong_file_name in wrong_dimensions_whole_txt.split(' '):
            if len(wrong_file_name) > 0 and wrong_file_name[-1] == ":":
                wrong_file_names.append(wrong_file_name[:-12])
    for embedding_file in os.listdir(embeddings_directory):
        try:
            counter = counter+1
            embedding = torch.load(embeddings_directory + "/" + embedding_file, map_location='cpu')[1].detach()
            np_embedding = embedding.numpy()
            # print("np_embedding")
            # print(np_embedding.shape)
            # print(np_embedding)
            file_name = embedding_file.replace("_", "-")
            if file_name[:-10] in wrong_file_names: # remove "-embedding" from file name
                continue
            file_name = file_name.split(".")[0][:-7]

            mo = re.match('.+([0-9])[^0-9]*$', file_name)
            file_name = file_name[0:mo.start(1) + 1]
            if file_name in label_dict.keys():
                label = label_dict[file_name]
                if type(label) == float:
                    continue
                embedding_dict[file_name] = embedding
                point_label_df = point_label_df.append({'embedding': np_embedding, 'label_path': [label, get_image_path(file_name)]}, ignore_index=True)
                counter2 = counter2 + 1
        except:
            pass
    return point_label_df