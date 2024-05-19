from MatrixChatbotGenerator.classes.UserInterface import UserInterface
from MatrixChatbotGenerator.classes.QTIParser import QTIParser

qti_parser = QTIParser()
questions = qti_parser.get_questions()
# questions.print_short()

ui = UserInterface(questions)
ui.loop()

