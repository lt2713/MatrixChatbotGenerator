import uuid


class Transaction:
    def __init__(self, quiz_name, msg_per_day, file_name=None, key=None):
        self.identifier = key if key else uuid.uuid4()
        self.quiz_name = quiz_name
        self.msg_per_day = msg_per_day
        self.file_name = file_name if file_name else self.identifier

    def print(self):
        print(f'id: {self.identifier}')
        print(f'quiz name: {self.quiz_name}')
        print(f'messages per day: {self.msg_per_day}')
        print(f'file name: {self.file_name}')
