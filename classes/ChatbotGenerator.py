from structures.transaction import Transaction
from structures.questions import Questions
from structures.question import Question
from structures.answer import Answer
from structures.feedback import Feedback


class ChatbotGenerator:
    def __init__(self, transaction, questions):
        if isinstance(transaction, Transaction):
            self.transaction = transaction
        else:
            self.transaction = None
        if isinstance(questions, Questions):
            self.questions = questions
        else:
            self.questions = None

    def start(self):
        if not self.transaction or not self.questions:
            print('Chatbot generation failed!')
            return False
        self.transaction.print()
        print(f'Number of questions: {self.questions.get_number_of_questions()}')
        self.questions.print_short()
        return True
