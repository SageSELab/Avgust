from transitions import *
from transitions.extensions import GraphMachine


class Matter(object):
    def alert(self):
        pass

    def resume(self):
        pass

    def notify(self):
        pass

    def is_valid(self):
        return True

    def is_not_valid(self):
        return False

    def is_also_valid(self):
        return True


extra_args = dict(initial='solid', title='Matter is Fun!',
                  show_conditions=True, show_state_attributes=True)

transitions = [
    { 'trigger': 'melt', 'source': 'solid', 'dest': 'liquid' },
    { 'trigger': 'evaporate', 'source': 'liquid', 'dest': 'gas', 'conditions':'is_valid' },
    { 'trigger': 'sublimate', 'source': 'solid', 'dest': 'gas', 'unless':'is_not_valid' },
    { 'trigger': 'ionize', 'source': 'gas', 'dest': 'plasma',
      'conditions':['is_valid','is_also_valid'] }
]
states=['solid', 'liquid', {'name': 'gas', 'on_exit': ['resume', 'notify']},
        {'name': 'plasma', 'on_enter': 'alert', 'on_exit': 'resume'}]

model = Matter()
machine = GraphMachine(model=model, states=states, transitions=transitions,
                       show_auto_transitions=True, **extra_args)
machine.add_state('aaa')
# model.machine.add_state('aaa')
model.get_graph().draw('my_state_diagram.png', prog='dot')
