from structures.question import Question


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

