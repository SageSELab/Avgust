import os, sys
import glob
import math
import copy
import pandas as pd
import json


current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir_path, '..'))
sys.path.insert(0, os.path.join(current_dir_path, '..', '3_model_generation'))
sys.path.insert(0, os.path.join(current_dir_path, '..', '4_dynamic_generation'))


from global_config import *

def count_file():
    count = 0
    for file in glob.glob(os.path.join(FINAL_ARTIFACT_ROOT_DIR, 'usage_data', '*', '*', 'ir_model.pickle')):
        print(file)
        count += 1
    print(count)

def count_label():
    df = pd.read_csv('/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/final_labels/final_labels_all.csv')
    widget_missing = df[pd.isna(df.tag_widget)].shape[0]
    screen_missing = df[pd.isna(df.tag_screen)].shape[0]
    total_row = df.shape[0]
    print('screen:', (total_row - screen_missing))
    print('widget', (total_row-widget_missing))

def count_usage_model():
    count = 0
    for file in glob.glob(os.path.join(FINAL_ARTIFACT_ROOT_DIR, 'output', 'models', '*', '*.pickle')):
        print(file)
        count += 1
    print(count)
    count = 0
    for file in glob.glob(os.path.join(FINAL_ARTIFACT_ROOT_DIR, 'output', 'models', '*', '*.png')):
        print(file)
        count += 1
    print(count)

def count_steps():
    count = 0
    for file in glob.glob(os.path.join(FINAL_ARTIFACT_ROOT_DIR, 'output', 'models', '*', 'dynamic_output_phase_2', '*', 'eval_results.json')):
        f = open(file)
        data = json.load(f)
        count += len(data)
        count -= 2
    print(count)


if __name__ == '__main__':
    count_steps()
    print('all done! :)')