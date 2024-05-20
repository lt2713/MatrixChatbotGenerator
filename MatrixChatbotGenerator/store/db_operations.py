from models import Base, User, Quiz, Question as DbQuestion, Answer, Feedback, LastQuestion
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import db_config
from structures.question import Question


# Initialize the database connection
engine = create_engine(db_config.Config.get_db_uri())
Session = sessionmaker(bind=engine)
session = Session()


def add_custom_question_to_db(question, quiz_id):
    question_model = question.to_db_model(quiz_id=quiz_id)
    session.add(question_model)
    session.commit()


if __name__ == "__main__":
    # Example usage
    custom_question = Question(
        identifier="Q1",
        question_type="multiple_choice",
        text="What is 2 + 2?",
        answers=[
            {"identifier": "A", "text": "3", "correct": False},
            {"identifier": "B", "text": "4", "correct": True}
        ],
        feedback=[
            {"identifier": "A", "text": "Incorrect, 2 + 2 is 4"},
            {"identifier": "B", "text": "Correct, 2 + 2 is 4"}
        ]
    )

    # Assume quiz_id is provided or obtained from somewhere
    quiz_id = "quiz1"
    custom_question.print_short()
    add_custom_question_to_db(custom_question, quiz_id=quiz_id)
