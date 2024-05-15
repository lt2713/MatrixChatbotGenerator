from classes.user_interface import UserInterface
from structures.questions import Questions
from classes.QTIParser import QTIParser

qti_parser = QTIParser()
questions = qti_parser.get_questions()
questions.print_short()

ui = UserInterface(questions)
ui.loop()


