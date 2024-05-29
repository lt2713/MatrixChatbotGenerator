import requests
from requests.auth import HTTPBasicAuth

from classes.ConfigManager import ConfigManager
from structures.questions import Questions
from structures.transaction import Transaction
from classes.QTIParser import QTIParser


class ChatbotGenerator:
    def __init__(self, transaction, questions, url=None, user=None, password=None):
        if isinstance(transaction, Transaction):
            self.transaction = transaction
        else:
            self.transaction = None
        if isinstance(questions, Questions):
            self.questions = questions
        else:
            self.questions = None
        self.message = ' '
        self.config = ConfigManager.load_config('Db')

        self.api_url = url if url else self.config['Db']['server']
        self.user = user if user else self.config['Db']['user_id']
        self.password = password if password else ConfigManager.decrypt_password(self.config['Db']['password'])
        self.auth = HTTPBasicAuth(self.user, self.password)

    def start(self):
        if not self.transaction or not self.questions or len(self.questions.questions) == 0:
            self.message = 'Chatbot generation failed! Parameter Error.'
            return False
        if self.quiz_exists(self.transaction.quiz_name):
            self.message = 'There already is a Quiz with this name. Please use a different Name'
            return False
        try:
            quiz_id = self.add_transaction_as_quiz_to_db(self.transaction)
            for question in self.questions.questions:
                self.add_custom_question_to_db(question, quiz_id)
        except Exception as e:
            self.message = f'Quiz could not be added due to an unexpected Error: {e}'
            return False
        self.message = 'Chatbot generated.'
        return True

    def get_message(self):
        return self.message

    def quiz_exists(self, quiz_name):
        response = requests.get(f'{self.api_url}/quizzes/{quiz_name}', auth=self.auth)
        return response.status_code == 200

    def add_transaction_as_quiz_to_db(self, transaction):
        quiz_data = {
            'name': transaction.quiz_name,
            'messages_per_day': transaction.msg_per_day
        }
        response = requests.post(f'{self.api_url}/quizzes', json=quiz_data, auth=self.auth)
        if response.status_code != 201:
            print(response)
            print(response.content)
            raise Exception('Failed to add quiz')
        return response.json()['id']

    def add_custom_question_to_db(self, question, quiz_id):
        question_data = {
            'type': question.type,
            'text': question.text,
            'answers': [{'identifier': ans.identifier, 'text': ans.text, 'is_correct': ans.correct} for ans in
                        question.answers],
            'feedback': [{'identifier': fb.identifier, 'text': fb.text} for fb in question.feedback]
        }
        response = requests.post(f'{self.api_url}/quizzes/{quiz_id}/questions', json=question_data, auth=self.auth)
        if response.status_code != 201:
            raise Exception('Failed to add question')


if __name__ == '__main__':
    qtiparser = QTIParser('./data/lt_testquiz.xml')
    default_questions = qtiparser.get_questions()
    default_transaction = Transaction('Letos Testquiz', 1, './data/lt_testquiz.xml')
    cg = ChatbotGenerator(default_transaction, default_questions)
    cg.start()

