import os
import glob

''' 
this script creates symlinks in order to work with 
Label Studio's data import script 
'''

usage_root_dir = os.path.abspath('../../video_data_examples') # change this
include_folder = 'ir_data_auto'

sym_root_dir = 'sym_' + os.path.basename(usage_root_dir)

if not os.path.exists(sym_root_dir):
    os.mkdir(sym_root_dir)

for src_file in glob.glob(usage_root_dir + '/*/' + include_folder + '/*'):
    # print(os.path.basename(src_file))
    dst_file = os.path.join(sym_root_dir, os.path.basename(src_file))
    os.symlink(src_file, dst_file)
    print('create symlink', src_file, dst_file)

print('all done! :)')