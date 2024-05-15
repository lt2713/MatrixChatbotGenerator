class Answer:
    def __init__(self, identifier, text, correct):
        self.id = identifier
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
        print(f'id: {self.id}')
        print(f'text: {self.text}')
        print(f'correct: {self.correct}')

    def print_short(self):
        print(self.id + ' ' + self.text + ' ' + self.correct)
