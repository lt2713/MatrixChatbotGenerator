from store.models import Base, User, Quiz as DbQuiz, Question as DbQuestion, Answer as DbAnswer, \
    Feedback as DbFeedback, LastQuestion, user_subscribed_to_quiz, user_asked_question
from sqlalchemy import create_engine, exists, func, select, update
from sqlalchemy.orm import sessionmaker
from store import db_config
from structures.quiz import Quiz
from structures.question import Question
from structures.answer import Answer
from structures.feedback import Feedback
from datetime import datetime, timedelta
from util import utility_functions as util

# Initialize the database connection
engine = create_engine(db_config.Config.get_db_uri())
Session = sessionmaker(bind=engine)
session = Session()

logger = util.create_logger('db_operations')


def convert_quiz_to_db_model(quiz):
    return DbQuiz(
        id=quiz.identifier,
        name=quiz.name,
        messages_per_day=quiz.msg_per_day,
        short_id=0
    )


def convert_feedback_to_db_model(feedback, question_id):
    return DbFeedback(
        id=feedback.id,
        identifier=feedback.identifier,
        text=feedback.text,
        question_id=question_id
    )


def convert_answer_to_db_model(answer, question_id):
    return DbAnswer(
        id=answer.id,
        identifier=answer.identifier,
        text=answer.text,
        is_correct=answer.correct,
        question_id=question_id
    )


def convert_question_to_db_model(question, quiz_id):
    db_question = DbQuestion(
        id=question.id,
        text=question.text,
        quiz_id=quiz_id,
        is_essay=True if question.type == "Essay Question" else False,
        is_multiple_choice=True if question.type != "Essay Question" else False
    )
    db_question.answers = [convert_answer_to_db_model(answer, question.id) for answer in question.answers]
    db_question.feedback = [convert_feedback_to_db_model(feedback, question.id) for feedback in question.feedback]
    return db_question


def add_custom_question_to_db(question, quiz_id):
    """
    Adds a custom question to the database for a specified quiz.

    :param question: The question object to be added.
    :param quiz_id: The ID of the quiz to which the question belongs.
    """
    question_model = convert_question_to_db_model(question, quiz_id)
    session.add(question_model)
    session.commit()


def add_quiz_to_db(quiz=None, quiz_model=None):
    """
    Adds a quiz or a quiz model to the database.

    :param quiz: The quiz object to be added as a quiz.
    :param quiz_model: The quiz_model to be added.
    """
    if quiz and not quiz_model:
        quiz_model = convert_quiz_to_db_model(quiz)
    if not quiz_model:
        return
    max_short_id = session.query(func.max(Quiz.short_id)).scalar()
    if max_short_id is None:
        max_short_id = 0
    quiz_model.short_id = max_short_id + 1
    session.add(quiz_model)
    session.commit()


def add_db_question_to_db(db_question):
    """
    Adds a new question to the database.

    :param db_question: The Question object to be added to the database.
    """
    try:
        session.add(db_question)
        session.commit()
    except Exception as e:
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")


def add_db_answer_to_db(db_answer):
    """
    Adds a new answer to the database.

    :param db_answer: The Answer object to be added to the database.
    """
    try:
        session.add(db_answer)
        session.commit()
    except Exception as e:
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")


def add_db_feedback_to_db(db_feedback):
    """
    Adds new feedback to the database.

    :param db_feedback: The Feedback object to be added to the database.
    """
    try:
        session.add(db_feedback)
        session.commit()
    except Exception as e:
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")


def quiz_exists(quiz_name):
    """
    Checks if a quiz with the given name exists in the database.

    :param quiz_name: The name of the quiz to check.
    :return: True if the quiz exists, False otherwise.
    """
    return session.query(exists().where(Quiz.name == quiz_name)).scalar()


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


def get_quiz_id_by_name(quiz_name):
    """
    Retrieves the ID of a quiz given its name.

    :param quiz_name: The name of the quiz.
    :return: The ID of the quiz if found, otherwise None.
    """
    normalized_quiz_name = quiz_name.strip().lower()
    quiz = session.query(Quiz).filter(func.lower(Quiz.name) == normalized_quiz_name).first()
    return quiz.id if quiz else None


def get_quiz_id_by_short_id(short_id):
    """
    Retrieves the ID of a quiz given its short ID.

    :param short_id: The short ID of the quiz.
    :return: The ID of the quiz if found, otherwise None.
    """
    quiz = session.query(Quiz).filter(Quiz.short_id == short_id).first()
    return quiz.id if quiz else None


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


def get_subscribed_room(user_id, quiz_id):
    """
    Gets the room a user subscribed to a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :return: Room Id or None
    """
    subscription = session.query(user_subscribed_to_quiz).filter_by(user_id=user_id, quiz_id=quiz_id).first()
    return subscription.room_id if subscription.room_id else None


def get_quiz_by_id(quiz_id):
    """
    Returns the quiz object for an id.
    :param quiz_id: The ID of the quiz.
    :return: quiz
    """
    return session.query(Quiz).filter_by(id=quiz_id).first()


def get_subscription(quiz_id, user_id):
    """
    Returns the subscription for a quiz and user.
    :param quiz_id: The ID of the quiz.
    :param user_id: The ID of the user.
    :return: subscription
    """
    return session.query(user_subscribed_to_quiz).filter_by(quiz_id=quiz_id, user_id=user_id).first()


def get_messages_per_day(quiz_id, user_id):
    """
    Returns the messages per day to be sent for a quiz and user.
    :param quiz_id: The ID of the quiz.
    :param user_id: The ID of the user.
    :return: Messages per day
    """
    subscription = get_subscription(quiz_id, user_id)
    messages_per_day = subscription.messages_per_day if subscription else 0
    return messages_per_day


def get_all_quizzes():
    """
    Returns all quizzes

    :return: The list of all quizzes
    """
    return session.query(Quiz).all()


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


def get_all_questions_for_quiz(quiz_id):
    """
    Retrieves all questions for a specific quiz identified by quiz_id.

    :param quiz_id: The unique identifier of the quiz.
    :return: A list of Question objects associated with the specified quiz. Returns an empty list if an error occurs.
    """
    try:
        questions = session.query(Question).filter_by(quiz_id=quiz_id).all()
        return questions
    except Exception as e:
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")
        return []


def count_subscribed_quizzes(user_id):
    """
    Counts the number of quizzes a user is subscribed to.

    :param user_id: The ID of the user.
    :return: The number of quizzes the user is subscribed to.
    """
    return session.query(user_subscribed_to_quiz).filter_by(user_id=user_id).count()


def count_subscribers(quiz_id):
    """
    Counts the number of users subscribed to a quiz.

    :param quiz_id: The ID of the quiz.
    :return: The number of users subscribed to a quiz.
    """
    return session.query(user_subscribed_to_quiz).filter_by(quiz_id=quiz_id).count()


def count_questions(quiz_id):
    """
    Counts the number of questions of a quiz.

    :param quiz_id: The ID of the quiz.
    :return: The number of questions of a quiz
    """
    return session.query(DbQuestion).filter_by(quiz_id=quiz_id).count()


def update_messages_per_day(user_id, quiz_id, messages_per_day):
    """
    Updates the messages per day field for a subscription.
    :param user_id: The Id of the user.
    :param quiz_id: The Id of the quiz.
    :param messages_per_day: Number of messages to be sent per day
    :return: True if updated, False if not updated
    """
    session = Session()
    try:
        stmt = (
            update(user_subscribed_to_quiz).
            where(user_subscribed_to_quiz.c.user_id == user_id).
            where(user_subscribed_to_quiz.c.quiz_id == quiz_id).
            values(messages_per_day=messages_per_day)
        )

        # Execute the update statement
        result = session.execute(stmt)
        session.commit()

        # Check if any row was updated
        if result.rowcount > 0:
            return True
        else:
            return False

    except Exception as e:
        session.rollback()
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")
        return False


def update_quiz_attributes(quiz_id, name, messages_per_day):
    """
    Updates the name and messages_per_day attributes of a quiz identified by quiz_id.

    :param quiz_id: The unique identifier of the quiz to update.
    :param name: The new name for the quiz.
    :param messages_per_day: The new number of messages per day for the quiz.
    :return: True if the quiz was successfully updated, False otherwise.
    """
    session = Session()
    try:
        quiz = session.query(Quiz).filter_by(id=quiz_id).first()
        if quiz:
            quiz.name = name
            quiz.messages_per_day = messages_per_day
            session.commit()
            return True
        else:
            return False

    except Exception as e:
        session.rollback()
        logger.error(f"An error occurred in {util.current_function_name()}: {e}")
        return False


def update_last_question(user_id, quiz_id, question_id, room_id, answered=False):
    """
    Updates the last question information for a user in a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :param question_id: The ID of the question.
    :param room_id: The ID of the room.
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


def is_user_subscribed(user_id, quiz_id):
    """
    Checks if a user is subscribed to a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz.
    :return: True if the user is subscribed to the quiz, False otherwise.
    """
    return session.query(user_subscribed_to_quiz).filter_by(user_id=user_id, quiz_id=quiz_id).count() > 0


def has_open_question(user_id, quiz_id=None, room_id=None):
    """
    Checks if a user has an open question in a specific quiz.

    :param user_id: The ID of the user.
    :param quiz_id: The ID of the quiz (optional).
    :param room_id: The ID of the room.
    :return: True if there is an open question, False otherwise.
    """
    return get_open_question(user_id, quiz_id, room_id, True)


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
            quiz = get_quiz_by_id(quiz_id)
            messages_per_day = quiz.messages_per_day
            session.execute(user_subscribed_to_quiz.insert().values(user_id=user_id, quiz_id=quiz_id, room_id=room_id,
                                                                    messages_per_day=messages_per_day))
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
        question_type="Essay Question" if db_question.is_essay else "Multiple Choice",
        text=db_question.text,
        answers=answers,
        feedback=feedback,
        key=db_question.id
    )
    return question


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


if __name__ == '__main__':
    pass
