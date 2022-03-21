import os, glob
import shutil
import pandas as pd
import pickle
import json
import sys
sys.path.insert(0, '/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/code/3_model_generation')

def delete_subdir(usage_root_dir, dirname):
    dir_path = os.path.join(usage_root_dir, '*', dirname)
    dir_list = glob.glob(dir_path)
    for dir in dir_list:
        print(dir)
        # shutil.rmtree(dir) # delete directory
        os.remove(dir) # delete a file

def rename_file(dir):
    for src in glob.glob(dir + '/*'):
        dst = src + '_2'
        os.rename(src, dst)

def check_widget_exist(usage_root_dir):
    for screen in glob.glob(usage_root_dir + '/*/ir_data_auto/*-screen.jpg'):
        widget = screen.replace('screen', 'widget')
        if not os.path.isfile(widget):
            print('not exist', widget)

def merge_csvs():
    df = pd.concat(map(pd.read_csv, [
        '/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/15-Filter/typing_result.csv',
        '/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/15-Filter-Summer/typing_result.csv']),
                   ignore_index=True)
    df.to_csv('/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/15-Filter/typing_result.csv')

def rename_files():
    for file in glob.glob('/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/15-Filter-Summer/*/ir_data_auto/*.jpg'):
        filename = os.path.basename(file)
        prefix = filename.split('bbox')[0]
        new_filename = filename.replace(prefix, prefix + 's-')
        full_new_file = file.replace(filename, new_filename)
        # print('old file', file)
        # print('new file', full_new_file)
        os.rename(file, full_new_file)

def rename_screenIR():
    oldIR = 'sign_in_or_sign_up'
    newIR = 'signin_or_signup'
    for file in glob.glob('/Users/XXX/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/*/LS-annotations.csv'):
        print('processing', file)
        df = pd.read_csv(file)
        df['tag_screen'] = df['tag_screen'].replace(oldIR, newIR)
        # print(df['tag_screen'])
        df.to_csv(file, index=False)

def find_IRs():
    IR = 'keep_signin'
    column = 'tag_screen'
    for file in glob.glob('/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/*/LS-annotations.csv'):
        df = pd.read_csv(file)
        rows = df.loc[df[column] == IR]
        if len(rows) != 0:
            print(file)

def rename_widgetIR():
    oldIR = 'get_started'
    newIR = 'continue'
    for file in glob.glob('/Users/XXX/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/*/LS-annotations.csv'):
        print('processing', file)
        df = pd.read_csv(file)
        df['tag_widget'] = df['tag_widget'].replace(oldIR, newIR)
        # print(df['tag_screen'])
        df.to_csv(file, index=False)

def merge_label_files():
    big_file = '/Users/XXX/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/1-SignIn/LS-annotations.csv'
    small_file = '/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/LS-annotations.csv'
    big_df = pd.read_csv(big_file)
    small_df = pd.read_csv(small_file)
    merged_df = big_df.loc[~big_df['screen'].isin(small_df['screen'])]
    merged_df = pd.concat([merged_df, small_df])
    merged_df.to_csv(big_file, index=False)

def merge_filter_labels():
    big_file = '/Users/XXX/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/15-Filter/LS-annotations.csv'
    small_file = '/Users/XXX/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/15-Filter/filter-summer-annotations.csv'
    big_df = pd.read_csv(big_file)
    small_df = pd.read_csv(small_file)
    merged_df = big_df.loc[~big_df['screen'].str.contains('-s-bbox')]
    merged_df = pd.concat([merged_df, small_df])
    merged_df.to_csv(big_file, index=False)

def check_nan_state():
    # usatoday-about-2.png has nan state, check it!
    # count = 0
    for ir_model_file in glob.glob('/Users/XXX/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts/*/*/ir_model.pickle'):
        if not os.path.exists(ir_model_file):
            print('ir model non exist in', ir_model_file)
        else:
            ir_model = pickle.load(open(ir_model_file, 'rb'))
            for state in ir_model.states:
                if pd.isna(state):
                    print('nan state in', ir_model_file)
                    # os.remove(ir_model_file)
                    # count += 1
    # print('removed', count)

def count_screen_images():
    root_usage = '/Users/XXX/Documents/Research/UsageTesting/v2s_data/UsageTesting-Artifacts'
    all_labels = pd.read_csv('/Users/XXX/Documents/Research/UsageTesting/v2s_data/final_labels/all.csv')

    screen_list = []
    for screen_file in glob.glob(os.path.join(root_usage, '*/*/ir_data_auto/*-screen.jpg')):
        screen_list.append(os.path.basename(os.path.normpath(screen_file)))

def count_REMAUI_output():
    root_dir = '/Users/XXX/Documents/Research/UsageTesting/REMAUIOutput'
    REMAUI_file_list = []
    autoencoder_file_list = []
    for file in glob.glob(root_dir + '/*/*/*-screen/activity_main.xml'):
        tmp = os.path.split(os.path.split(file)[0])[1]
        # print(tmp)
        REMAUI_file_list.append(tmp)
    autoencoder_file = open('/Users/XXX/Documents/Research/UsageTesting/KNNscreenClassifier/names.json')
    names_json = json.load(autoencoder_file)
    for name in names_json:
        tmp = os.path.basename(os.path.normpath(name)).replace('.jpg', '')
        # print(tmp)
        autoencoder_file_list.append(tmp)

    diff = set(REMAUI_file_list) - set(autoencoder_file_list)
    print('diff =', diff)
    print('diff len =', len(diff))


def combine_LS_labels():
    label_root = '/Users/XXX/Documents/Research/UsageTesting/v2s_data/final_labels'
    merged_df = None
    columns = None
    for label_file in glob.glob(label_root +'/*.csv'):
        df = pd.read_csv(label_file)
        if merged_df is None:
            merged_df = df
            columns = df.columns
        else:
            merged_df = pd.concat([merged_df, df[columns]], axis=0)
    # merged_df.to_csv(label_root + '/all.csv', index=False)

if __name__ == '__main__':
    delete_subdir('/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/usage_data', '*/ir_model.pickle')
    print('all done! :)')