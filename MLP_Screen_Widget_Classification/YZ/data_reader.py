import pandas as pd
import numpy as np
import os
import torch
import re
import json

# file path of image
# filename example: 'zappos-filter-1-bbox-1140-screen.jpg' for old data
# filename example: 'zappos-state_spinner-3' for augmented data
def get_image_path(filename):
    usage_folder_map = {}
    usage_folder_map['signin'] = '1-SignIn'
    usage_folder_map['signup'] = '2-SignUp'
    usage_folder_map['category'] = '3-Category'
    usage_folder_map['search'] = '4-Search'
    usage_folder_map['terms'] = '5-Terms'
    usage_folder_map['account'] = '6-Account'
    usage_folder_map['detail'] = '7-Detail'
    usage_folder_map['menu'] = '8-Menu'
    usage_folder_map['about'] = '9-About'
    usage_folder_map['contact'] = '10-Contact'
    usage_folder_map['help'] = '11-Help'
    usage_folder_map['addcart'] = '12-AddCart'
    usage_folder_map['removecart'] = '13-RemoveCart'
    usage_folder_map['address'] = '14-Address'
    usage_folder_map['filter'] = '15-Filter'
    usage_folder_map['addbookmark'] = '16-AddBookmark'
    usage_folder_map['removebookmark'] = '17-RemoveBookmark'
    usage_folder_map['textsize'] = '18-Textsize'
    usage_root_dir = '/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/usage_data'
    augmented_data_dir = '/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/Screen_AugmentedTrainingData'

    if 'screen' in filename:
        info = filename.split('-')
        usage_name = None
        if info[1] == 'video':
            usage_name = info[2]
        else:
            usage_name = info[1]
        if not usage_name[-1].isalpha():
            usage_name = usage_name[:-1]
        if usage_name.lower() == "details":
            usage_name = "detail"
        if usage_name.lower() == "fontsize":
            usage_name = 'textsize'

        image_file_path = os.path.join(usage_root_dir,
                                       usage_folder_map[usage_name],
                                       filename.split('-bbox')[0],
                                       'ir_data_auto',
                                       filename)
        if not os.path.exists(image_file_path):
            print('filename:', filename)
            print('image path:', image_file_path)
            raise ValueError('image path not exist')
        return image_file_path
    else:
        image_file_path = os.path.join(augmented_data_dir, filename + '.png')
        if not os.path.exists(image_file_path):
            print('filename:', filename)
            print('image path:', image_file_path)
            raise ValueError('image path not exist')
        return image_file_path


def prepare_autoencoder_data_for_AUT(embedding_file, augmented_embedding_file, final_label_file, augmented_label_file, AUT, remove_wrong_dimensions=False):
    counter = 0
    counter2 = 0
    df1 = pd.read_csv(final_label_file, usecols=['screen', 'tag_screen'])
    df2 = pd.read_csv(augmented_label_file, usecols=['screen', 'tag_screen'])
    label_df = pd.concat([df1, df2], axis=0, ignore_index=True)
    for index in label_df.index:
        if 'http' in label_df.loc[index, 'screen']:
            label_df.loc[index, 'screen'] = label_df.loc[index, 'screen'].split('/')[-1]
    # df1.screen = (df1.screen.str.rsplit("/", n=1, expand=True)[1])
    # df1.screen = (df1.screen.str.rsplit("-", n=1, expand=True)[0])

    label_dict = dict(zip(label_df.screen, label_df.tag_screen))
    point_label_df_train = pd.DataFrame(columns=['embedding', 'label'])
    point_label_df_test = pd.DataFrame(columns=['embedding', 'label'])

    # np_embedding = torch.load(embedding_file, map_location='cpu')
    embeddings_old = torch.load(embedding_file, map_location='cpu')
    embeddings_augmented = torch.load(augmented_embedding_file, map_location='cpu')
    all_embeddings = np.concatenate((embeddings_old, embeddings_augmented), axis=0)

    # np_names = np.array(json.load(open(r"autoencoder_embeddings\names.json")))
    names = json.load(open(r"/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/embeddings/autoencoder/AllNamesOld.json"))
    names_augmented = json.load(open(r"/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/embeddings/autoencoder/AllNames_augmented.json"))
    names.extend(names_augmented)
    np_names = np.array(names)

    wrong_dimensions_file = open('weird_dimensions.txt', 'r')
    wrong_dimensions_whole_txt = wrong_dimensions_file.read()
    wrong_file_names = []
    if remove_wrong_dimensions:
        for wrong_file_name in wrong_dimensions_whole_txt.split(' '):
            if len(wrong_file_name) > 0 and wrong_file_name[-1] == ":":
                wrong_file_names.append(wrong_file_name[:-1])

    for i in range(len(all_embeddings)):
        try:
            # remove files with incorrect dimensions
            file_name = np_names[i].split("/")[-1]
            if remove_wrong_dimensions and file_name in wrong_file_names:
                continue
            if 'screen' in file_name:
                # file_name = file_name.split(".")[0][:-7]  # remove -screen in the file name
                pass
            elif 'activity_main' in file_name:
                file_name = file_name.replace('-activity_main.jpg', '')
            else:
                print('embedding name:', file_name)
                raise ValueError('embedding name does not contain screen or activity_main...')

            app_name = file_name.split('-')[0].lower()

            counter = counter + 1
            if file_name in label_dict.keys():
                counter2 = counter2 + 1
                label = label_dict[file_name]
                if type(label) == float:
                    raise TypeError('label is float')
                if app_name == AUT:
                    # point_label_df_test = point_label_df_test.append({'embedding': all_embeddings[i], 'label_path': [label, get_image_path(file_name)]}, ignore_index=True)
                    pass # no need for test set, as the autoencoder embedding will be fed on the fly (1 autoencoder embedding from dynamic XML)
                else:
                    point_label_df_train = point_label_df_train.append({'embedding': all_embeddings[i], 'label_path': [label, get_image_path(file_name)]}, ignore_index=True)
            counter2 = counter2 + 1
        except:
            pass
    return point_label_df_train