from structures.questions import Questions
from classes.QTIParser import QTIParser
from structures.transaction import Transaction
from classes.QuizBot import Quizbot
from store.db_operations import *


class ChatbotGenerator:
    def __init__(self, transaction, questions):
        print(transaction)
        print(questions)
        print(type(transaction))
        print(type(questions))
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
        add_transaction_as_quiz_to_db(self.transaction)
        for question in self.questions.questions:
            add_custom_question_to_db(question, self.transaction.identifier)


if __name__ == '__main__':
    qtiparser = QTIParser('lt_testquiz.xml')
    default_questions = qtiparser.get_questions()
    default_transaction = Transaction('Letos Testquiz', 1, 'lt_testquiz.xml')
    cg = ChatbotGenerator(default_transaction, default_questions)
    if cg.start():
        print('Chatbot generated')

