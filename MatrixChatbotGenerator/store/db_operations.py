from store.models import Base, User, Quiz, Question as DbQuestion, Answer, Feedback, LastQuestion
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


if __name__ == '__main__':
    quizzes = fetch_all_quizzes()
    for quiz in quizzes:
        print(quiz.name)
