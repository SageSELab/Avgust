import PIL
from appium import webdriver
import layout_tree as LayoutTree
import time
import os, csv
from appium.webdriver.common.touch_action import TouchAction
import pickle
import sys

current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_dir_path, '..', '3_model_generation'))

from entities import IR_Model
from pathlib import Path
import pandas as pd
import json

class Explorer:
    def __init__(self, desiredCapabilities):
        # replace with you own desired capabilities for Appium
        self.desiredCapabilities = desiredCapabilities
        # make sure too change to port your Appium server is listening on
        d = webdriver.Remote('http://localhost:4723/wd/hub', self.desiredCapabilities)
        assert d is not None
        self.driver = d
        self.screenshot_idx = 0
        self.test_num = 0

    def execute_test(self, test_file):
        test = pickle.load(open(test_file, 'rb'))
        for event in test:
            if type(event) is list:
                for self_event in event:
                    self.execute_event(self_event)
            else:
                self.execute_event(event)


    def get_current_widgetIR(self, event, annotation_df):
        crop_path = event.crop_screenshot_path
        row_found = annotation_df.loc[annotation_df['filepath'] == crop_path]
        if len(row_found) == 0:
            image = PIL.Image.open(event.crop_screenshot_path)
            image.show()
            widgetIR = input('type widget IR that is about to trigger\n')
            annotation_df = annotation_df.append({'filepath' : crop_path, 'IR': widgetIR}, ignore_index = True)
            return widgetIR, annotation_df
        elif len(row_found) == 1:
            if pd.isna(row_found['IR'].values[0]):
                image = PIL.Image.open(event.crop_screenshot_path)
                image.show()
                widgetIR = input('type widget IR that is about to trigger\n')
                annotation_df = annotation_df.append({'filepath' : crop_path, 'IR': widgetIR}, ignore_index = True)
                return widgetIR, annotation_df
            return row_found['IR'].values[0], annotation_df
        else:
            raise ValueError('row found is > 1 when getting widgetIR, check', event.crop_screenshot_path)

    def get_current_screenIR(self, event, annotation_df):
        screenshot_path = event.state_screenshot_path
        row_found = annotation_df.loc[annotation_df['filepath'] == screenshot_path]
        if len(row_found) == 0:
            image = PIL.Image.open(event.state_screenshot_path)
            image.show()
            current_screenIR = input('type current screen IR shown in the screenshot\n')
            annotation_df = annotation_df.append({'filepath' : screenshot_path, 'IR': current_screenIR}, ignore_index = True)
            return current_screenIR, annotation_df
        elif len(row_found) == 1:
            if pd.isna(row_found['IR'].values[0]):
                image = PIL.Image.open(event.state_screenshot_path)
                image.show()
                current_screenIR = input('type current screen IR shown in the screenshot\n')
                annotation_df = annotation_df.append({'filepath' : screenshot_path, 'IR': current_screenIR}, ignore_index = True)
                return current_screenIR, annotation_df
            return row_found['IR'].values[0], annotation_df
        else:
            raise ValueError('row found is > 1 when getting screenIR, check', event.state_screenshot_path)

    def execute_test_and_generate_linear_model(self, test_file):
        test = pickle.load(open(test_file, 'rb'))
        linear_model = []
        dynamic_annotation_file = os.path.join(Path(test_file).parent.parent.parent.parent.absolute(), 'dynamic_annotations.csv')
        if not os.path.exists(dynamic_annotation_file):
            headers = ['filepath', 'IR']
            with open(dynamic_annotation_file, 'w') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(headers)
        annotation_df = pd.read_csv(dynamic_annotation_file)
        for event in test:
            if type(event) is list:
                for self_event in event:
                    current_screenIR, annotation_df = self.get_current_screenIR(self_event, annotation_df)
                    action = self_event.action
                    if 'swipe' in action:
                        swipe_direction = event.action.split('-')[1]
                        linear_model.append({'state': current_screenIR, 'transition': swipe_direction})
                    else:
                        widgetIR, annotation_df = self.get_current_widgetIR(self_event, annotation_df)
                        transition_name = widgetIR + '#' + action
                        linear_model.append({'state': current_screenIR, 'transition': transition_name})
                    self.execute_event(self_event)
            else:
                current_screenIR, annotation_df = self.get_current_screenIR(event, annotation_df)
                action = event.action
                if 'swipe' in action:
                    swipe_direction = event.action.split('-')[1]
                    linear_model.append({'state': current_screenIR, 'transition': swipe_direction})
                else:
                    widgetIR, annotation_df = self.get_current_widgetIR(event, annotation_df)
                    transition_name = widgetIR + '#' + action
                    linear_model.append({'state': current_screenIR, 'transition': transition_name})
                self.execute_event(event)
        annotation_df.to_csv(dynamic_annotation_file, index=False)
        with open(test_file.replace('.pickle', '-linear.json'), 'w') as output:
            json.dump(linear_model, output)

    def extract_state(self, output_dir):
        layout = LayoutTree.LayoutTree(self.driver, output_dir)
        activity = self.driver.current_activity
        curr_state = layout.extract_state()
        curr_state.set_activity(activity)
        for element in curr_state.nodes:
            if element.interactable:
                if 'content-desc' in element.attributes.keys():
                    element.add_data('content-desc', element.attributes['content-desc'])
                    element.add_exec_identifier('accessibility-id', element.attributes['content-desc'])

                if 'id' in element.attributes.keys():
                    element.add_data('id', element.attributes['id'])
                    element.add_exec_identifier('id', element.attributes['id'])

                if 'resource-id' in element.attributes.keys():
                    element.add_data('resource-id', element.attributes['resource-id'])
                    element.add_exec_identifier('resource-id', element.attributes['resource-id'])

                if 'text' in element.attributes.keys():
                    element.add_data('text', element.attributes['text'])


        if not os.path.isdir(os.path.join(output_dir, 'screenshots')):
            os.makedirs(os.path.join(output_dir, 'screenshots'))
        screenshot_path = os.path.join(output_dir, 'screenshots', str(self.test_num) + '-' + str(self.screenshot_idx) + '.png')
        self.driver.save_screenshot(screenshot_path)
        xml_path = os.path.join(output_dir, 'screenshots', str(self.test_num) + '-' + str(self.screenshot_idx) + '.xml')
        with open(xml_path, "w") as file:
            file.write(self.driver.page_source)
        curr_state.add_screenshot_path(screenshot_path)
        curr_state.add_UIXML_path(xml_path)
        self.screenshot_idx += 1
        return curr_state


    def execute_swipe(self, direction):
        # Get screen dimensions
        screen_dimensions = self.driver.get_window_size()
        if direction == 'up':
            # Set co-ordinate X according to the element you want to scroll on.
            location_x = screen_dimensions["width"] * 0.5
            # Set co-ordinate start Y and end Y according to the scroll driection up or down
            location_start_y = screen_dimensions["height"] * 0.6
            location_end_y = screen_dimensions["height"] * 0.3
            # Perform vertical scroll gesture using TouchAction API.
            TouchAction(self.driver).press(x=location_x, y=location_start_y).wait(1000)\
                .move_to(x=location_x, y=location_end_y).release().perform()
        if direction == 'down':
            # Set co-ordinate X according to the element you want to scroll on.
            location_x = screen_dimensions["width"] * 0.5
            # Set co-ordinate start Y and end Y according to the scroll driection up or down
            location_start_y = screen_dimensions["height"] * 0.3
            location_end_y = screen_dimensions["height"] * 0.6
            # Perform vertical scroll gesture using TouchAction API.
            TouchAction(self.driver).press(x=location_x, y=location_start_y).wait(1000) \
                .move_to(x=location_x, y=location_end_y).release().perform()
        if direction == 'left':
            # Set co-ordinate start X and end X according
            location_start_x = screen_dimensions["width"] * 0.8
            location_end_x = screen_dimensions["width"] * 0.2
            # Set co-ordinate Y according to the element you want to swipe on.
            location_y = screen_dimensions["height"] * 0.5
            # Perform swipe gesture using TouchAction API.
            TouchAction(self.driver).press(x=location_start_x, y=location_y).wait(1000) \
                .move_to(x=location_end_x, y=location_y).release().perform()
        if direction == 'right':
            # Set co-ordinate start X and end X according
            location_start_x = screen_dimensions["width"] * 0.2
            location_end_x = screen_dimensions["width"] * 0.8
            # Set co-ordinate Y according to the element you want to swipe on.
            location_y = screen_dimensions["height"] * 0.5
            # Perform swipe gesture using TouchAction API.
            TouchAction(self.driver).press(x=location_start_x, y=location_y).wait(1000) \
                .move_to(x=location_end_x, y=location_y).release().perform()

    def execute_event(self, event): # return the name of next state (will end test generation is it's 'end')
        element = None
        alreadyClicked = False
        actions = TouchAction(self.driver)
        print('executing event:', event.exec_id_type, event.exec_id_val, event.action)

        if event.exec_id_type == "accessibility-id":
            time.sleep(1)
            # print(event.exec_id_val)
            element = self.driver.find_element_by_accessibility_id(event.exec_id_val)

        if event.exec_id_type == "xPath":
            time.sleep(1)
            element = self.driver.find_element_by_xpath(event.exec_id_val)

        if event.exec_id_type == "resource-id":
            time.sleep(1)
            element = self.driver.find_element_by_id(event.exec_id_val)

        if 'swipe' in event.action:
            time.sleep(1)
            swipe_direction = event.action.split('-')[1]
            self.execute_swipe(swipe_direction)

        if event.action == 'long':
            time.sleep(1)
            alreadyClicked = True
            actions.long_press(element).release().perform()

        if event.action == "send_keys":
            time.sleep(1)
            element.click()
            alreadyClicked = True
            time.sleep(1)
            element.send_keys(event.text_input)

        if event.action == "send_keys_enter":
            time.sleep(1)
            element.click()
            alreadyClicked = True
            time.sleep(1)
            element.send_keys(event.text_input)
            self.driver.press_keycode(66)

        if not alreadyClicked and event.action == 'click':
            element.click()



if __name__ == "__main__":
    desiredCapabilities = {
        "platformName": "Android",
        "deviceName": "emulator-5554",
        "newCommandTimeout": 10000,
        "appPackage": "com.etsy.android",
        "appActivity": "com.etsy.android.ui.homescreen.HomescreenTabsActivity"
    }
    explorer = Explorer(desiredCapabilities)
    while True:
        direction = input('enter swipe direction')
        time.sleep(5)
        explorer.execute_swipe(direction)
    # explorer.extract_state("example_extraction_output")

