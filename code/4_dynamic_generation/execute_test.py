from sys import argv
import os, sys
import re

import psutil

import explorer
import time
import json
import selenium
from test_generator_manual import TestGenerator, DestEvent
from explorer import Explorer
import pickle

current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir_path, '..'))

from global_config import *


if __name__ == '__main__':
    desiredCapabilities = {
        "platformName": "Android",
        "deviceName": "emulator-5554",
        "newCommandTimeout": 10000,
        "appPackage": "com.etsy.android",
        "appActivity": "com.etsy.android.ui.homescreen.HomescreenTabsActivity"
    }
    start = time.time()
    explorer = Explorer(desiredCapabilities)
    # explorer.execute_test('/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/dynamic_output/etsy/generated_tests/test_executable0.pickle')
    explorer.execute_test_and_generate_linear_model(os.path.join(USAGE_REPO_ROOT_DIR, 'video_data_examples/dynamic_output/etsy/generated_tests/test_executable0.pickle'))
    end = time.time()
    print("test running time " + str(end - start) + " seconds")
    # kill all the images opened by Preview
    for proc in psutil.process_iter():
        # print(proc.name())
        if proc.name() == 'Preview':
            proc.kill()