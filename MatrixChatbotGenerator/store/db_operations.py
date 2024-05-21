from store.models import Base, User, Quiz, Question as DbQuestion, Answer, Feedback, LastQuestion, \
    user_subscribed_to_quiz, user_answered_question
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from store import db_config
from structures.question import Question
from structures.transaction import Transaction


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
            session.query(Feedback).filter_by(question_id=question.id).delete()

        # Delete all answers related to the quiz questions
        for question in quiz.questions:
            session.query(Answer).filter_by(question_id=question.id).delete()

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


if __name__ == '__main__':
    quizzes = fetch_all_quizzes()
    for quiz in quizzes:
        print(quiz.name)
