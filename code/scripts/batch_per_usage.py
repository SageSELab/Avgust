import sys
sys.path.insert(0, '/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/code/1_step_extraction')
sys.path.insert(0, '/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/code/2_ir_classification')
sys.path.insert(0, '/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/code/binaryClassifier')

from step_extraction import generate_clicked_frame
from step_cleaning import copy_useful_steps
from special_step_recognition import add_special_action
from crop_clicked_frames import generate_clicked_frame_crop
from create_symlink import create_sym_keyboard_crops
from labelPredictor import generate_typing_results
from typingLocator import update_typing_results
from screen_widget_extraction import screen_extraction_auto, widget_extraction_auto


usage_root_dir_list = [
    '/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/12-AddCart'
    # '/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/13-RemoveCart',
    # '/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/14-Address',
    # '/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/15-Filter'
]

def first_auto_batch(usage_root_dir_list):
    for usage_root_dir in usage_root_dir_list:
        generate_clicked_frame(usage_root_dir, 0)
        generate_clicked_frame_crop(usage_root_dir)
        create_sym_keyboard_crops(usage_root_dir)
        generate_typing_results(usage_root_dir)
        update_typing_results(usage_root_dir)
        copy_useful_steps(usage_root_dir)

def second_auto_batch(usage_root_dir_list):
    for usage_root_dir in usage_root_dir_list:
        add_special_action(usage_root_dir)
        screen_extraction_auto(usage_root_dir)

def third_auto_batch(usage_root_dir_list):
    for usage_root_dir in usage_root_dir_list:
        widget_extraction_auto(usage_root_dir)

if __name__ == '__main__':
    option = input('enter 1 or 2 or 3 to run corresponding auto pipeline...\n')
    if option == '1':
        first_auto_batch(usage_root_dir_list)
        print('first automation all done! :) check steps clean folder now...')
    elif option == '2':
        second_auto_batch(usage_root_dir_list)
        print('second automation all done! :) run UIED now...')
    elif option == '3':
        third_auto_batch(usage_root_dir_list)
        print('third automation all done! :) you can check if each screen has a matching widget in util_func.py')

