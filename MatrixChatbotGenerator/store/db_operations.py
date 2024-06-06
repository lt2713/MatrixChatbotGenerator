from store.models import Base, User, Quiz, Question as DbQuestion, Answer as DbAnswer, Feedback as DbFeedback,  \
    LastQuestion, user_subscribed_to_quiz, user_asked_question
from sqlalchemy import create_engine, exists, func, select
from sqlalchemy.orm import sessionmaker
from store import db_config
from structures.question import Question
from structures.answer import Answer
from structures.feedback import Feedback
from structures.quiz import Transaction
from datetime import datetime, timedelta
from util import utility_functions as util

# Initialize the database connection
engine = create_engine(db_config.Config.get_db_uri())
Session = sessionmaker(bind=engine)
session = Session()

logger = util.create_logger('db_operations')


def add_custom_question_to_db(question, quiz_id):
    """
    Adds a custom question to the database for a specified quiz.

    :param question: The question object to be added.
    :param quiz_id: The ID of the quiz to which the question belongs.
    """
    question_model = question.to_db_model(quiz_id=quiz_id)
    session.add(question_model)
    session.commit()


def add_transaction_as_quiz_to_db(transaction):
    """
    Adds a transaction as a quiz to the database.

    :param transaction: The transaction object to be added as a quiz.
    """
    quiz_model = transaction.to_db_model()
    session.add(quiz_model)
    session.commit()


def quiz_exists(quiz_name):
    """
    Checks if a quiz with the given name exists in the database.

    :param quiz_name: The name of the quiz to check.
    :return: True if the quiz exists, False otherwise.
    """
    return session.query(exists().where(Quiz.name == quiz_name)).scalar()


def get_quiz_id_by_name(quiz_name):
    """
    Retrieves the ID of a quiz given its name.

    :param quiz_name: The name of the quiz.
    :return: The ID of the quiz if found, otherwise None.
    """
    normalized_quiz_name = quiz_name.strip().lower()
    quiz = session.query(Quiz).filter(func.lower(Quiz.name) == normalized_quiz_name).first()
    return quiz.id if quiz else None


def fetch_all_quizzes():
    """
    Fetches all quizzes from the database.

    :return: A list of all quiz objects.
    """
    quizzes = session.query(Quiz).all()
    return quizzes


def user_exists(user_id):
    """
    Checks if a user with the given ID exists in the database.

    :param user_id: The ID of the user to check.
    :return: True if the user exists, False otherwise.
    """
    return session.query(exists().where(User.id == user_id)).scalar()


def create_user(user_id):
    """
    Creates a new user with the given ID if the user does not already exist.

    :param user_id: The ID of the user to create.
    :return: True if the user was created, False otherwise.
    """
    if not user_exists(user_id):
        try:
            user = User(id=user_id)
            session.add(user)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(e)
            return False
    else:
        return False
    return True


def get_subscribed_quizzes(user_id):
    """
    Retrieves all quizzes to which a user is subscribed.

    :param user_id: The ID of the user.
    :return: A list of quizzes the user is subscribed to, or an empty list if there are no subscriptions.
    """
    quizzes = session.query(Quiz).join(user_subscribed_to_quiz).\
        filter(user_subscribed_to_quiz.c.user_id == user_id).all()
    return quizzes if quizzes else []


def get_subscribed_users(quiz_id):
    """
    Retrieves all users which are subscribed to a quiz.

    :param quiz_id: The ID of the quiz.
    :return: A list of users that are subscribed to a Quiz or an empty list.
    """
    users = session.query(User).join(user_subscribed_to_quiz).\
        filter(user_subscribed_to_quiz.c.quiz_id == quiz_id).all()
    return users if users else []


def is_user_subscribed(user_id, quiz_id):
    """
    Checks if a user is subscribed to a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :return: True if the user is subscribed to the quiz, False otherwise.
    """
    return session.query(user_subscribed_to_quiz).filter_by(user_id=user_id, quiz_id=quiz_id).count() > 0

def get_subscribed_room(user_id, quiz_id):
    """
    Gets the room a user subscribed to a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :return: Room Id or None
    """
    subscription = session.query(user_subscribed_to_quiz).filter_by(user_id=user_id, quiz_id=quiz_id).first()
    return subscription.room_id if subscription.room_id else None


def count_subscribed_quizzes(user_id):
    """
    Counts the number of quizzes a user is subscribed to.

    :param user_id: The ID of the user.
    :return: The number of quizzes the user is subscribed to.
    """
    return session.query(user_subscribed_to_quiz).filter_by(user_id=user_id).count()


def get_all_quizzes():
    """
    Counts the number of quizzes a user is subscribed to.

    :param user_id: The ID of the user.
    :return: The number of quizzes the user is subscribed to.
    """
    return session.query(Quiz).all()


def subscribe_user_to_quiz(user_id, quiz_id, room_id):
    """
    Subscribes a user to a quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :param room_id: The ID of the room.
    :return: True if the subscription was successful, False otherwise.
    """
    if not is_user_subscribed(user_id, quiz_id):
        try:
            session.execute(user_subscribed_to_quiz.insert().values(user_id=user_id, quiz_id=quiz_id, room_id=room_id))
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(e)
            return False
    else:
        return False
    return True


def unsubscribe_user_from_quiz(user_id, quiz_id):
    """
    Unsubscribes a user from a quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :return: True if the unsubscription was successful, False otherwise.
    """
    if is_user_subscribed(user_id, quiz_id):
        try:
            session.query(user_subscribed_to_quiz).filter_by(user_id=user_id, quiz_id=quiz_id).delete()
            session.commit()
            reset_quiz_by_id(quiz_id, user_id)
        except Exception as e:
            session.rollback()
            logger.error(e)
            return False
    else:
        return False
    return True


def get_asked_questions(user_id, quiz_id):
    """
    Retrieves all questions asked to a user from a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :return: A list of questions that have been asked to the user from the specified quiz.
    """
    try:
        asked_questions = session.query(DbQuestion).\
            join(user_asked_question, DbQuestion.id == user_asked_question.c.question_id).\
            filter(user_asked_question.c.user_id == user_id, DbQuestion.quiz_id == quiz_id).all()
        return asked_questions
    except Exception as e:
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")
        return []


def get_asked_questions_count_on_date(user_id, quiz_id, date):
    """
    Retrieves the number of questions asked on a specific date to a user from a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :param date: The specific date to count the questions (datetime.date object).
    :return: The number of questions asked on the specified date to the user from the quiz.
    """
    try:
        # Get the start and end datetime for the specified date
        day_start = datetime.combine(date, datetime.min.time())
        day_end = day_start + timedelta(days=1)

        count = session.query(func.count(user_asked_question.c.question_id)).\
            join(DbQuestion, DbQuestion.id == user_asked_question.c.question_id).\
            filter(user_asked_question.c.user_id == user_id,
                   DbQuestion.quiz_id == quiz_id,
                   user_asked_question.c.ts >= day_start,
                   user_asked_question.c.ts < day_end).scalar()
        return count
    except Exception as e:
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")
        return 0


def delete_quiz_by_id(quiz_id):
    """
    Deletes a quiz and all related data by its ID.

    :param quiz_id: The ID of the quiz to delete.
    :return: True if the deletion was successful, False otherwise.
    """
    try:
        quiz = session.query(Quiz).filter_by(id=quiz_id).first()
        if not quiz:
            return

        # Delete all feedback related to the quiz questions
        for question in quiz.questions:
            session.query(DbFeedback).filter_by(question_id=question.id).delete()

        # Delete all answers related to the quiz questions
        for question in quiz.questions:
            session.query(DbAnswer).filter_by(question_id=question.id).delete()

        # Delete all entries from user_asked_question related to the quiz questions
        for question in quiz.questions:
            session.query(user_asked_question).filter_by(question_id=question.id).delete()

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
        logger.error(e)
        return False
    return True


def reset_quiz_by_id(quiz_id, user_id):
    """
    Resets a quiz for a specific user by deleting related entries.

    :param quiz_id: The ID of the quiz to reset.
    :param user_id: The ID of the user for whom to reset the quiz.
    :return: True if the reset was successful, False otherwise.
    """
    try:
        quiz = session.query(Quiz).filter_by(id=quiz_id).first()
        if not quiz:
            return

        # Delete all entries in last_question
        session.query(LastQuestion).filter_by(quiz_id=quiz_id, user_id=user_id).delete()
        # Delete all entries in user_asked_question
        for question in quiz.questions:
            session.query(user_asked_question).filter_by(question_id=question.id, user_id=user_id).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(e)
        return False
    return True


def get_unanswered_question(user_id, quiz_id):
    """
    Retrieves the first unanswered question for a user in a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :return: The first unanswered question object, or None if all questions are answered.
    """
    answered_questions = session.query(user_asked_question).filter_by(user_id=user_id).all()
    answered_ids = {aq.question_id for aq in answered_questions}

    all_questions = session.query(DbQuestion).filter_by(quiz_id=quiz_id).all()

    for question in all_questions:
        if question.id not in answered_ids:
            return question
    return None


def convert_question_model_to_question(db_question):
    """
    Converts a database question model to a Python Question class.

    :param db_question: The database question model to convert.
    :return: A Question object.
    """
    answers = [
        Answer(key=ans.id, identifier=ans.identifier, text=ans.text, correct=ans.is_correct)
        for ans in db_question.answers
    ]
    feedback = [
        Feedback(key=fb.id, identifier=fb.identifier, text=fb.text)
        for fb in db_question.feedback
    ]
    question = Question(
        identifier=db_question.id,
        question_type=db_question.type,
        text=db_question.text,
        answers=answers,
        feedback=feedback,
        key=db_question.id
    )
    return question


def update_last_question(user_id, quiz_id, question_id, room_id, answered=False):
    """
    Updates the last question information for a user in a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :param question_id: The ID of the question.
    :param answered: Boolean indicating whether the question was answered.
    """
    session = Session()
    try:
        last_question = session.query(LastQuestion).filter_by(user_id=user_id, quiz_id=quiz_id).first()
        if last_question:
            last_question.question_id = question_id
            last_question.answered = answered
            last_question.room_id = room_id
            if answered:
                last_question.answered_ts = datetime.now()
            else:
                last_question.asked_ts = datetime.now()
        else:
            last_question = LastQuestion(
                user_id=user_id,
                quiz_id=quiz_id,
                question_id=question_id,
                room_id=room_id,
                answered=answered,
                asked_ts=datetime.now() if not answered else None,
                answered_ts=datetime.now() if answered else None
            )
            session.add(last_question)

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")


def update_user_asked_question(user_id, question_id):
    """
    Updates the user answered question information in the database.

    :param user_id: The ID of the user.
    :param question_id: The ID of the question.
    """
    exists = session.query(user_asked_question).filter_by(user_id=user_id, question_id=question_id).count() > 0
    if not exists:
        stmt = user_asked_question.insert().values(user_id=user_id, question_id=question_id, ts=datetime.now())
        session.execute(stmt)
        session.commit()


def ask_question_to_user(user_id, quiz_id, question_id, room_id):
    """
    Asks a question to a user by updating the last question and answered question records.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :param question_id: The ID of the question.
    :return: True if the operation was successful, False otherwise.
    """
    try:
        update_last_question(user_id, quiz_id, question_id, room_id)
        update_user_asked_question(user_id, question_id)
    except Exception as e:
        session.rollback()
        logger.error(e)
        return False
    return True


def get_open_question(user_id, quiz_id=None, room_id=None, is_answered=None):
    """
    Retrieves the open question for a user in a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz (optional).
    :param is_answered: Boolean indicating whether to check if the question is answered (optional).
    :return: The open question object, or None if no open question is found. When is_answered it returns a boolean.
    """
    try:
        if quiz_id and room_id:
            open_question = session.query(LastQuestion).filter_by(user_id=user_id,
                                                                  quiz_id=quiz_id,
                                                                  room_id=room_id,
                                                                  answered=False).first()
        elif quiz_id:
            open_question = session.query(LastQuestion).filter_by(user_id=user_id,
                                                                  quiz_id=quiz_id,
                                                                  answered=False).first()
        elif room_id:
            open_question = session.query(LastQuestion).filter_by(user_id=user_id,
                                                                  room_id=room_id,
                                                                  answered=False).first()
        else:
            open_question = session.query(LastQuestion).filter_by(user_id=user_id,
                                                                  answered=False).first()
        if not open_question:
            return None
        if is_answered:
            return not open_question.answered
        question = session.query(DbQuestion).filter_by(id=open_question.question_id).first()
        return question if question else None
    except Exception as e:
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")
        return None


def has_open_question(user_id, quiz_id=None, room_id=None):
    """
    Checks if a user has an open question in a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz (optional).
    :return: True if there is an open question, False otherwise.
    """
    return get_open_question(user_id, quiz_id, room_id, True)


def get_model_answer(question_id):
    """
    Retrieves the model answer for a specific question.

    :param question_id: The ID of the question.
    :return: The model answer object, or None if no model answer is found.
    """
    try:
        model_answer = session.query(DbFeedback).filter_by(question_id=question_id, identifier='Model').first()
        return model_answer
    except Exception as e:
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")
        return None


def get_feedback(question_id, correct=False):
    """
    Retrieves feedback for a specific question based on whether the answer was correct.

    :param question_id: The ID of the question.
    :param correct: Boolean indicating whether the feedback is for a correct answer.
    :return: The feedback object, or None if no feedback is found.
    """
    try:
        identifier = 'Correct' if correct else 'InCorrect'
        feedback = session.query(DbFeedback).filter_by(question_id=question_id, identifier=identifier).first()
        if not feedback:
            feedback = session.query(DbFeedback).filter_by(question_id=question_id, identifier='FEEDBACK').first()
        return feedback if feedback else None
    except Exception as e:
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")
        return None


def get_all_answers_for_question(question_id):
    """
    Retrieves all answers for a specific question.

    :param question_id: The ID of the question.
    :return: A list of answer objects, or an empty list if no answers are found.
    """
    try:
        answers = session.query(DbAnswer).filter_by(question_id=question_id).all()
        return answers
    except Exception as e:
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")
        return []


if __name__ == '__main__':
    pass
