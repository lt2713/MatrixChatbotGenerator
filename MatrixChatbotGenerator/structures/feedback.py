class Feedback:
    def __init__(self, identifier, text):
        self.id = identifier
        if text is None:
            self.text = ' '
        else:
            self.text = text

    def validate(self):
        return True

    def print(self):
        print(f'id: {self.id}')
        print(f'text: {self.text}')

    def print_short(self):
        print(self.id + '\t' + self.text)
