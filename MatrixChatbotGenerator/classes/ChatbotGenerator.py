from util.http_handler import HttpHandler
from structures.quiz import Quiz


class ChatbotGenerator:
    def __init__(self, quiz, url=None, user=None, password=None):
        if isinstance(quiz, Quiz):
            self.quiz = quiz
        else:
            self.quiz = None
        self.message = ' '
        self.hh = HttpHandler(url if url else None, user if user else None, password if password else None)

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
        quizzes = self.hh.get('/quizzes/')
        for quiz in quizzes:
            if quiz['name'] == quiz_name:
                return True
        return False

    def add_quiz_to_db(self, quiz):
        quiz_data = {
            'name': quiz.name,
            'messages_per_day': quiz.msg_per_day
        }
        response = self.hh.post('/quizzes', quiz_data)
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
        response = self.hh.post(f'/quizzes/{quiz_id}/questions', question_data)
        if response.status_code != 201:
            raise Exception('Failed to add question')

