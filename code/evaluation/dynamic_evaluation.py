import sys, time

import PIL, json
import psutil as psutil
import os, shutil

current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir_path, '..'))
sys.path.insert(0, os.path.join(current_dir_path, '..', '4_dynamic_generation'))

from global_config import *
from App_Config import *
from test_generator_auto import *


def evaluation_with_true_label(AUT, usage_name):

    start = time.time()
    test_gen = TestGenerator(AUT.desiredCapabilities, REMAUI_flag=False, eval_flag=True, use_TRUE_label_flag=True)

    final_data_root = FINAL_ARTIFACT_ROOT_DIR

    usage_model_path = os.path.join(final_data_root, 'output', 'models', usage_name,
                                    'usage_model-' + AUT.appname + '.pickle')

    # dynamic_output folder contains our output and will be generated automatically, no need to create an empty folder
    output_path = os.path.join(final_data_root, 'output', 'models', usage_name, 'dynamic_output')

    test_gen.start(output_path, usage_model_path, AUT.appname)

    end = time.time()

    test_gen.eval_results['usage_states'] = test_gen.usage_model.states
    test_gen.eval_results['true_label_time'] = (end - start)


    with open(os.path.join(output_path, AUT.appname, 'eval_results.json'), 'w+') as outfile:
        json.dump(test_gen.eval_results, outfile)

    print("Dynamic generation running time " + str(end - start) + " seconds")

    # kill all the images opened by Preview
    for proc in psutil.process_iter():
        # print(proc.name())
        if proc.name() == 'Preview':
            proc.kill()


if __name__ == '__main__':
    AUT = Zappos()
    usage_name = usage_folder_map['filter'] # this usage_folder_map is defined in global_config.py
    # AUT = Abc()
    # usage_name = '18-TextSize'
    evaluation_with_true_label(AUT, usage_name)
    print('all done! :)')