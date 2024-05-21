from structures.questions import Questions
from classes.QTIParser import QTIParser
from structures.transaction import Transaction
from classes.QuizBot import Quizbot
from store.db_operations import *


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
        self.message = ' '

    def start(self):
        if not self.transaction or not self.questions or len(self.questions.questions) == 0:
            self.message = 'Chatbot generation failed! Parameter Error.'
            return False
        if quiz_exists(self.transaction.quiz_name):
            self.message = 'There already is a Quiz with this name. Please use a different Name'
            return False
        try:
            add_transaction_as_quiz_to_db(self.transaction)
            for question in self.questions.questions:
                add_custom_question_to_db(question, self.transaction.identifier)
        except Exception as e:
            self.message = f'Quiz could not be added due to an unexpected Error: {e}'
            return False
        self.message = 'Chatbot generated.'
        return True

    def get_message(self):
        return self.message


if __name__ == '__main__':
    qtiparser = QTIParser('../data/lt_testquiz.xml')
    default_questions = qtiparser.get_questions()
    default_transaction = Transaction('Letos Testquiz', 1, '../data/lt_testquiz.xml')
    cg = ChatbotGenerator(default_transaction, default_questions)
    cg.start()
    print(cg.get_message())

