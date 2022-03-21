import pickle
import os, glob
import time
import json


# usage_model.get_graph().draw('my_state_diagram.png', prog='dot')
# initial_state = usage_model.machine.get_state('start')
# transition1 = usage_model.machine.get_transitions(source='start')
# transition2 = usage_model.machine.get_transitions(source='sign_in')
# aaa = usage_model.machine.get_triggers('sign_in')

def add_new_transition(usage_model, trigger, source, dest):
    existing_transitions = usage_model.machine.get_transitions(trigger=trigger, source=source, dest=dest)
    if len(existing_transitions) == 0:
        usage_model.machine.add_transition(trigger=trigger, source=source, dest=dest)
        usage_model.states.append(source)
        usage_model.states.append(dest)

def get_condition_list(self_transitions):
    condition_list = []
    existing_conditions = self_transitions[0].conditions
    for condition in existing_conditions:
        condition_list.append(condition.func)  # get the string of the condition, not the condition obj
    return condition_list

def update_condition_list(self_transitions, new_condition_list):
    condition_list = get_condition_list(self_transitions)
    for new_condition in new_condition_list:
        if new_condition not in condition_list:
            condition_list.append(new_condition)
    return condition_list

def add_self_transition(usage_model, state, new_condition_list):
    trigger_list = usage_model.machine.get_triggers(state)
    for trigger in trigger_list:
        if trigger == 'self': # self loop exists in the usage model
            self_transitions = usage_model.machine.get_transitions('self', state, state)
            condition_list = update_condition_list(self_transitions, new_condition_list)
            usage_model.machine.remove_transition('self', state, state)
            usage_model.machine.add_transition(trigger='self', source=state, dest=state, conditions=condition_list)
            usage_model.states.append(state)
            return
    # when self loop doesn't exist or the state doesn't exist
    usage_model.machine.add_transition(trigger='self', source=state, dest=state, conditions=new_condition_list)
    usage_model.states.append(state)

# merger ir_model into existing usage model
def add_ir_model(usage_model, ir_model):
    # print('merging', ir_model.name)
    for state in set(ir_model.states): # add out transitions of each state
        if state == 'start':
            initial_transition_list = ir_model.machine.get_transitions(trigger='initial', source='start')
            if len(initial_transition_list) == 1:
                initial_transition = initial_transition_list[0]
                add_new_transition(usage_model, 'initial', 'start', initial_transition.dest)
            else:
                print('first state is more than 1, check', ir_model.name)
        elif state == 'end':
            pass # no out transitions, do nothing
        else:
            new_trigger_list = ir_model.machine.get_triggers(state)
            for new_trigger in new_trigger_list:
                if new_trigger == 'self':
                    new_self_transitions = ir_model.machine.get_transitions('self', state, state)
                    new_condition_list = get_condition_list(new_self_transitions)
                    add_self_transition(usage_model, state=state, new_condition_list=new_condition_list)
                else:
                    new_transitions = ir_model.machine.get_transitions(trigger=new_trigger, source=state)
                    if len(new_transitions) == 1:
                        add_new_transition(usage_model, trigger=new_trigger, source=state, dest=new_transitions[0].dest)
                    else:
                        print('transition is more than 1, check', ir_model.name, state, new_trigger)

def get_appname_from_ir_model_file(ir_model_file):
    appname = ir_model_file.replace('ir_model.pickle', '')
    appname = os.path.basename(os.path.normpath(appname))
    appname = appname.split('-')[0].lower()
    return appname

def get_training_ir_model_list(usage_root_dir, AUTname):
    ir_model_list = []
    for ir_model_file in glob.glob(os.path.join(usage_root_dir, '*', 'ir_model.pickle')):
        appname = get_appname_from_ir_model_file(ir_model_file)
        if appname != AUTname:
            ir_model = pickle.load(open(ir_model_file, 'rb'))
            ir_model_list.append(ir_model)
    return ir_model_list

def merge_ir_models(usage_root_dir, AUTname):
    # pickle_filepath = os.path.join(usage_root_dir, 'ir_models.pickle')
    ir_model_list = get_training_ir_model_list(usage_root_dir, AUTname)
    usage_name = os.path.basename(os.path.normpath(usage_root_dir))
    usage_model = ir_model_list[0] # initialize usage model with the first ir model
    # print('merged ir model', ir_model_list[0].name)
    usage_model.name = usage_name + '-' + AUTname
    i = 1
    while i < len(ir_model_list):
        add_ir_model(usage_model, ir_model_list[i])
        # print('merged ir model', ir_model_list[i].name)
        i += 1
    usage_model.states = list(set(usage_model.states))
    if not os.path.exists(os.path.join('/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/output/models', usage_name)):
        os.makedirs(os.path.join('/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/output/models', usage_name))
    usage_model.get_graph().draw(os.path.join('/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/output/models', usage_name, usage_model.name + '.png'), prog='dot')
    pickle_file_path = os.path.join('/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/output/models', usage_name, 'usage_model-' + AUTname + '.pickle')
    with open(pickle_file_path, 'wb') as file:
        pickle.dump(usage_model, file)

def generating_usage_models(usage_root_dir):
    runtime_per_model_list = []
    app_set = set()
    for file in os.listdir(usage_root_dir):
        file_path = os.path.join(usage_root_dir, file)
        if os.path.isdir(file_path):
            app_name = file.split('-')[0].lower()
            app_set.add(app_name)
    for app_name in app_set:
        print('generating usage model for', app_name, '...')
        start_time = time.time()
        merge_ir_models(usage_root_dir, app_name)
        end_time = time.time()
        runtime_per_model_list.append(end_time - start_time)
    return runtime_per_model_list


def run_usage_model_generation(usage_root_dir):
    runtime_file_path = os.path.join(usage_root_dir, 'runtime_final.json')
    runtime_per_model_list = generating_usage_models(usage_root_dir)

    with open(runtime_file_path, "r") as inputfile:
        runtime = json.load(inputfile)

    runtime['usage_model_generation'] = runtime_per_model_list
    with open(runtime_file_path, 'w') as outfile:
        json.dump(runtime, outfile)


if __name__ == '__main__':
    usage_root_dir = os.path.abspath('/Users/XXX/Documents/Research/UsageTesting/Final-Artifacts/usage_data/1-SignIn')
    # generating_usage_models(usage_root_dir)
    run_usage_model_generation(usage_root_dir)
    print('all done! :)')