import uuid
from structures.question import Question


class Quiz:
    def __init__(self, name=None, msg_per_day=None, file_name=None, questions=None, key=None):
        self.identifier = key if key else str(uuid.uuid4())
        self.name = name if name else ' '
        self.msg_per_day = msg_per_day if msg_per_day else 1
        self.file_name = file_name if file_name else self.identifier
        self.questions = questions if questions else []

    def print(self):
        print(f'id: {self.identifier}')
        print(f'quiz name: {self.name}')
        print(f'messages per day: {self.msg_per_day}')
        print(f'file name: {self.file_name}')
        for question in self.questions:
            question.print()

    def add_question(self, question):
        if isinstance(question, Question) and question.validate():
            self.questions.append(question)

    def get_number_of_questions(self):
        return len(self.questions)

    def print_short(self):
        print(f'id {self.identifier} {self.name}')
        for question in self.questions:
            print('\n')
            question.print_short()

