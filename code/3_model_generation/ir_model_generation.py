import os, glob

import PIL
import pandas as pd
import pickle
import psutil
import json
from entities import IR_Model
import time

### input parameters to change ###
CLICK_ACTION = 'click'
LONG_TAP_ACTION = 'long'
# usage_root_dir = os.path.abspath('/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples')
input_dir = 'steps_clean'
screen_widget_dir = 'ir_data_auto'
input_time = 0
### end input parameters ###

def get_action_from_step(filename_abspath):
    if LONG_TAP_ACTION in os.path.basename(filename_abspath):
        return LONG_TAP_ACTION
    elif 'swipe' in os.path.basename(filename_abspath):
        filename_array = str(os.path.basename(filename_abspath)).split('-')
        # print(filename_array)
        return filename_array[3].replace('.jpg', '')
    else:
        return CLICK_ACTION

# def get_screenIR_from_step_LS(app_root_dir, step_image_file_abspath, usage_root_dir):
#     annotation_file = os.path.join(usage_root_dir, 'LS-annotations.csv')
#     appname = os.path.basename(os.path.normpath(app_root_dir))
#     screen = appname + '-' + os.path.basename(step_image_file_abspath).replace('.jpg', '-screen.jpg')
#     if 'long' in screen:
#         screen = screen.replace('-long', '')
#     df = pd.read_csv(annotation_file)
#     row_found = df.loc[df['screen'].str.contains(screen)]
#     if len(row_found) == 0:
#         image = PIL.Image.open(os.path.join(app_root_dir, screen_widget_dir, screen))
#         image.show()
#         user_input = input('please enter screen IR manually for ' + screen + '\n')
#         return user_input
#     elif len(row_found) == 1:
#         if pd.isna(row_found['tag_screen'].values[0]):
#             image = PIL.Image.open(os.path.join(app_root_dir, screen_widget_dir, screen))
#             image.show()
#             user_input = input('please enter screen IR manually for ' + screen + '\n')
#             return user_input
#         return row_found['tag_screen'].values[0]
#     else:
#         raise ValueError('row found is > 1 when getting screenIR, check', screen)

def get_screenIR_from_step_LS_merged(app_root_dir, step_image_file_abspath):
    annotation_file = '/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/final_labels/final_labels_all.csv'
    appname = os.path.basename(os.path.normpath(app_root_dir))
    screen = appname + '-' + os.path.basename(step_image_file_abspath).replace('.jpg', '-screen.jpg')
    if 'long' in screen:
        screen = screen.replace('-long', '')
    df = pd.read_csv(annotation_file)
    row_found = df.loc[df['screen'].str.contains(screen)]
    if len(row_found) == 0:
        image = PIL.Image.open(os.path.join(app_root_dir, screen_widget_dir, screen))
        image.show()
        user_input = input('please enter screen IR manually for ' + screen + '\n')
        return user_input
    elif len(row_found) == 1:
        if pd.isna(row_found['tag_screen'].values[0]):
            image = PIL.Image.open(os.path.join(app_root_dir, screen_widget_dir, screen))
            image.show()
            user_input = input('please enter screen IR manually for ' + screen + '\n')
            return user_input
        return row_found['tag_screen'].values[0]
    else:
        raise ValueError('row found is > 1 when getting screenIR, check', screen)


# def get_widgetIR_from_step_LS(app_root_dir, step_image_file_abspath, usage_root_dir):
#     annotation_file = os.path.join(usage_root_dir, 'LS-annotations.csv')
#     appname = os.path.basename(os.path.normpath(app_root_dir))
#     widget = appname + '-' + os.path.basename(step_image_file_abspath).replace('.jpg', '-widget.jpg')
#     if 'long' in widget:
#         widget = widget.replace('-long', '')
#     df = pd.read_csv(annotation_file)
#     row_found = df.loc[df['widget'].str.contains(widget)]
#     if len(row_found) == 0:
#         image = PIL.Image.open(step_image_file_abspath)
#         image.show()
#         user_input = input('please enter widget IR manually for widget ' + widget + '\n')
#         return user_input
#     elif len(row_found) == 1:
#         if pd.isna(row_found['tag_widget'].values[0]):
#             image = PIL.Image.open(step_image_file_abspath)
#             image.show()
#             user_input = input('please enter widget IR manually for widget ' + widget + '\n')
#             return user_input
#         return row_found['tag_widget'].values[0]
#     else:
#         raise ValueError('row found is > 1 when getting widgetIR, check', widget)


def get_widgetIR_from_step_LS_merged(app_root_dir, step_image_file_abspath):
    annotation_file = '/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/final_labels/final_labels_all.csv'
    appname = os.path.basename(os.path.normpath(app_root_dir))
    widget = appname + '-' + os.path.basename(step_image_file_abspath).replace('.jpg', '-widget.jpg')
    if 'long' in widget:
        widget = widget.replace('-long', '')
    df = pd.read_csv(annotation_file)
    row_found = df.loc[df['widget'].str.contains(widget)]
    if len(row_found) == 0:
        image = PIL.Image.open(step_image_file_abspath)
        image.show()
        user_input = input('please enter widget IR manually for widget ' + widget + '\n')
        return user_input
    elif len(row_found) == 1:
        if pd.isna(row_found['tag_widget'].values[0]) or row_found['tag_widget'].values[0] == 'N/A':
            image = PIL.Image.open(step_image_file_abspath)
            image.show()
            user_input = input('please enter widget IR manually for widget ' + widget + '\n')
            return user_input
        return row_found['tag_widget'].values[0]
    else:
        raise ValueError('row found is > 1 when getting widgetIR, check', widget)

'''
if the action is click or long, return 'widgetIR#action'
else (it's swipe), return only the action, e.g., 'up'
'''
def get_transition_name(app_root_dir, step_image_file_abspath):
    action = get_action_from_step(step_image_file_abspath)
    if action == CLICK_ACTION or action == LONG_TAP_ACTION:
        widgetIR = get_widgetIR_from_step_LS_merged(app_root_dir, step_image_file_abspath)
        if pd.isna(widgetIR):
            image = PIL.Image.open(step_image_file_abspath)
            image.show()
            user_input = input('please enter widget IR manually for widget ' + os.path.basename(step_image_file_abspath) + '\n')
            widgetIR = user_input
        return widgetIR + '#' + action
    else:
        return action

def handle_self_loop(ir_model, screenIR, transition_name):
    self_transitions = ir_model.machine.get_transitions('self', screenIR, screenIR)
    if len(self_transitions) == 0:
        new_self_transition = {'trigger': 'self', 'source': screenIR, 'dest': screenIR,
                               'conditions': [transition_name]}
        ir_model.machine.add_transitions(new_self_transition)
        ir_model.states.append(screenIR)
    elif len(self_transitions) == 1:
        condition_list = []
        existing_conditions = self_transitions[0].conditions
        for condition in existing_conditions:
            condition_list.append(condition.func) # get the string of the condition, not the condition obj
        if transition_name not in condition_list:
            condition_list.append(transition_name)
        ir_model.machine.remove_transition('self', screenIR, screenIR)
        ir_model.machine.add_transition(trigger='self', source=screenIR, dest=screenIR, conditions=condition_list)
        ir_model.states.append(screenIR)
    else:
        print('self transition > 1, check transition (self, ', screenIR, ')')
    return ir_model

def get_noswiping_previous_screenIR(app_root_dir, step_list, i, usage_root_dir):
    action = get_action_from_step(step_list[i-1])
    if action == CLICK_ACTION or action == LONG_TAP_ACTION:
        return get_screenIR_from_step_LS_merged(app_root_dir, step_list[i-1])
    else:
        while not (action == CLICK_ACTION or action == LONG_TAP_ACTION):
            i = i - 1
            action = get_action_from_step(step_list[i])
        return get_screenIR_from_step_LS_merged(app_root_dir, step_list[i])


def add_transition_buffer(transition_buffer, ir_model, app_root_dir, step_list, i, screenIR, usage_root_dir):
    # print('transition buffer should have widget#action first, followed by swipes', transition_buffer)
    # add action to connect with previous screen
    trigger = transition_buffer[0]
    previous_screenIR = get_noswiping_previous_screenIR(app_root_dir, step_list, i, usage_root_dir)
    if previous_screenIR == screenIR:
        handle_self_loop(ir_model, screenIR, trigger)
    else:
        ir_model.machine.add_transition(trigger, previous_screenIR, screenIR)
        ir_model.states.append(previous_screenIR)
        ir_model.states.append(screenIR)
    # add swipes to self transition's conditions
    transition_buffer.pop(0)
    self_transitions = ir_model.machine.get_transitions('self', screenIR, screenIR)
    if len(self_transitions) == 0:
        transition_buffer = list(set(transition_buffer)) # get unique values only
        new_self_transition = {'trigger': 'self', 'source': screenIR, 'dest': screenIR,
                               'conditions': transition_buffer}
        ir_model.machine.add_transitions(new_self_transition)
        ir_model.states.append(screenIR)
    elif len(self_transitions) == 1:
        condition_list = []
        existing_conditions = self_transitions[0].conditions
        for condition in existing_conditions:
            condition_list.append(condition.func)  # get the string of the condition, not the condition obj
        for transition_name in transition_buffer:
            if transition_name not in condition_list:
                condition_list.append(transition_name)
        ir_model.machine.remove_transition('self', screenIR, screenIR)
        ir_model.machine.add_transition(trigger='self', source=screenIR, dest=screenIR, conditions=condition_list)
        ir_model.states.append(screenIR)
    else:
        print('self transition > 1, check transition (self, ', screenIR, ')')
    return ir_model

def build_ir_model(app_root_dir, step_dir, usage_root_dir):
    appname = os.path.basename(os.path.normpath(app_root_dir))
    ir_model = IR_Model(appname)
    step_list = sorted(glob.glob(step_dir + '/' + '*.jpg'))
    transition_buffer = []
    i = 0
    start_time = time.time()
    while i < len(step_list):
        current_action = get_action_from_step(step_list[i])
        if i == 0: # initial step
            # skip swipes in the beginning
            while not (current_action == CLICK_ACTION or current_action == LONG_TAP_ACTION):
                i += 1
                current_action = get_action_from_step(step_list[i])
            if current_action == CLICK_ACTION or current_action == LONG_TAP_ACTION: # only add initial state if the action is NOT swipe
                screenIR = get_screenIR_from_step_LS_merged(app_root_dir, step_list[i])
                ir_model.machine.add_transition('initial', 'start', screenIR)
                ir_model.states.append(screenIR)
                # try:
                #     screenIR_next = get_screenIR_from_step_LS(app_root_dir, step_list[i+1])
                #     if screenIR == screenIR_next: # transit to the same screen, such as typing username
                #         transition_name = get_transition_name(app_root_dir, step_list[i])
                #         ir_model = handle_self_loop(ir_model, screenIR, transition_name)
                #     else:
                #         current_transition = get_transition_name(app_root_dir, step_list[i])
                #         ir_model.machine.add_transition(current_transition, screenIR, screenIR_next)
                # except IndexError:
                #     # current step is the last step
                #     final_transition = get_transition_name(app_root_dir, step_dir[i])
                #     ir_model.machine.add_transition(final_transition, screenIR, 'end')
            else:
                print('initial state is a swipe, check', app_root_dir)
        if i == len(glob.glob(step_dir + '/' + '*.jpg')) - 1: # last step
            if current_action == CLICK_ACTION or current_action == LONG_TAP_ACTION:
                screenIR = get_screenIR_from_step_LS_merged(app_root_dir, step_list[i])
                if len(transition_buffer) != 0:  # add transition buffer to transit to the current screen
                    ir_model = add_transition_buffer(transition_buffer, ir_model, app_root_dir, step_list, i, screenIR, usage_root_dir)
                    transition_buffer.clear()
                final_transition = get_transition_name(app_root_dir, step_list[i])
                ir_model.machine.add_transition(final_transition, screenIR, 'end')
                ir_model.states.append(screenIR)
                ir_model.states.append('end')
            else: # final step is swipe
                screenIR = get_noswiping_previous_screenIR(app_root_dir, step_list, i, usage_root_dir)
                ir_model.machine.add_transition(transition_buffer[0], screenIR, 'end')
                ir_model.states.append(screenIR)
                ir_model.states.append('end')
        else:
            next_action = get_action_from_step(step_list[i+1])
            if current_action == CLICK_ACTION or current_action == LONG_TAP_ACTION:
                screenIR = get_screenIR_from_step_LS_merged(app_root_dir, step_list[i])
                if len(transition_buffer) != 0: # add transition buffer to transit to the current screen
                    ir_model = add_transition_buffer(transition_buffer, ir_model, app_root_dir, step_list, i, screenIR, usage_root_dir)
                    transition_buffer.clear()
                if next_action == CLICK_ACTION or next_action == LONG_TAP_ACTION:
                    screenIR_next = get_screenIR_from_step_LS_merged(app_root_dir, step_list[i+1])
                    if screenIR == screenIR_next:  # transit to the same screen, such as typing username
                        transition_name = get_transition_name(app_root_dir, step_list[i])
                        ir_model = handle_self_loop(ir_model, screenIR, transition_name)
                    else:
                        current_transition = get_transition_name(app_root_dir, step_list[i])
                        ir_model.machine.add_transition(current_transition, screenIR, screenIR_next)
                        ir_model.states.append(screenIR)
                        ir_model.states.append(screenIR_next)
                else: # current action is NOT swipe, next action is swipe
                    if len(transition_buffer) != 0:
                        print('transition buffer is not 0, check', step_list[i])
                    else:
                        transition_buffer.append(get_transition_name(app_root_dir, step_list[i]))
            else: # current action is swipe, then add the swiping direction to the transition buffer (will handle at next non-swipe screen)
                transition_buffer.append(get_transition_name(app_root_dir, step_list[i]))
        i += 1
    end_time = time.time()
    return ir_model, (end_time - start_time)

def generating_ir_models(usage_root_dir):
    # ir_model_list = []
    runtime_per_model_list = []
    for step_dir in glob.glob(usage_root_dir + '/*/' + input_dir):
        app_root_dir = step_dir.replace(input_dir, '') # /Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/6pm-video-signin-3/
        ir_model_path = os.path.join(app_root_dir, 'ir_model.pickle')
        # if os.path.exists(ir_model_path):
        #     print('ir model already existed in', app_root_dir, 'skipping...')
        #     continue
        print('building ir model for', app_root_dir)
        ir_model, runtime = build_ir_model(app_root_dir, step_dir, usage_root_dir)
        runtime_per_model_list.append(runtime)
        ir_model.states = list(set(ir_model.states))
        # ir_model_list.append(ir_model)
        with open(ir_model_path, 'wb') as file:
            pickle.dump(ir_model, file)
        ir_model.get_graph().draw(os.path.join(app_root_dir, ir_model.name + '.png'), prog='dot')
    return runtime_per_model_list
    # ir_model_list_path = os.path.join(usage_root_dir, 'ir_model_list.pickle')
    # with open(ir_model_list_path, 'wb') as file:
        # for ir_model in ir_model_list:
        #     print(ir_model.states)
        # pickle.dump(ir_model_list, file)


def run_ir_model_generation(usage_root_dir):
    runtime_list = generating_ir_models(usage_root_dir)
    runtime = {}
    runtime['ir_model_generation'] = runtime_list
    runtime_file_path = os.path.join(usage_root_dir, 'runtime_final.json')
    with open(runtime_file_path, 'w') as outfile:
        json.dump(runtime, outfile)
    for proc in psutil.process_iter():
        # print(proc.name())
        if proc.name() == 'Preview':
            proc.kill()

if __name__ == '__main__':
    run_ir_model_generation('/Users/XXX/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples')
    print('all done! :)')