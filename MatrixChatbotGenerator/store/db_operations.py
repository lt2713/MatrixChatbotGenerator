from store.models import Base, User, Quiz, Question as DbQuestion, Answer as DbAnswer, Feedback as DbFeedback,  \
    LastQuestion, user_subscribed_to_quiz, user_answered_question
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from store import db_config
from structures.question import Question
from structures.answer import Answer
from structures.feedback import Feedback
from structures.transaction import Transaction
from datetime import datetime


# Initialize the database connection
engine = create_engine(db_config.Config.get_db_uri())
Session = sessionmaker(bind=engine)
session = Session()


def add_custom_question_to_db(question, quiz_id):
    question_model = question.to_db_model(quiz_id=quiz_id)
    session.add(question_model)
    session.commit()


def add_transaction_as_quiz_to_db(transaction):
    quiz_model = transaction.to_db_model()
    session.add(quiz_model)
    session.commit()


def quiz_exists(quiz_name):
    return session.query(exists().where(Quiz.name == quiz_name)).scalar()


def get_quiz_id_by_name(quiz_name):
    quiz = session.query(Quiz).filter_by(name=quiz_name).first()
    return quiz.id if quiz else None


def fetch_all_quizzes():
    # Query the database to get all quizzes
    quizzes = session.query(Quiz).all()
    return quizzes


def user_exists(user_id):
    return session.query(exists().where(User.id == user_id)).scalar()


def create_user(user_id):
    if not user_exists(user_id):
        try:
            user = User(id=user_id)
            session.add(user)
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)
            return False
    else:
        return False
    return True


def get_subscribed_quizzes(user_id):
    quizzes = session.query(Quiz).join(user_subscribed_to_quiz).\
        filter(user_subscribed_to_quiz.c.user_id == user_id).all()
    return [quiz.name for quiz in quizzes]


def is_user_subscribed(user_id, quiz_id):
    return session.query(user_subscribed_to_quiz).filter_by(user_id=user_id, quiz_id=quiz_id).count() > 0


def subscribe_user_to_quiz(user_id, quiz_id):
    if not is_user_subscribed(user_id, quiz_id):
        try:
            session.execute(user_subscribed_to_quiz.insert().values(user_id=user_id, quiz_id=quiz_id))
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)
            return False
    else:
        return False
    return True


def unsubscribe_user_from_quiz(user_id, quiz_id):
    if is_user_subscribed(user_id, quiz_id):
        try:
            session.query(user_subscribed_to_quiz).filter_by(user_id=user_id, quiz_id=quiz_id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)
            return False
    else:
        return False
    return True


def delete_quiz_by_id(quiz_id):
    try:
        quiz = session.query(Quiz).filter_by(id=quiz_id).first()
        if not quiz:
            print(f"No quiz found with ID {quiz_id}")
            return

        # Delete all feedback related to the quiz questions
        for question in quiz.questions:
            session.query(DbFeedback).filter_by(question_id=question.id).delete()

        # Delete all answers related to the quiz questions
        for question in quiz.questions:
            session.query(DbAnswer).filter_by(question_id=question.id).delete()

        # Delete all entries from user_answered_question related to the quiz questions
        for question in quiz.questions:
            session.query(user_answered_question).filter_by(question_id=question.id).delete()

        # Delete all questions related to the quiz
        session.query(DbQuestion).filter_by(quiz_id=quiz_id).delete()

        # Delete all entries from user_subscribed_to_set related to the quiz
        session.query(user_subscribed_to_quiz).filter_by(quiz_id=quiz_id).delete()

        # Delete all entries from last_question related to the quiz
        session.query(LastQuestion).filter_by(quiz_id=quiz_id).delete()

        # Delete the quiz itself
        session.delete(quiz)

        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        return False
    return True


def reset_quiz_by_id(quiz_id, user_id):
    try:
        quiz = session.query(Quiz).filter_by(id=quiz_id).first()
        if not quiz:
            print(f"No quiz found with ID {quiz_id}")
            return

        # Delete all entries in last_question
        session.query(LastQuestion).filter_by(quiz_id=quiz_id, user_id=user_id).delete()
        # Delete all entries in user_answer_question
        for question in quiz.questions:
            session.query(user_answered_question).filter_by(question_id=question.id, user_id=user_id).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        return False
    return True


def get_unanswered_question(user_id, quiz_id):

    subquery = session.query(user_answered_question.c.question_id).filter_by(user_id=user_id).subquery()
    question = session.query(DbQuestion).filter(DbQuestion.quiz_id == quiz_id, ~DbQuestion.id.in_(subquery)).first()
    return question


def convert_question_model_to_question(db_question):
    answers = [
        Answer(key=ans.id, identifier=ans.identifier, text=ans.text, correct=ans.is_correct)
        for ans in db_question.answers
    ]
    feedback = [
        Feedback(key=fb.id, identifier=fb.identifier, text=fb.text)
        for fb in db_question.feedback
    ]
    question = Question(
        identifier=db_question.identifier,
        question_type=db_question.type,
        text=db_question.text,
        answers=answers,
        feedback=feedback,
        key=db_question.id
    )
    return question


def update_last_question(user_id, quiz_id, question_id, answered=False):
    session = Session()
    try:
        last_question = session.query(LastQuestion).filter_by(user_id=user_id, quiz_id=quiz_id,
                                                              question_id=question_id).first()
        if last_question:
            last_question.question_id = question_id
            last_question.answered = answered
            if answered:
                last_question.answered_ts = datetime.now()
            else:
                last_question.asked_ts = datetime.now()
        else:
            last_question = LastQuestion(
                user_id=user_id,
                quiz_id=quiz_id,
                question_id=question_id,
                answered=answered,
                asked_ts=datetime.now() if not answered else None,
                answered_ts=datetime.now() if answered else None
            )
            session.add(last_question)

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"An error occurred in update_last_question: {e}")


def update_user_answered_question(user_id, question_id):
    exists = session.query(user_answered_question).filter_by(user_id=user_id, question_id=question_id).count() > 0
    if not exists:
        stmt = user_answered_question.insert().values(user_id=user_id, question_id=question_id)
        session.execute(stmt)
        session.commit()


def ask_question_to_user(user_id, quiz_id, question_id):
    try:
        update_last_question(user_id, quiz_id, question_id)
        update_user_answered_question(user_id, question_id)
    except Exception as e:
        session.rollback()
        print(e)
        return False
    return True


def get_open_question(user_id, quiz_id=None):
    try:
        open_question = session.query(LastQuestion).filter_by(user_id=user_id).first()
        # if quiz_id:
        #     query = query.filter_by(quiz_id=quiz_id)
        question = session.query(DbQuestion).filter_by(id=open_question.question_id).first()
        return question if question else None
    except Exception as e:
        print(f"An error occurred in get_open_question: {e}")
        return None


def has_open_question(user_id, quiz_id=None):
    return True if get_open_question(user_id, quiz_id) is not None else False


def get_model_answer(question_id):
    try:
        model_answer = session.query(DbFeedback).filter_by(question_id=question_id, identifier='Model').first()
        return model_answer
    except Exception as e:
        print(f"An error occurred in get_model_answer: {e}")
        return None


def get_feedback(question_id, correct=False):
    try:
        identifier = 'Correct' if correct else 'InCorrect'
        feedback = session.query(DbFeedback).filter_by(question_id=question_id, identifier=identifier).first()
        return feedback if feedback else None
    except Exception as e:
        print(f"An error occurred in get_feedback: {e}")
        return None


def get_all_answers_for_question(question_id):
    try:
        answers = session.query(DbAnswer).filter_by(question_id=question_id).all()
        return answers
    except Exception as e:
        print(f"An error occurred in get_all_answers_for_question: {e}")
        return []


if __name__ == '__main__':
    pass
