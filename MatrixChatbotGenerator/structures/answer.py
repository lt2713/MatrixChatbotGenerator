import uuid


class Answer:
    def __init__(self, identifier, text, correct, key=None):
        self.id = key if key else str(uuid.uuid4())

        self.identifier = self.extract_choice_suffix(identifier)
        self.text = text
        self.correct = correct

    def validate(self):
        # Check Answer Text
        if not isinstance(self.text, str) or not self.text:
            return False
        # Check for correct type
        if not isinstance(self.correct, bool):
            return False
        return True

    def print(self):
        print(f'id: {self.identifier}')
        print(f'text: {self.text}')
        print(f'correct: {self.correct}')

    def print_short(self):
        print(self.identifier + '\t' + self.text + '\t' + str(self.correct))

    def extract_choice_suffix(self, choice_string):
        if choice_string.startswith("CHOICE_") and len(choice_string) == 8:
            return choice_string.split('_')[-1]
        else:
            return choice_string

    def get(self):
        return self.identifier + ') ' + self.text + '\n'
