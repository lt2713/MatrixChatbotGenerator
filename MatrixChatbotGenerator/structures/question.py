import uuid


class Question:
    def __init__(self, identifier, question_type, text=None, answers=None, feedback=None, key=None):
        self.id = key if key else uuid.uuid4()
        self.identifier = identifier
        self.type = question_type
        self.text = text if text else ' '
        self.answers = answers if answers else []
        self.feedback = feedback if feedback else []

    def validate(self):
        # Check for ID
        if not self.identifier:
            return False
        # Check for Type
        if self.type.lower() not in self.valid_types_lower():
            return False
        # Check for text
        if not self.text or self.text == ' ':
            return False
        # Check if answers and type match
        if self.type == 'Multiple Choice' or self.type == 'Multiple Correct':
            if len(self.answers) < 2:
                return False
            for answer in self.answers:
                if not answer.validate():
                    return False
        if self.type == 'True - False':
            if len(self.answers) != 2:
                return False
            for answer in self.answers:
                if not answer.validate():
                    return False

        if self.type == 'Essay Question':
            if len(self.feedback) == 0:
                return False
            for feedback in self.feedback:
                if not feedback.validate():
                    return False
        return True

    def print(self):
        print(f'Question id: {self.identifier}')
        print(f'type {self.type}')
        print(f'text: {self.text}')
        if len(self.answers) > 0:
            print('Answers:')
            for answer in self.answers:
                answer.print()
        if len(self.feedback) > 0:
            print('Feedback:')
            for feedback in self.feedback:
                feedback.print()

    def print_short(self):
        print('Question ' + self.identifier + '\t' + self.type + '\t' + self.text)
        if len(self.answers) > 0:
            print('Answers:')
            for answer in self.answers:
                answer.print_short()
        if len(self.feedback) > 0:
            print('Feedback:')
            for feedback in self.feedback:
                feedback.print_short()

    def get(self):
        result = self.text + '\n'
        if len(self.answers) > 0:
            for answer in self.answers:
                result = result + answer.get()
        return result

    @staticmethod
    def valid_types():
        return ['Multiple Choice', 'Multiple Correct', 'Essay Question', 'True - False']

    @staticmethod
    def valid_types_lower():
        return ['multiple choice', 'multiple correct', 'essay question', 'true - false']








