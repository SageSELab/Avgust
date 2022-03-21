'''clean steps from the clicked_frames folder, to only output the useful steps into steps_clean folder
(e.g., omitting certain keyboard typing actions)'''

import os
import glob
import shutil
import pandas as pd



def is_useful(step_image_file, app_root_dir, usage_root_dir, df_typing_result):
    filename = os.path.dirname(app_root_dir).replace(usage_root_dir + '/', '') \
               + '-clicked_frames_crop/' + os.path.basename(step_image_file)
    if len(df_typing_result.loc[df_typing_result['filename'] == filename]) == 0:
        return True
    else:
        found_row = (df_typing_result.loc[df_typing_result['filename'] == filename]).iloc[0]
        if found_row['touch_location'] == 'out':
            # print(found_row['filename'])
            return True
    return False

# copy all the 'noTyping' steps from the clicked_frames folder
def copy_useful_steps(usage_root_dir):
    input_dir = 'clicked_frames'
    output_dir = 'steps_clean'
    typing_result_file = os.path.join(usage_root_dir, 'typing_result.csv')
    df_typing_result = pd.read_csv(typing_result_file)
    for step_dir in glob.glob(usage_root_dir + '/*/' + input_dir):
        # print(step_dir.replace(input_dir, output_dir))
        if not os.path.exists(step_dir.replace(input_dir, output_dir)):
            os.mkdir(step_dir.replace(input_dir, output_dir))
        app_root_dir = step_dir.replace(input_dir, '')
        for step_image_file in os.scandir(step_dir):
            # print(step_image_file.path) # full abs path
            if step_image_file.path.endswith('.jpg') and is_useful(step_image_file, app_root_dir, usage_root_dir, df_typing_result):
                src_file = step_image_file.path
                dst_dir = os.path.join(app_root_dir, output_dir)
                shutil.copy(src_file, dst_dir)

if __name__ == '__main__':
    usage_root_dir = os.path.abspath('/Users/XXX/Documents/Research/UsageTesting/v2s_data/Combined/10-Contact')
    copy_useful_steps(usage_root_dir)
    print('all done! :)')