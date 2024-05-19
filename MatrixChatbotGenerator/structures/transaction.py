import uuid


class Transaction:
    def __init__(self, quiz_name, msg_per_day, file_name=None):
        self.identifier = uuid.uuid4()
        self.quiz_name = quiz_name
        self.msg_per_day = msg_per_day
        if not file_name:
            self.file_name = self.identifier
        else:
            self.file_name = file_name

    def print(self):
        print(f'id: {self.identifier}')
        print(f'quiz name: {self.quiz_name}')
        print(f'messages per day: {self.msg_per_day}')
        print(f'file name: {self.file_name}')
