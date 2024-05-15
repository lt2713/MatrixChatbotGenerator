from MatrixChatbotGenerator.structures.question import Question


class Questions:
    def __init__(self, questions=None):
        if questions:
            self.questions = questions
        else:
            self.questions = []

    def add(self, question):
        if isinstance(question, Question) and question.validate():
            self.questions.append(question)

    def get_number_of_questions(self):
        return len(self.questions)

    def print(self):
        for question in self.questions:
            question.print()

    def print_short(self):
        for question in self.questions:
            print('\n')
            question.print_short()
