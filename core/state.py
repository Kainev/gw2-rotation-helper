import json


class Sequence(object):
    def __init__(self, name, actions, transitions=None):
        self.name: str = name
        self.actions: list[str] = actions
        self.position = 0

        self.transitions = transitions or []
        self.validate_transitions()

    def on_enter(self, position=0):
        self.position = position

    def add_transition(self, transition):
        self.transitions.append(transition)
        self.validate_transitions()

    def validate_transitions(self):
        pass

    @property
    def action(self):
        try:
            return self.actions[self.position]
        except IndexError:
            return None

    def to_dict(self):
        return {
            'name': self.name,
            'actions': self.actions,
            'transitions': [transition.to_dict() for transition in self.transitions]
        }

    @staticmethod
    def from_dict(data):
        name = data['name']
        actions = data['actions']
        transitions = [Transition.from_dict(t) for t in data.get('transitions', [])]
        return Sequence(name, actions, transitions)


class Rotation(object):
    def __init__(self):
        self._sequences: list[Sequence] = []
        self.current_sequence: Sequence = None

        self._character

    def add_sequence(self, sequence: Sequence):
        self._sequences.append(sequence)

        if not self.current_sequence:
            self.current_sequence = sequence

    def transition(self, event: str or None) -> bool:
        for transition in self.current_sequence.transitions:
            if transition.matches(event):
                self.current_sequence = next((sequence for sequence in self._sequences if sequence.name == transition.to))
                self.current_sequence.on_enter(position=transition.to_position)
                return True

        return False

    def on_control_pressed(self, control: str) -> bool:
        if not self.current_sequence:
            return

        current_action = self.current_sequence.actions[self.current_sequence.position]
        if control == current_action:
            self.current_sequence.position += 1

            if self.current_sequence.position >= len(self.current_sequence.actions):
                self.transition('complete')

            return True

        # Attempt to transition in case of matching action
        return self.transition(control)

    def next(self):
        next_index = (self._sequences.index(self.current_sequence) + 1) % len(self._sequences)
        self.current_sequence = self._sequences[next_index]

    def reset(self):
        self.current_sequence = self._sequences[0]
        self.current_sequence.on_enter(0)

    def reset_sequence(self):
        self.current_sequence.on_enter(0)

    @property
    def action(self):
        try:
            return self.current_sequence.action
        except AttributeError:
            return None

    def to_dict(self):
        return [sequence.to_dict() for sequence in self._sequences]

    @staticmethod
    def from_dict(data):
        sequences = [Sequence.from_dict(seq_data) for seq_data in data]
        state_machine = Rotation()
        state_machine._sequences = sequences
        state_machine.current_sequence = sequences[0]

        return state_machine

    def save_to_file(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.to_dict(), file, indent=4)

    @staticmethod
    def load_from_file(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            return Rotation.from_dict(data)


class Transition(object):
    def __init__(self, to: Sequence, on: str, to_position: int = 0) -> None:
        self.to: Sequence = to
        self.on: str = on

        self.to_position: int = to_position

    def matches(self, event) -> bool:
        return event == self.on

    def to_dict(self):
        return {
            'to': self.to,
            'on': self.on,
            'to_position': self.to_position
        }

    @staticmethod
    def from_dict(data):
        return Transition(data['to'], data['on'], data.get('to_position', 0))
