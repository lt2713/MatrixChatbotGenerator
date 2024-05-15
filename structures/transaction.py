import uuid


class Transaction:
    def __init__(self, course_name, year, chatbot_name, msg_per_day, file_name=None):
        self.identifier = uuid.uuid4()
        self.corse_name = course_name
        self.year = year
        self.chatbot_name = chatbot_name
        self.msg_per_day = msg_per_day
        if not file_name:
            self.file_name = self.identifier
        else:
            self.file_name = file_name

    def print(self):
        print(f'id: {self.identifier}')
        print(f'course name: {self.corse_name}')
        print(f'year: {self.year}')
        print(f'chatbot name: {self.chatbot_name}')
        print(f'messages per day: {self.msg_per_day}')
        print(f'file name: {self.file_name}')
