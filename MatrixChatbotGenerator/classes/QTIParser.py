import xml.etree.ElementTree as ET
from MatrixChatbotGenerator.structures.questions import Questions
from MatrixChatbotGenerator.structures.question import Question
from MatrixChatbotGenerator.structures.answer import Answer
from MatrixChatbotGenerator.structures.feedback import Feedback


class QTIParser:
    def __init__(self, file=None):
        if not file:
            self.file = 'lt_testquiz.xml'
        else:
            self.file = file

        self.tree = self.build_tree()
        questions_found = self.find_questions()
        self.questions = Questions()
        for question in questions_found:
            self.questions.add(question)

    def build_tree(self):
        tree = ET.parse(self.file)
        return tree.getroot()

    def find_questions(self):
        valid_question_types = Question.valid_types()
        questions = []
        for item in self.tree.findall('.//item'):
            # Extract relevant information from the item element
            question_id = item.get('ident')
            question_type = item.get('title')
            if question_type not in valid_question_types:
                print('Question type ' + question_type + ' not supported!')
                continue
            question_text = item.find('.//presentation/flow/material/mattext').text.strip()
            question = Question(question_id, question_type, question_text)
            self.find_answers(item, question)
            if question.type == 'Essay Question':
                self.find_model_answer(item, question)
            else:
                self.find_feedback(item, question)
            questions.append(question)
        return questions

    def find_answers(self, item, question):
        for answer in item.findall('.//response_label'):
            mattext_element = answer.find('.//mattext')
            ident = answer.get('ident')
            if mattext_element is not None:
                answer_text = mattext_element.text
                if answer_text is not None:
                    for respcondition in item.findall('.//respcondition'):
                        varequal_element = respcondition.find('.//varequal')
                        if varequal_element is not None and varequal_element.text == ident:
                            linkrefid = respcondition.find('.//displayfeedback[@feedbacktype="Response"]').get(
                                'linkrefid')
                            if linkrefid == 'Correct':
                                answer_true = True
                            else:
                                answer_true = False
                            new_answer = Answer(ident, answer_text, answer_true)
                            question.answers.append(new_answer)
                            break
            else:
                print("No text found for answer")

    def find_model_answer(self, item, question):
        model_answer = item.find('.//response_label/material/mattext').text
        feedback = Feedback('Model', model_answer)
        question.feedback.append(feedback)

    def find_feedback(self, item, question):
        for itemfeedback in item.findall('.//itemfeedback'):
            # Get the ident attribute value
            ident = itemfeedback.get('ident')
            if ident == 'Correct' or ident == 'InCorrect':
                # Find the mattext element within the itemfeedback element
                mattext_element = itemfeedback.find('.//mattext')
                text_content = mattext_element.text
                if text_content is not None:
                    feedback = Feedback(ident, text_content)
                    question.feedback.append(feedback)

    def get_questions(self):
        return self.questions
