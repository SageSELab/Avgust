import sys, os
import PIL
import psutil as psutil

current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir_path, '..', '3_model_generation'))
sys.path.insert(0, os.path.join(current_dir_path, '..'))

from global_config import *
from App_Config import *

from sys import argv
import os, shutil
import re
import explorer
import time
import json
import selenium
import test_generator_manual
import os.path
import pickle
from entities import IR_Model
import glob
import random
import pandas as pd
import webbrowser

class TestCase:
    def __init__(self, test_folder_path):
        self.test_folder_path = test_folder_path
        self.events = []

    def add_event(self, action, state, image_path, text, text_input):
        event = Event(action, state, image_path, text, text_input)
        self.events.append(event)

    def print_test_case(self):
        for event in self.events:
            if event.action == "oracle-text_input":
                print("--------------------")
                print("state: " + event.state)
                print("action: " + event.action)
                print("oracle text input: " + event.text_input)
            else:
                print("--------------------")
                print("state: " + event.state)
                print("action: " + event.action)
                print("image_path: " + event.image_path)
                print(event.text)


class Event:
    def __init__(self, action, state, image_path, text, text_input):
        self.action = action
        self.state = state
        self.image_path = image_path
        self.text = text
        self.text_input = text_input


class DestEvent:
    def __init__(self, action, exec_id_type, exec_id_val, text_input, isEnd, crop_screenshot_path, state_screenshot_path):
        self.action = action
        self.exec_id_type = exec_id_type
        self.exec_id_val = exec_id_val
        self.text_input = text_input
        self.isEnd = isEnd
        self.crop_screenshot_path = crop_screenshot_path
        self.state_screenshot_path = state_screenshot_path

    def print_event(self):
        print("---- printing dest event ----")
        print("action:")
        print(self.action)
        print("exec_id_type")
        print(self.exec_id_type)
        print("exec_id_val")
        print(self.exec_id_val)
        print("text_input")
        print(self.text_input)


class TestGenerator:
    def __init__(self, desiredCapabilities):
        self.explorer = explorer.Explorer(desiredCapabilities)
        self.test_num = 0
        self.MAX_TEST_NUM = 3

    def start(self, output_dir, usage_model_path, appname):
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        else:
            shutil.rmtree(output_dir)
            os.makedirs(output_dir)
        self.appname = appname
        self.output_dir = os.path.join(output_dir, appname)
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        self.generated_tests_dir = os.path.join(self.output_dir, 'generated_tests')
        self.MAX_ACTION = 20
        if not os.path.isdir(self.generated_tests_dir):
            os.makedirs(self.generated_tests_dir)
        self.load_usage_model(usage_model_path)
        self.generate_test()

    def load_usage_model(self, usage_model_path):
        pickle_filepath = os.path.join(usage_model_path)
        self.usage_model = pickle.load(open(pickle_filepath, 'rb'))

    def is_test_equal(self, test1, test2):
        if not len(test1) == len(test2):
            return False
        i = 0
        while i < len(test1):
            if not self.is_event_equal(test1[i], test2[i]):
                return False
        return True

    def save_test(self, current_generated_test):
        print('saving test', self.test_num, '...')
        for test_file in glob.glob(os.path.join(self.generated_tests_dir, 'test_executable*')):
            existing_test = pickle.load(open(test_file, 'rb'))
            if self.is_test_equal(existing_test, current_generated_test):
                print('test already generated')
                return
        file_path = os.path.join(self.generated_tests_dir, 'test_executable' + str(self.test_num) + '.pickle')
        with open(file_path, 'wb') as file:
            pickle.dump(current_generated_test, file)
        print('test generated and saved!')
        # file_path = os.path.join(self.generated_tests_dir, current_ir_model.name + '.png')
        # current_ir_model.get_graph().draw(file_path, prog='dot')
        # file_path = os.path.join(self.generated_tests_dir, current_ir_model.name + '.pickle')
        # with open(file_path, 'wb') as file:
        #     pickle.dump(current_ir_model, file)

    def generate_test(self):
        while self.test_num < self.MAX_TEST_NUM:
            step_index = 0
            isEnd_flag = False
            current_generated_test = [] # list of DestEvent/list(DestEvent) if self actions
            # current_ir_model = IR_Model('test_model' + str(self.test_num))
            self.explorer.test_num = self.test_num
            self.explorer.screenshot_idx = 0
            while step_index < self.MAX_ACTION and not isEnd_flag:
                time.sleep(2)
                current_state = self.explorer.extract_state(self.output_dir)
                current_state.print_state()
                # placeholder context: you only need to care about find_next_event_list function
                next_event_list = self.find_next_event_list(current_state)
                if next_event_list is None or len(next_event_list) == 0:
                    print('no next event found. ending dynamic generation...')
                    break
                elif len(next_event_list) == 1:
                    if type(next_event_list[0]) is list:
                        print('the only event is a list of the following events. should be self actions')
                        for event in next_event_list[0]:
                            print(event.exec_id_val, event.exec_id_val, event.action)
                            current_generated_test.append(event)
                            self.explorer.execute_event(event)
                    else:
                        isEnd_flag = (next_event_list[0]).isEnd
                        current_generated_test.append(next_event_list[0])
                        # current_ir_model.machine.add_transition(next_event_list[0].transition)
                        self.explorer.execute_event(next_event_list[0])
                else:
                    for next_event in next_event_list:
                        if type(next_event) is list: # trigger self actions first
                            for self_action in next_event:
                                current_generated_test.append(self_action)
                                # current_ir_model.machine.add_transition(self_action.transition)
                                self.explorer.execute_event(self_action)
                            next_event_list.remove(next_event)
                    # randomly pick one path after executing the self actions
                    random_idx = random.randint(0, len(next_event_list)-1)
                    next_event = next_event_list[random_idx]
                    isEnd_flag = next_event.isEnd
                    current_generated_test.append(next_event)
                    # current_ir_model.machine.add_transition(next_event.transition)
                    self.explorer.execute_event(next_event)
                step_index += 1
            self.save_test(current_generated_test)
            self.explorer.driver.close_app()
            self.explorer.driver.launch_app()
            self.test_num += 1

    def is_event_equal(self, event1, event2):
        if event1.exec_id_type == event2.exec_id_type and event1.exec_id_val == event2.exec_id_val:
            return True
        return False

    def find_mathing_state_in_usage_model(self, current_state):
        ### placeholder for screen classifier
        image = PIL.Image.open(current_state.screenshot_path)
        image.show()
        current_screenIR = input('manually type current state IR based on the screenshot that was just opened\n')
        triggers = self.usage_model.machine.get_triggers(current_screenIR)
        if len(triggers) == 0:
            ### placeholder for screen classifier to get 2nd, 3rd ... possible matching screenIR when the top1 doesn't have a match ###
            ### should NOT return None but should always find the closest state in the usage model
            return None
        else:
            return current_screenIR

    # def classify_widgetIR(self, element):
    #     ### placeholder for widget classifier ###
    #     ### element.path_to_screenshot gives you the croped image
    #     elementIR = input('manually type widget IR based on crop here' + element.path_to_screenshot + '\n')
    #     print('you typed', elementIR)
    #     return elementIR

    def is_final_trigger(self, trigger, source):
        if len(self.usage_model.machine.get_transitions(trigger=trigger, source=source, dest='end')) == 0:
            return False
        return True

    def is_widgetIR_input_type(self, widgetIR):
        widgetIR_file = os.path.join(USAGE_REPO_ROOT_DIR, 'IR', 'widget_ir.csv')
        df = pd.read_csv(widgetIR_file)
        row_found = df.loc[df['ir'] == widgetIR]
        if len(row_found) == 0:
            print('no widget IR found in the IR definition, check IR', widgetIR)
        elif row_found.iloc[0]['widget_type'] == 'input':
            return True
        return False

    def find_actions_from_self_transition(self, matching_screenIR, current_state):
        print('finding action list for self trigger of', matching_screenIR)
        self_actions = []
        self_transitions = self.usage_model.machine.get_transitions(trigger='self',
                                                                    source=matching_screenIR,
                                                                    dest=matching_screenIR)
        condition_list = self.usage_model.get_condition_list(self_transitions)
        all_triggers = self.usage_model.machine.get_triggers(matching_screenIR)
        needs_user_input = False
        for condition in condition_list:
            print('finding element for', condition)
            if '#' in condition:
                widgetIR = condition.split('#')[0]
                action = condition.split('#')[1]
                if self.is_widgetIR_input_type(widgetIR):
                    needs_user_input = True
                elif condition in all_triggers:
                    pass # if current self action is covered by other triggers, it means this self action can jump to a diff state, so skip it and handle it when it appears in other triggers (that's not self trigger)
                else:
                    for element in current_state.nodes:
                        if element.interactable:
                            ### placeholder to find matching element based on widgetIR. change code below ###
                            image = PIL.Image.open(element.path_to_screenshot)
                            image.show()
                            is_matched = input('check element that was just opened and enter y if matched')
                            if is_matched == 'y':
                                self_actions.append(DestEvent(action=action, exec_id_type=element.get_exec_id_type(),
                                                              exec_id_val=element.get_exec_id_val(), text_input='', isEnd=False,
                                                              crop_screenshot_path=element.path_to_screenshot, state_screenshot_path=current_state.screenshot_path))
            else:
                action = 'swipe-' + condition
                print('generated action', action)
                self_actions.append(DestEvent(action=action, exec_id_val='', exec_id_type='', text_input='', isEnd=False, crop_screenshot_path=None,
                                              state_screenshot_path=current_state.screenshot_path))

        # generate actions for EditText fields and fill the form
        if needs_user_input:
            print('generating user inputs...')
            for element in current_state.nodes:
                if element.interactable and 'EditText' in element.get_element_type():
                    image = PIL.Image.open(element.path_to_screenshot)
                    image.show()
                    user_input = input('please enter your input for element that was just opened\n enter nothing if you want to skip this element\n')
                    if not user_input == '':
                        self_actions.append(DestEvent(action='send_keys', exec_id_type=element.get_exec_id_type(),
                                                      exec_id_val=element.get_exec_id_val(),
                                                      text_input=user_input, isEnd=False, crop_screenshot_path=element.path_to_screenshot,
                                                      state_screenshot_path=current_state.screenshot_path))

        return self_actions

    def find_matching_element_per_trigger(self, current_state, trigger):
        print('finding matching action for trigger', trigger)
        widgetIR = trigger.split('#')[0]
        # The elements (widgets) are of type of node objects defined in node.py
        for element in current_state.nodes:
            if element.interactable:
                ### placeholder to find matching element based on widgetIR. change code below ###
                image = PIL.Image.open(element.path_to_screenshot)
                image.show()
                is_matched = input('check element that was just opened. enter y if matched')
                if is_matched == 'y':
                    return element
        return None

    def find_possible_next_actions(self, current_state, matching_screenIR, triggers):
        possible_actions = []
        for trigger in triggers:
            if trigger == 'self':
                raise ValueError('self trigger should be removed already, check triggers of ', matching_screenIR)
            isEnd = self.is_final_trigger(trigger=trigger, source=matching_screenIR)
            # placeholder context: change find_matching_element_per_trigger function
            matching_element = self.find_matching_element_per_trigger(current_state, trigger)
            if matching_element is not None:
                # transition = {'trigger': trigger, 'source': matching_screenIR, 'dest': 'aaa', 'conditions': ['con1', 'con2'],
                #               'label': ['label1']}
                possible_actions.append(DestEvent(action=trigger.split('#')[1], exec_id_type=matching_element.get_exec_id_type(),
                                                  exec_id_val=matching_element.get_exec_id_val(), text_input='', isEnd=isEnd,
                                                  crop_screenshot_path=matching_element.path_to_screenshot, state_screenshot_path=current_state.screenshot_path))
        return possible_actions

    def find_next_event_list(self, current_state):
        next_event_list = []
        # placeholder context: change find_matching_state_in_usage_model function
        matching_screenIR = self.find_mathing_state_in_usage_model(current_state)
        if matching_screenIR is None:
            print('no matching state found in the usage model...')
            return []
        else:
            all_possible_triggers = self.usage_model.machine.get_triggers(matching_screenIR)
            if 'self' in all_possible_triggers:
                # self_actions is a *list* of DestEvent
                # placeholder context: change find_actions_from_self_transition function
                self_actions = self.find_actions_from_self_transition(matching_screenIR, current_state)
                next_event_list.append(self_actions)
                all_possible_triggers.remove('self')
            # placeholder context: change find_possible_next_actions function
            possible_actions = self.find_possible_next_actions(current_state, matching_screenIR, all_possible_triggers)
            for possible_action in possible_actions:
                next_event_list.append(possible_action)
        return next_event_list
        # In the end your next event is a combination of a widget (next_event_widget) which is the type of the
        # node object defined in node.py. and and action that can be either "click" or "send_keys" or
        # "send_keys_enter" or "long" or "swipe-up" etc. You can use the code line below to make a DestEvent (which is defined at the top of this file) - if your action type is send keys then the text input
        # argument would be the input ow it would be empty string

if __name__ == "__main__":
    # appPackage and appActivity can be found here for shooping apps: https://github.com/felicitia/UsageTesting-Repo/blob/master/shopping_app_info.csv
    # here for news apps: https://github.com/felicitia/UsageTesting-Repo/blob/master/news_app_info.csv
    # desiredCapabilities = {
    #     "platformName": "Android",
    #     "deviceName": "emulator-5554", # adb devices
    #     "newCommandTimeout": 10000,
    #     "appPackage": "com.etsy.android",
    #     "appActivity": "com.etsy.android.ui.homescreen.HomescreenTabsActivity"
    # }

    # AUT = Etsy()
    # usage_name = '1-SignIn'
    AUT = Abc()
    usage_name = '18-TextSize'

    start = time.time()
    test_gen = TestGenerator(AUT.desiredCapabilities)

    final_data_root = FINAL_ARTIFACT_ROOT_DIR

    usage_model_path = os.path.join(final_data_root, 'output', 'models', usage_name,
                                    'usage_model-' + AUT.appname + '.pickle')
    # dynamic_output folder contains our output and will be generated automatically, no need to create an empty folder
    output_path = os.path.join(final_data_root, 'output', 'models', usage_name, 'dynamic_output')

    test_gen.start(output_path, usage_model_path, AUT)
    end = time.time()
    print("Dynamic generation running time " + str(end - start) + " seconds")
    # kill all the images opened by Preview
    for proc in psutil.process_iter():
        # print(proc.name())
        if proc.name() == 'Preview':
            proc.kill()