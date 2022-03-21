import sys
sys.path.insert(0, '../3_model_generation')

import glob, os
from ir_model_generation import run_ir_model_generation
from linear_model_generation import run_linear_model_generation
from usage_model_generation import run_usage_model_generation

def ir_model_batch():
    final_data_root = '/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/usage_data'
    for usage_dir in glob.glob(os.path.join(final_data_root, '*')):
        print(usage_dir)
        run_ir_model_generation(usage_dir)

def linear_ir_model_batch():
    final_data_root = '/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/usage_data'
    for usage_dir in glob.glob(os.path.join(final_data_root, '*')):
        print(usage_dir)
        run_linear_model_generation(usage_dir)

def usage_model_batch():
    final_data_root = '/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/usage_data'
    for usage_dir in glob.glob(os.path.join(final_data_root, '*')):
        print(usage_dir)
        run_usage_model_generation(usage_dir)


if __name__ == '__main__':
    # linear_ir_model_batch()
    usage_model_batch()
    # ir_model_batch()
    print('all done! :)')