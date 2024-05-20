import uuid
from store.models import Feedback as DbFeedback


class Feedback:
    def __init__(self, identifier, text, key=None):
        self.id = key if key else uuid.uuid4()
        self.identifier = identifier
        self.text = text if text else ' '

    def validate(self):
        return True

    def print(self):
        print(f'id: {self.identifier}')
        print(f'text: {self.text}')

    def print_short(self):
        print(self.identifier + '\t' + self.text)

    def to_db_model(self, question_id):
        return DbFeedback(
            id=self.id,
            identifier=self.identifier,
            text=self.text,
            question_id=question_id
        )
