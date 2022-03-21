''' This function outputs whether the touch indicator falls onto the keyboard or not '''

import os
import pandas as pd
import json
import shutil


# add results to new column 'touch_location': the results are either 'onKeyboard' or 'out'
def find_touch_location(row, usage_root_dir):
    KEYBOARD_Y = 1110  # threashold for the keyboard region. Y coordinate where keyboard starts when Y >= KEYBOARD_Y
    split_word = '-clicked_frames_crop/bbox-'
    app_dir = str(row['filename']).split(split_word)[0]
    frame_id = int(str(row['filename']).split(split_word)[1].replace('.jpg', ''))
    # print(app_dir, frame_id)
    Y_cor = get_touch_Y(app_dir, frame_id, usage_root_dir)
    if Y_cor is None:
        print('frame NOT FOUND! check: ', row['filename'])
    elif Y_cor >= KEYBOARD_Y:
        return 'onKeyboard'
    return 'out'

def get_touch_Y(app_dir, frame_id, usage_root_dir):
    frame_index = 0  # Index of the frame list. keep it consistent with the value in the step_extraction.py
    action_file = open(os.path.join(usage_root_dir, app_dir, 'detected_actions.json'), 'r')
    action_array = json.load(action_file)
    for action in action_array:
        # print(frame_id, action['taps'][frame_index]['frame'])
        if frame_id == action['taps'][frame_index]['frame']:
            return action['taps'][frame_index]['y']
    return None

def update_typing_results(usage_root_dir):
    usage_name = os.path.basename(os.path.normpath(usage_root_dir))
    typing_result_file = os.path.abspath(
        'sym_'+ usage_name +'/typing_result.csv')  # output file to append 'touch_location' results
    df_typing_result = pd.read_csv(typing_result_file)
    df_typing_result['touch_location'] = df_typing_result.apply(lambda row: find_touch_location(row, usage_root_dir), axis = 1) # apply find_touch_location function to each row
    df_typing_result.to_csv(typing_result_file)
    shutil.copy(typing_result_file, usage_root_dir+'/.')
    print('update typing results all done! :)')

if __name__ == '__main__':
    usage_root_dir = '/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/10-Contact'
    update_typing_results(usage_root_dir)
