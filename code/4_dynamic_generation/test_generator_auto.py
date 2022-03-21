import sys

import PIL
import psutil as psutil
import os, shutil

current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir_path, '..', '3_model_generation'))
sys.path.insert(0, os.path.join(current_dir_path, 'autoencoder_MLP'))
sys.path.insert(0, os.path.join(current_dir_path, '..'))

from global_config import *
from bert_similarity_calc import SimilarityCalculator_BERT
from text_similarity_calculator import SimilarityCalculator_W2V
from App_Config import *
from sentence_transformers import SentenceTransformer

import explorer
import time
import json
import os.path
import pickle
import glob
import pandas as pd
import nltk
import random

os.environ['TOKENIZERS_PARALLELISM'] = "False"


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
    def __init__(self, action, exec_id_type, exec_id_val, text_input, isEnd, crop_screenshot_path,
                 state_screenshot_path, matched_trigger="unknown"):
        self.action = action
        self.exec_id_type = exec_id_type
        self.exec_id_val = exec_id_val
        self.text_input = text_input
        self.isEnd = isEnd
        self.crop_screenshot_path = crop_screenshot_path
        self.state_screenshot_path = state_screenshot_path
        self.matched_trigger = matched_trigger

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
    def __init__(self, desiredCapabilities, text_sim_flag=False, REMAUI_flag=False, eval_flag=False,
                 use_TRUE_label_flag=False):
        self.explorer = explorer.Explorer(desiredCapabilities)
        self.test_num = 0
        self.MAX_TEST_NUM = 1
        self.REMAUI_flag = REMAUI_flag
        self.eval_flag = eval_flag
        self.use_TRUE_IR_flag = use_TRUE_label_flag
        self.bert = SentenceTransformer('bert-base-nli-mean-tokens').to('cpu')
        nltk.download('words')
        nltk.download('punkt')
        self.words = set(nltk.corpus.words.words())

        if text_sim_flag:
            self.text_sim_w2v = SimilarityCalculator_W2V()
            self.text_sim_bert = SimilarityCalculator_BERT()
        else:
            self.text_sim_w2v = None
            self.text_sim_bert = None

        if eval_flag:
            self.eval_results = {}

    def start(self, dynamic_output_root_dir, usage_model_path, appname):
        if not os.path.isdir(dynamic_output_root_dir):
            os.makedirs(dynamic_output_root_dir)

        self.appname = appname
        self.output_dir = os.path.join(dynamic_output_root_dir, appname)
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        else:
            delete_input = input(self.output_dir + ' already existed! delete it? enter y to delete\n')
            if delete_input == 'y':
                shutil.rmtree(self.output_dir)
                os.makedirs(self.output_dir)

        self.generated_tests_dir = os.path.join(self.output_dir, 'generated_tests')
        self.widget_classification_res_dir = os.path.join(self.output_dir, 'widget_classifier')
        self.MAX_ACTION = 10
        if not os.path.isdir(self.generated_tests_dir):
            os.makedirs(self.generated_tests_dir)
        if not os.path.isdir(self.widget_classification_res_dir):
            os.makedirs(self.widget_classification_res_dir)
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
            i += 1
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

    def generate_test(self):
        while self.test_num < self.MAX_TEST_NUM:
            step_index = 0
            isEnd_flag = False
            current_generated_test = []  # list of DestEvent/list(DestEvent) if self actions
            # current_ir_model = IR_Model('test_model' + str(self.test_num))
            self.explorer.test_num = self.test_num
            self.explorer.screenshot_idx = 0
            while step_index < self.MAX_ACTION and not isEnd_flag:
                time.sleep(10)
                scroll = input('Do you want to scroll down to see more widgets first?')
                current_state = self.explorer.extract_state(self.output_dir)
                next_event_list, recorded_states_and_triggers = self.find_next_event_list(current_state)
                if scroll == 'up' or scroll == 'down' or scroll == 'left' or scroll == 'right':
                    next_event = DestEvent(action='swipe-' + scroll,
                                                     exec_id_type=None,
                                                     exec_id_val=None, text_input='', isEnd=False,
                                                     crop_screenshot_path=None,
                                                     state_screenshot_path=current_state.screenshot_path)

                    XML_basename = os.path.basename(os.path.normpath(current_state.UIXML_path)).replace(
                        '.xml', '')
                    if XML_basename in self.eval_results.keys():
                        self.eval_results[XML_basename]['true_widget_IR'] = scroll
                    else:
                        self.eval_results[XML_basename] = {}
                        self.eval_results[XML_basename]['true_widget_IR'] = scroll
                    current_generated_test.append(next_event)
                    self.explorer.execute_event(next_event)

                else:
                    if (recorded_states_and_triggers["screen"] == "sign_in") or (recorded_states_and_triggers["screen"] == "sign_up"):
                        has_input_text = False
                        for next_event in next_event_list:
                            if type(next_event) == list:
                                for e in next_event:
                                    if e.action == "send_keys":
                                        has_input_text = True
                        if not has_input_text:
                            self_actions = []
                            print('generating user inputs...')
                            for element in current_state.nodes:
                                if element.interactable and 'EditText' in element.get_element_type():
                                    image = PIL.Image.open(element.path_to_screenshot)
                                    image.show()
                                    user_input = input(
                                        'please enter your input for element that was just opened\n enter nothing if you want to skip this element\n')
                                    if not user_input == '':
                                        self_actions.append(
                                            DestEvent(action='send_keys', exec_id_type=element.get_exec_id_type(),
                                                      exec_id_val=element.get_exec_id_val(),
                                                      text_input=user_input, isEnd=False,
                                                      crop_screenshot_path=element.path_to_screenshot,
                                                      state_screenshot_path=current_state.screenshot_path))
                                    for proc in psutil.process_iter():
                                        if proc.name() == 'Preview':
                                            proc.kill()
                            next_event_list = [self_actions] + next_event_list

                    if next_event_list is None or len(next_event_list) == 0:
                        element_candidates = []
                        for element in current_state.nodes:
                            if element.interactable:
                                image = PIL.Image.open(element.path_to_screenshot)
                                image.show()
                                element_candidates.append(element)
                        event_index = int(input(
                            'no next event found based on the usage model, please provide the index of the event to trigger (enter any out of range index to end current test)\n'))
                        # kill all the images opened by Preview
                        for proc in psutil.process_iter():
                            # print(proc.name())
                            if proc.name() == 'Preview':
                                proc.kill()
                        if event_index >= len(element_candidates):
                            break
                        else:
                            element = element_candidates[event_index]
                            guided_event = DestEvent(action='click', exec_id_type=element.get_exec_id_type(),
                                                     exec_id_val=element.get_exec_id_val(), text_input='', isEnd=False,
                                                     crop_screenshot_path=element.path_to_screenshot,
                                                     state_screenshot_path=current_state.screenshot_path)
                            current_generated_test.append(guided_event)
                            self.explorer.execute_event(guided_event)

                    elif len(next_event_list) == 1:
                        if type(next_event_list[0]) is list:
                            print('the only event is a list of the following events. should be self actions')
                            for event in next_event_list[0]:
                                print(event.exec_id_val, event.exec_id_val, event.action)
                                current_generated_test.append(event)
                                self.explorer.execute_event(event)
                                correct_widgetIR = input('Please enter the ground truth IR for the widget you chose:')
                                XML_basename = os.path.basename(os.path.normpath(current_state.UIXML_path)).replace('.xml',
                                                                                                                    '')
                                if XML_basename in self.eval_results.keys():
                                    self.eval_results[XML_basename]['true_widget_IR'] = correct_widgetIR
                                else:
                                    self.eval_results[XML_basename] = {}
                                    self.eval_results[XML_basename]['true_widget_IR'] = correct_widgetIR
                                for proc in psutil.process_iter():
                                    if proc.name() == 'Preview':
                                        proc.kill()
                        else:
                            print("only one action is possible in this step.")
                            image = PIL.Image.open(next_event_list[0].crop_screenshot_path)
                            image.show()
                            correct_widgetIR = input('Please enter the ground truth IR for the widget you chose:')
                            XML_basename = os.path.basename(os.path.normpath(current_state.UIXML_path)).replace('.xml', '')
                            if XML_basename in self.eval_results.keys():
                                self.eval_results[XML_basename]['true_widget_IR'] = correct_widgetIR
                            else:
                                self.eval_results[XML_basename] = {}
                                self.eval_results[XML_basename]['true_widget_IR'] = correct_widgetIR
                            for proc in psutil.process_iter():
                                if proc.name() == 'Preview':
                                    proc.kill()
                            isEnd_flag = (next_event_list[0]).isEnd
                            if isEnd_flag:
                                ans = input("The model detected that the program should end now, do you want to keep going?")
                                if ans == 'y':
                                    isEnd_flag = False
                            current_generated_test.append(next_event_list[0])
                            step_classification_res_dir_path = os.path.join(self.widget_classification_res_dir,
                                                                            XML_basename)
                            if not os.path.isdir(step_classification_res_dir_path):
                                os.makedirs(step_classification_res_dir_path)
                            image_name = str(0) + ".png"
                            image.save(os.path.join(step_classification_res_dir_path, image_name))
                            with open(os.path.join(step_classification_res_dir_path, "recoded_state_triggers.json"),
                                      "w") as triggers_file:
                                json.dump(recorded_states_and_triggers, triggers_file)
                            self.explorer.execute_event(next_event_list[0])
                    else:
                        added_in_step = 1
                        for next_event in next_event_list:
                            if type(next_event) is list:  # trigger self actions first
                                for self_action in next_event:
                                    current_generated_test.append(self_action)
                                    if self_action.action == "send_keys":
                                        self.explorer.execute_event(self_action)
                                        correct_widgetIR = input(
                                            'Please enter the ground truth IR for the widget the input was typed on:')
                                        XML_basename = os.path.basename(os.path.normpath(current_state.UIXML_path)).replace(
                                            '.xml', '') + "-" + str(added_in_step)
                                        if XML_basename in self.eval_results.keys():
                                            self.eval_results[XML_basename]['true_widget_IR'] = correct_widgetIR
                                        else:
                                            self.eval_results[XML_basename] = {}
                                            self.eval_results[XML_basename]['true_widget_IR'] = correct_widgetIR
                                        added_in_step += 1
                                    else:
                                        next_event_list.append(self_action)
                                next_event_list.remove(next_event)

                        XML_basename = os.path.basename(os.path.normpath(current_state.UIXML_path)).replace('.xml', '')
                        step_classification_res_dir_path = os.path.join(self.widget_classification_res_dir, XML_basename)
                        if len(next_event_list) != 0:
                            if not os.path.isdir(step_classification_res_dir_path):
                                os.makedirs(step_classification_res_dir_path)
                        print(next_event_list)
                        for i, event in enumerate(next_event_list):
                            print(event.exec_id_val)
                            print("id:" + str(i) + " - val: " + event.exec_id_val + "- matched with: " + event.matched_trigger)
                            image = PIL.Image.open(event.crop_screenshot_path)
                            image.show()
                            image_name = str(i) + "-" + event.matched_trigger + ".png"
                            image.save(os.path.join(step_classification_res_dir_path, image_name))

                        with open(os.path.join(step_classification_res_dir_path, "recoded_state_triggers.json"),
                                  "w") as triggers_file:
                            json.dump(recorded_states_and_triggers, triggers_file)
                        event_indx = input('Choose the id of the widget you want to interact with:')
                        next_event = next_event_list[int(event_indx)]
                        if next_event.action == "send_keys":
                            input_text = input('Type in the input for the chosen widget:')
                            next_event.text_input = input_text
                        correct_widgetIR = input('Please enter the ground truth IR for the widget you chose:')

                        if added_in_step != 1:
                            XML_basename += "-" + str(added_in_step)
                        if XML_basename in self.eval_results.keys():
                            self.eval_results[XML_basename]['true_widget_IR'] = correct_widgetIR
                        else:
                            self.eval_results[XML_basename] = {}
                            self.eval_results[XML_basename]['true_widget_IR'] = correct_widgetIR
                        isEnd_flag = next_event.isEnd
                        if isEnd_flag:
                            ans = input("The model detected that the program should end now, do you want to keep going?")
                            if ans == 'y':
                                isEnd_flag = False
                        current_generated_test.append(next_event)
                        for proc in psutil.process_iter():
                            if proc.name() == 'Preview':
                                proc.kill()
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
        # image = PIL.Image.open(current_state.screenshot_path)
        # image.show()
        # current_screenIR = input('manually type current state IR based on the screenshot that was just opened\n')
        if self.use_TRUE_IR_flag:
            print('states in usage model:', self.usage_model.states)
            screenIR_input = input('\nthe TRUE screen IR you want to use\n')
            current_screenIR = current_state.get_screenIR(self.eval_results, self.appname, self.usage_model,
                                                          self.text_sim_w2v, self.text_sim_bert,
                                                          self.REMAUI_flag, true_IR=screenIR_input)
        else:
            XML_basename = os.path.basename(os.path.normpath(current_state.UIXML_path)).replace('.xml', '')
            top1, top5, top10 = current_state.get_screen_IR(self.appname, self.bert, self.words, self.usage_model)
            print("The screen classifier top1 guess for the screen: ")
            print(top1)
            print("The screen classifier top5 guesses for the screen: ")
            print(top5)

            current_screenIR = input('\nChoose the closest screen tag from the top5 guesses:\n')
            correct_screenIR = input('\nType in the correct screen tag:\n')

            if XML_basename in self.eval_results.keys():
                self.eval_results[XML_basename]['true_screen_IR'] = correct_screenIR
            else:
                self.eval_results[XML_basename] = {}
                self.eval_results[XML_basename]['true_screen_IR'] = correct_screenIR

        triggers = self.usage_model.machine.get_triggers(current_screenIR)

        if len(triggers) == 0:
            print('current screenIR', current_screenIR)
            if self.use_TRUE_IR_flag:
                if current_screenIR == 'popup':
                    print('next possible actions:', 'continue')
                else:
                    screenIR_input = input(
                        'current screenIR does not have any triggers... please re-enter the correct screenIR and make sure it is in the states of the modle\n')
                    current_screenIR = current_state.get_screenIR(self.eval_results, self.appname, self.usage_model,
                                                                  self.text_sim_w2v, self.text_sim_bert,
                                                                  self.REMAUI_flag, true_IR=screenIR_input)
                    triggers = self.usage_model.machine.get_triggers(current_screenIR)
                    print('------------------')
                    print('next possible actions:', triggers)
                    return current_screenIR
            else:
                raise ValueError('current screenIR does not have any triggers...')
        else:
            return current_screenIR

    def is_final_trigger(self, trigger, source):
        if len(self.usage_model.machine.get_transitions(trigger=trigger, source=source, dest='end')) == 0:
            return False
        return True

    def is_widgetIR_input_type(self, widgetIR):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        widgetIR_file = os.path.join(current_dir_path, '..', '..', 'IR', 'widget_ir.csv')
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
        self_actions_added = set()
        for condition in condition_list:
            print('finding element for', condition)

            if '#' in condition:
                widgetIR = condition.split('#')[0]
                action = condition.split('#')[1]
                if self.is_widgetIR_input_type(widgetIR):
                    needs_user_input = True
                elif condition in all_triggers:
                    pass  # if current self action is covered by other triggers, it means this self action can jump to a diff state, so skip it and handle it when it appears in other triggers (that's not self trigger)
                else:
                    top_candidates, secondary_candidates, heuristic_matches = current_state.find_widget_to_trigger(
                        widgetIR, matching_screenIR, self.bert, self.appname)
                    for element in heuristic_matches:
                        if element.get_exec_id_val() not in self_actions_added:
                            self_actions.append(DestEvent(action=action, exec_id_type=element.get_exec_id_type(),
                                                          exec_id_val=element.get_exec_id_val(), text_input='', isEnd=False,
                                                          crop_screenshot_path=element.path_to_screenshot,
                                                          state_screenshot_path=current_state.screenshot_path))
                            self_actions_added.add(element.get_exec_id_val())
                print("every thing that was added from self:")
                print(self_actions_added)
        # generate actions for EditText fields and fill the form
        if needs_user_input:
            print('generating user inputs...')
            for element in current_state.nodes:
                if element.interactable and 'EditText' in element.get_element_type():
                    image = PIL.Image.open(element.path_to_screenshot)
                    image.show()
                    user_input = input(
                        'please enter your input for element that was just opened\n enter nothing if you want to skip this element\n')
                    if not user_input == '':
                        self_actions.append(DestEvent(action='send_keys', exec_id_type=element.get_exec_id_type(),
                                                      exec_id_val=element.get_exec_id_val(),
                                                      text_input=user_input, isEnd=False,
                                                      crop_screenshot_path=element.path_to_screenshot,
                                                      state_screenshot_path=current_state.screenshot_path))
                    for proc in psutil.process_iter():
                        if proc.name() == 'Preview':
                            proc.kill()

        return self_actions

    def find_matching_element_per_trigger(self, current_state, trigger, screenIR):
        print('finding matching action for trigger', trigger)
        widgetIR = trigger.split('#')[0]
        top_candidates, secondary_candidates, heuristic_based_candidates = current_state.find_widget_to_trigger(
            widgetIR, screenIR, self.bert, self.appname)
        return top_candidates, secondary_candidates, heuristic_based_candidates

    def find_possible_next_actions(self, current_state, matching_screenIR, triggers, added_from_self):
        SUGGESTION_CNT = 5
        top_actions = []
        secondary_actions = []
        heuristic_actions = []
        tops = set()
        secondaries = set()
        heuristics = set()
        for event in added_from_self:
            if type(event) is list:
                for e in event:
                    heuristics.add(e.exec_id_val)
            else:
                heuristics.tops.add(event.exec_id_val)
        for trigger in triggers:
            if trigger == 'self':
                raise ValueError('self trigger should be removed already, check triggers of ', matching_screenIR)
            isEnd = self.is_final_trigger(trigger=trigger, source=matching_screenIR)
            top_matches, secondary_matches, heuristic_based_matches = self.find_matching_element_per_trigger(
                current_state, trigger, matching_screenIR)
            if len(heuristic_based_matches) > 0:
                for match in heuristic_based_matches:
                    action = trigger.split('#')[-1]
                    if match.get_element_type().split('.')[-1] == "EditText":
                        action = "send_keys"
                    if match.get_exec_id_val() not in heuristics:
                        heuristic_actions.append(DestEvent(action=action, exec_id_type=match.get_exec_id_type(),
                                                           exec_id_val=match.get_exec_id_val(), text_input='',
                                                           isEnd=isEnd,
                                                           crop_screenshot_path=match.path_to_screenshot,
                                                           state_screenshot_path=current_state.screenshot_path, matched_trigger=trigger))
                        heuristics.add(match.get_exec_id_val())
                        if match.get_exec_id_val() in tops:
                            tops.remove(match.get_exec_id_val())
                        if match.get_exec_id_val() in secondaries:
                            secondaries.remove(match.get_exec_id_val())
            if len(top_matches) > 0:
                for match in top_matches:
                    action = trigger.split('#')[-1]
                    if match.get_element_type().split('.')[-1] == "EditText":
                        action = "send_keys"
                    if (match.get_exec_id_val() not in tops) and (match.get_exec_id_val() not in heuristics):
                        top_actions.append(DestEvent(action=action, exec_id_type=match.get_exec_id_type(),
                                                     exec_id_val=match.get_exec_id_val(), text_input='', isEnd=isEnd,
                                                     crop_screenshot_path=match.path_to_screenshot,
                                                     state_screenshot_path=current_state.screenshot_path, matched_trigger=trigger))
                        tops.add(match.get_exec_id_val())
                        if match.get_exec_id_val() in secondaries:
                            secondaries.remove(match.get_exec_id_val())
            if len(secondary_matches) > 0:
                for match in secondary_matches:
                    action = trigger.split('#')[-1]
                    if match.get_element_type().split('.')[-1] == "EditText":
                        action = "send_keys"
                    if (match.get_exec_id_val() not in secondaries) and (match.get_exec_id_val() not in tops) and (
                            match.get_exec_id_val() not in heuristics):
                        secondary_actions.append(DestEvent(action=action, exec_id_type=match.get_exec_id_type(),
                                                           exec_id_val=match.get_exec_id_val(), text_input='',
                                                           isEnd=isEnd,
                                                           crop_screenshot_path=match.path_to_screenshot,
                                                           state_screenshot_path=current_state.screenshot_path, matched_trigger=trigger))
                        secondaries.add(match.get_exec_id_val())

        print("not in self at the end:")
        print(heuristics)
        print(tops)
        print(secondaries)
        if len(heuristic_actions) >= SUGGESTION_CNT:
            return heuristic_actions[:SUGGESTION_CNT]
        elif len(heuristic_actions) + len(top_actions) > SUGGESTION_CNT:
            chosen_top_actions = top_actions[:(SUGGESTION_CNT - len(heuristic_actions))]
            return heuristic_actions + chosen_top_actions
        else:
            chosen_secondary = secondary_actions[:(SUGGESTION_CNT - len(top_actions) - len(heuristic_actions))]
            return heuristic_actions + top_actions + chosen_secondary

    def find_all_triggers_in_model(self):
        all_triggers = set()
        for state in self.usage_model.states:
            current_triggers = self.usage_model.machine.get_triggers(state)
            for trigger in current_triggers:
                if trigger == 'self':
                    self_transitions = self.usage_model.machine.get_transitions(trigger='self', source=state,
                                                                                dest=state)
                    for condition in self.usage_model.get_condition_list(self_transitions):
                        all_triggers.add(condition)
                else:
                    all_triggers.add(trigger)
        excluding_trigger = {'to_start', 'initial'}
        return all_triggers - excluding_trigger

    def find_next_event_list(self, current_state):
        next_event_list = []
        # placeholder context: change find_matching_state_in_usage_model function
        matching_screenIR = self.find_mathing_state_in_usage_model(current_state)
        if matching_screenIR is None:
            print('no matching state found in the usage model...')
            return []
        else:
            if self.use_TRUE_IR_flag:  # when using true labels, just pick an interactable widget directly
                matching_element = None
                # trigger_exist_flag = input('does any of the suggested widgets exist on the current screen? answer n or No; anything else for Yes\n')
                # if trigger_exist_flag == 'n':
                print('all possible actions in the model', self.find_all_triggers_in_model())
                while matching_element is None:
                    for element in current_state.nodes:
                        # print(element.get_element_type())
                        if element.interactable:
                            image = PIL.Image.open(element.path_to_screenshot)
                            image.show()
                            user_input = input(
                                'picking this widget? type the TRUE widget IR to select it; type space to skip it\n(Also, you can type up/down/left/right if you need to scroll)\n')
                            # print('stripping user input', user_input.strip())
                            if user_input.strip() != '':
                                if user_input == 'up' or user_input == 'down' or user_input == 'left' or user_input == 'right':
                                    next_event_list.append(DestEvent(action='swipe-' + user_input,
                                                                     exec_id_type=None,
                                                                     exec_id_val=None, text_input='', isEnd=False,
                                                                     crop_screenshot_path=None,
                                                                     state_screenshot_path=current_state.screenshot_path))

                                    XML_basename = os.path.basename(os.path.normpath(current_state.UIXML_path)).replace(
                                        '.xml', '')
                                    if XML_basename in self.eval_results.keys():
                                        self.eval_results[XML_basename]['true_widget_IR'] = user_input
                                    else:
                                        self.eval_results[XML_basename] = {}
                                        self.eval_results[XML_basename]['true_widget_IR'] = user_input
                                    return next_event_list

                                else:
                                    matching_element = element
                                    XML_basename = os.path.basename(os.path.normpath(current_state.UIXML_path)).replace(
                                        '.xml', '')
                                    if XML_basename in self.eval_results.keys():
                                        self.eval_results[XML_basename]['true_widget_IR'] = user_input
                                    else:
                                        self.eval_results[XML_basename] = {}
                                        self.eval_results[XML_basename]['true_widget_IR'] = user_input
                                    break

                user_input = input(
                    'is this the last action? type y to set isEnd flag True; type anything else to set it False\n')
                if user_input == 'y':
                    isEnd = True
                else:
                    isEnd = False

                input_element_type = ['EditText', 'AutoCompleteTextView', 'Spinner']
                if matching_element.get_element_type().split('.')[-1] in input_element_type:
                    user_input = input('type the text input you want to use\n')
                    next_event_list.append(
                        DestEvent(action='send_keys', exec_id_type=matching_element.get_exec_id_type(),
                                  exec_id_val=matching_element.get_exec_id_val(), text_input=user_input, isEnd=isEnd,
                                  crop_screenshot_path=matching_element.path_to_screenshot,
                                  state_screenshot_path=current_state.screenshot_path))
                else:
                    next_event_list.append(
                        DestEvent(action='click', exec_id_type=matching_element.get_exec_id_type(),
                                  exec_id_val=matching_element.get_exec_id_val(), text_input='', isEnd=isEnd,
                                  crop_screenshot_path=matching_element.path_to_screenshot,
                                  state_screenshot_path=current_state.screenshot_path))

                # kill all the images opened by Preview
                for proc in psutil.process_iter():
                    # print(proc.name())
                    if proc.name() == 'Preview':
                        proc.kill()

            else:
                all_possible_triggers = self.usage_model.machine.get_triggers(matching_screenIR)
                state_and_triggers_recorded = {
                    "screen": matching_screenIR,
                    "triggers": all_possible_triggers
                }
                if 'self' in all_possible_triggers:
                    self_actions = self.find_actions_from_self_transition(matching_screenIR, current_state)
                    next_event_list.append(self_actions)
                    all_possible_triggers.remove('self')
                # placeholder context: change find_possible_next_actions function
                possible_actions = self.find_possible_next_actions(current_state, matching_screenIR,
                                                                   all_possible_triggers, next_event_list)
                for possible_action in possible_actions:
                    next_event_list.append(possible_action)

        return next_event_list, state_and_triggers_recorded
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
    AUT = Zappos()
    usage_name = '15-Filter'
    start = time.time()
    test_gen = TestGenerator(AUT.desiredCapabilities)

    final_data_root = FINAL_ARTIFACT_ROOT_DIR

    usage_model_path = os.path.join(final_data_root, 'output', 'models', usage_name,
                                    'usage_model-' + AUT.appname + '.pickle')
    # dynamic_output folder contains our output and will be generated automatically, no need to create an empty folder
    output_path = os.path.join(final_data_root, 'output', 'models', usage_name, 'dynamic_output')

    test_gen.start(output_path, usage_model_path, AUT.appname)

    end = time.time()
    print("Dynamic generation running time " + str(end - start) + " seconds")

    # kill all the images opened by Preview
    for proc in psutil.process_iter():
        # print(proc.name())
        if proc.name() == 'Preview':
            proc.kill()
