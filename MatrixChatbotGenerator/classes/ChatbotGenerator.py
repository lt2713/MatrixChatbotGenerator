import requests
from requests.auth import HTTPBasicAuth

from classes.ConfigManager import ConfigManager
from structures.quiz import Quiz


class ChatbotGenerator:
    def __init__(self, quiz, url=None, user=None, password=None):
        if isinstance(quiz, Quiz):
            self.quiz = quiz
        else:
            self.quiz = None
        self.message = ' '
        cm = ConfigManager()
        self.config = cm.load_config('Db')

        self.api_url = url if url else self.config['Db']['server']
        self.user = user if user else self.config['Db']['user_id']
        self.password = password if password else ConfigManager.decrypt_password(self.config['Db']['password'])
        self.auth = HTTPBasicAuth(self.user, self.password)

    def start(self, progress_callback=None):
        if not self.quiz or len(self.quiz.questions) == 0:
            self.message = 'Chatbot generation failed! Parameter Error.'
            return False
        if self.quiz_exists(self.quiz.name):
            self.message = 'There already is a Quiz with this name. Please use a different Name'
            return False
        try:
            if progress_callback:
                progress_callback(0)
            quiz_id = self.add_quiz_to_db(self.quiz)
            if progress_callback:
                progress_callback(10)
            total_questions = len(self.quiz.questions)
            for i, question in enumerate(self.quiz.questions, 1):
                self.add_custom_question_to_db(question, quiz_id)
                if progress_callback:
                    progress_callback(10 + (i * 100 / total_questions))
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

    def add_quiz_to_db(self, quiz):
        quiz_data = {
            'name': quiz.name,
            'messages_per_day': quiz.msg_per_day
        }
        response = requests.post(f'{self.api_url}/quizzes', json=quiz_data, auth=self.auth)
        if response.status_code != 201:
            print(response)
            print(response.content)
            raise Exception('Failed to add quiz')
        return response.json()['id']

    def add_custom_question_to_db(self, question, quiz_id):
        question_data = {
            'text': question.text,
            'is_essay': True if question.type == "Essay Question" else False,
            'is_multiple_choice': True if question.type != "Essay Question" else False,
            'answers': [{'identifier': ans.identifier, 'text': ans.text, 'is_correct': ans.correct} for ans in
                        question.answers],
            'feedback': [{'identifier': fb.identifier, 'text': fb.text} for fb in question.feedback]
        }
        response = requests.post(f'{self.api_url}/quizzes/{quiz_id}/questions', json=question_data, auth=self.auth)
        if response.status_code != 201:
            raise Exception('Failed to add question')

