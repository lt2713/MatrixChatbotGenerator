import uuid
from structures.answer import Answer
from structures.feedback import Feedback
from store.models import Question as DbQuestion


class Question:
    def __init__(self, identifier, question_type, text=None, answers=None, feedback=None, key=None):
        self.id = key if key else str(uuid.uuid4())
        self.identifier = identifier
        self.type = question_type
        self.text = text if text else ' '
        self.answers = [Answer(**ans) if isinstance(ans, dict) else ans for ans in (answers or [])]
        self.feedback = [Feedback(**fb) if isinstance(fb, dict) else fb for fb in (feedback or [])]

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
                if isinstance(answer, Answer):
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

    def to_db_model(self, quiz_id):
        question = DbQuestion(
            id=self.id,
            type=self.type,
            text=self.text,
            quiz_id=quiz_id
        )
        question.answers = [answer.to_db_model(question.id) for answer in self.answers]
        question.feedback = [feedback.to_db_model(question.id) for feedback in self.feedback]
        return question

    @staticmethod
    def valid_types():
        return ['Multiple Choice', 'Multiple Correct', 'Essay Question', 'True - False']

    @staticmethod
    def valid_types_lower():
        return ['multiple choice', 'multiple correct', 'essay question', 'true - false']








