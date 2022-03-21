from transitions import *
from transitions.extensions import GraphMachine

class IR_Model(object):
    def __init__(self, name):
        self.name = name
        self.states = ['start']
        self.machine = GraphMachine(model=self, initial='start', title=name, show_conditions=True, show_state_attributes=True)

    def get_condition_list(self, self_transitions):
        condition_list = []
        existing_conditions = self_transitions[0].conditions
        for condition in existing_conditions:
            condition_list.append(condition.func)  # get the string of the condition, not the condition obj
        return condition_list

    def update_condition_list(self, self_transitions, new_condition_list):
        condition_list = self.get_condition_list(self_transitions)
        for new_condition in new_condition_list:
            if new_condition not in condition_list:
                condition_list.append(new_condition)
        return condition_list

    def add_new_transition(self, trigger, source, dest):
        existing_transitions = self.machine.get_transitions(trigger=trigger, source=source, dest=dest)
        if len(existing_transitions) == 0:
            self.machine.add_transition(trigger=trigger, source=source, dest=dest)
            self.states.append(source)
            self.states.append(dest)

    def add_self_transition(self, state, new_condition_list):
        trigger_list = self.machine.get_triggers(state)
        for trigger in trigger_list:
            if trigger == 'self':  # self loop exists in the usage model
                self_transitions = self.machine.get_transitions('self', state, state)
                condition_list = self.update_condition_list(self_transitions, new_condition_list)
                self.machine.remove_transition('self', state, state)
                self.machine.add_transition(trigger='self', source=state, dest=state, conditions=condition_list)
                self.states.append(state)
                return
        # when self loop doesn't exist or the state doesn't exist
        self.machine.add_transition(trigger='self', source=state, dest=state, conditions=new_condition_list)
        self.states.append(state)


if __name__ == '__main__':
#     transitions = [
#         {'trigger': 'widget1', 'source': 'start', 'dest': 'state1', 'unless': 'aaa'},
#         {'trigger': 'widget2', 'source': 'start', 'dest': 'ICSE',
#          'conditions': ['is_valid', 'is_also_valid']}
#     ]
#     states = [{'name': 'ICSE', 'on_exit': ['resume', 'notify']},
#               {'name': 'final', 'on_enter': 'alert', 'on_exit': 'resume'}]
    model1 = IR_Model('HELLO')
    transition = {'trigger': 'self', 'source': 'start', 'dest': 'aaa', 'conditions': ['con1', 'con2'], 'label': ['label1']}
    model1.machine.add_transitions(transition)
    model1.states.append('aaa')
    model1.states.append('start')
    print(model1.states)
    # conditions = []
    # for cond in model1.machine.get_transitions('self', 'start', 'start')[0].conditions:
    #     conditions.append(cond.func)
    # model1.machine.remove_transition('self', 'start', 'start')
    # conditions.append('333333')
    # model1.machine.add_transition(trigger='self', source='start', dest='start', conditions=conditions)
#     model1.machine.add_state(states)
#     print(model1.machine.get_state('final').name)
    model1.get_graph().draw('my_state_diagram.png', prog='dot')