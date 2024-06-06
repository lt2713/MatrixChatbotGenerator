import xml.etree.ElementTree as ET
from structures.quiz import Quiz
from structures.question import Question
from structures.answer import Answer
from structures.feedback import Feedback
from util import utility_functions as util

logger = util.create_logger('QTIParser')


class QTIParser:
    def __init__(self, file=None):
        if not file:
            self.file = './data/lt_testquiz.xml'
        else:
            self.file = file
        self.quiz = Quiz()
        self.valid_question_types = Question.valid_types()
        self.valid_question_types_lower = Question.valid_types_lower()
        self.tree = self.build_tree()
        if self.tree:
            questions_found = self.find_questions()
            for question in questions_found:
                self.quiz.add_question(question)

    def build_tree(self):
        try:
            tree = ET.parse(self.file)
            return tree.getroot()
        except Exception as e:
            logger.error(f'An unexpected error occurred while trying to read the file:{e}')
            return None

    def find_questions(self):
        questions = []
        for item in self.tree.findall('.//item'):
            try:
                question = self.find_question(questions, item)
            except Exception as e:
                logger.error(f'An unexpected error occurred while trying to read a question:{e}')
                question = None
            if question:
                questions.append(question)
        return questions

    def find_question(self, question, item):
        # Extract relevant information from the item element
        question_id = item.get('ident')
        question_type = item.get('title')
        if question_type.lower() not in self.valid_question_types_lower:
            logger.error('Question type ' + question_type + ' not supported!')
            return None
        try:
            question_text = item.find('.//presentation/flow/material/mattext').text.strip()
        except Exception as e:
            question_text = item.find('.//presentation/material/mattext').text.strip()
        if not question_text:
            logger.error('Could not find Question Text')
            return None
        question = Question(question_id, question_type, question_text)
        question.answers = self.find_answers(item, question)
        if question.type == 'Essay Question':
            self.find_model_answer(item, question)
        else:
            self.find_feedbacks(item, question)
        return question

    def find_answers(self, item, question):
        answers = []
        for answer in item.findall('.//response_label'):
            try:
                new_answer = self.find_answer(item, answer, question)
            except Exception as e:
                logger.error(f'An unexpected error occurred while trying to read an answer:{e} '
                             f'question: {question.id} {question.text}')
                new_answer = None
            if new_answer:
                answers.append(new_answer)
        return answers

    def find_answer(self, item, answer, question):
        mattext_element = answer.find('.//mattext')
        ident = answer.get('ident')
        if mattext_element is not None:
            answer_text = mattext_element.text
            if answer_text is not None:
                found_equal = False
                other_text = None
                for respcondition in item.findall('.//respcondition'):
                    conditionvar_element = respcondition.find('.//conditionvar')
                    other_element = conditionvar_element.find('.//other')
                    if other_element is not None:
                        other_text = respcondition.get('title')
                    for varequal_element in respcondition.findall('.//varequal'):
                        if varequal_element is not None and varequal_element.text == ident:
                            found_equal = True
                            try:
                                linkrefid = respcondition.find('.//displayfeedback[@feedbacktype="Response"]').get(
                                    'linkrefid')
                            except Exception as e:
                                linkrefid = respcondition.get('title')
                            if not linkrefid:
                                logger.error(f'Could not determine if answer is correct. {question.id} {question.text} '
                                             f'{answer_text}')

                            if linkrefid.lower() == 'correct':
                                answer_true = True
                            else:
                                answer_true = False
                            new_answer = Answer(ident, answer_text, answer_true)
                            return new_answer
                if not found_equal and other_text:
                    if other_text.lower() == 'correct':
                        answer_true = True
                    else:
                        answer_true = False
                    new_answer = Answer(ident, answer_text, answer_true)
                    return new_answer

        else:
            logger.error(f"No text found for answer for question {question.id + ' ' + question.text}")

    def find_model_answer(self, item, question):
        model_answer = item.find('.//response_label/material/mattext')
        if not model_answer:
            model_answer = item.find('.//itemfeedback/solution/solutionmaterial/mattext')
        if model_answer is not None:
            text = model_answer.text
            feedback = Feedback('Model', text)
            question.feedback.append(feedback)
        logger.error(f'Could not find Model Answer for question {question.id} {question.text}')

    def find_feedbacks(self, item, question):
        for itemfeedback in item.findall('.//itemfeedback'):
            try:
                feedback = self.find_feedback(itemfeedback)
            except Exception as e:
                logger.error(f'An unexpected error occurred while trying to read feedback:{e}'
                             f'question: {question.id} {question.text}')
                feedback = None
            if feedback:
                question.feedback.append(feedback)

    def find_feedback(self, itemfeedback):
        # Get the ident attribute value
        ident = itemfeedback.get('ident')
        if ident.lower() == 'correct' or ident.lower() == 'incorrect' or ident.lower() == 'feedback':
            # Find the mattext element within the itemfeedback element
            mattext_element = itemfeedback.find('.//mattext')
            text_content = mattext_element.text
            if text_content is not None:
                return Feedback(ident, text_content)

    def get_questions(self):
        return self.quiz.questions
