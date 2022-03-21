import csv
import pandas as pd
import numpy as np
import sys
import os
import torch
from string import digits
import re
import xml.etree.ElementTree as ET


def get_app_names(embeddings_directory):
    app_names = []
    for embedding_file in os.listdir(embeddings_directory):
        app_name = embedding_file.split("-")[0]
        if app_name not in app_names:
            app_names.append(app_name)



def prepare_app_fold_data(embeddings_directory, labels_filename, test_app):
    counter = 0
    counter2 = 0
    df = pd.read_csv(labels_filename, usecols=['widget', 'tag_widget'])
    df.widget = (df.widget.str.rsplit("/", n=1, expand=True)[1])
    df.widget = (df.widget.str.rsplit(".", n=1, expand=True)[0])
    label_dict = dict(zip(df.widget, df.tag_widget))
    point_label_df_train = pd.DataFrame(columns=['embedding', 'label'])
    point_label_df_test = pd.DataFrame(columns=['embedding', 'label'])
    for embedding_file in os.listdir(embeddings_directory):
        counter = counter+1
        embedding = torch.load(embeddings_directory + "/" + embedding_file, map_location='cpu').detach()
        np_embedding = embedding.numpy()
        # print("np_embedding")
        # print(np_embedding.shape)
        app_name = embedding_file.split("-")[0]
        file_name = embedding_file.replace("_", "-")
        mo = re.match('.+([0-9])[^0-9]*$', file_name)
        file_name = file_name[0:mo.start(1) + 1]
        file_name = file_name+"-widget"
        if file_name in label_dict.keys():
            label = label_dict[file_name]
            if type(label) == float:
                continue
            if app_name == test_app:
                point_label_df_test = point_label_df_test.append({'embedding': np_embedding, 'label': label}, ignore_index=True)
            else:
                point_label_df_train = point_label_df_train.append({'embedding': np_embedding, 'label': label}, ignore_index=True)
            counter2 = counter2 + 1
    return point_label_df_train, point_label_df_test

def prepare_data(embeddings_directory, labels_filename):
    counter = 0
    counter2 = 0
    df = pd.read_csv(labels_filename, usecols=['widget', 'tag_widget'])
    df.widget = (df.widget.str.rsplit("/", n=1, expand=True)[1])
    df.widget = (df.widget.str.rsplit(".", n=1, expand=True)[0])
    label_dict = dict(zip(df.widget, df.tag_widget))
    # print(label_dict)
    embedding_dict = {}
    point_label_df = pd.DataFrame(columns=['embedding', 'label'])
    # embeddings_directory = "categoris_screen2vec_embeddings"
    for embedding_file in os.listdir(embeddings_directory):
        counter = counter+1
        embedding = torch.load(embeddings_directory + "/" + embedding_file, map_location='cpu').detach()
        np_embedding = embedding.numpy()
        # print("np_embedding")
        # print(np_embedding.shape)
        file_name = embedding_file.replace("_", "-")
        mo = re.match('.+([0-9])[^0-9]*$', file_name)
        file_name = file_name[0:mo.start(1) + 1]
        file_name = file_name+"-widget"
        if file_name in label_dict.keys():
            label = label_dict[file_name]
            if type(label) == float:
                continue
            embedding_dict[file_name] = embedding
            point_label_df = point_label_df.append({'embedding': np_embedding, 'label': label}, ignore_index=True)
            counter2 = counter2 + 1


    print("c1")
    print(counter)
    print("c2")
    print(counter2)
    return point_label_df


def make_bert_data_frame(remaui_output_dir_path):
    for usage in os.listdir(remaui_output_dir_path):
        for trace in os.listdir(os.path.join(remaui_output_dir_path, usage)):
            if os.path.isdir(os.path.join(remaui_output_dir_path, usage, trace)):
                print("---------trace started------------")
                for screen in os.listdir(os.path.join(remaui_output_dir_path, usage, trace)):
                    print(screen)
                    output_path = trace + "_" + screen
                    get_ocr_results(os.path.join(remaui_output_dir_path, usage, trace, screen), output_path)


def get_ocr_results(path,output_path):
    with open(os.path.join(path,"out.hocr")) as ocr_file:
        data = ocr_file.read()
        root = ET.fromstring(data)
        text = ''.join(root.itertext())
        print(text)
        print("-------------")


# make_bert_data_frame("REMAUI_outputs")



# def prepare_data_for_bert(remaui_embedding_folder):
