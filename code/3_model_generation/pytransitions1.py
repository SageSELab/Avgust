from transitions.extensions import MachineFactory
from transitions.extensions.states import add_state_features, Tags, Timeout
from transitions import Machine

diagram_class = MachineFactory.get_predefined(graph=True)

@add_state_features(Tags, Timeout)
class CustomStateMachine(Machine):
    pass

class NarcolepticSuperhero(object):
    states = ['asleep']
    # states = ['asleep', {'name': 'myname', 'tags': ['tag1', 'tag2']}]

    def __init__(self, name):
        self.name = name
        self.machine = diagram_class(model=self, states=NarcolepticSuperhero.states, initial='asleep', title=name)
        # self.machine = CustomStateMachine(model=self, states=NarcolepticSuperhero.states, initial='asleep')
if __name__ == "__main__":
    batman = NarcolepticSuperhero("Batman")
    # batman.machine.add_state('awake!')
    batman.machine.add_transition('yay', 'asleep', 'awake!')
    batman.machine.add_transition('yay2', 'awake!', 'asleep')
    batman.machine.add_transition('self', 'asleep', 'asleep')
    triggers = batman.machine.get_triggers('asleep')
    batman.get_graph().draw('my_state_diagram.png', prog='dot')
    # print(batman.machine.get_state('myname').tags)