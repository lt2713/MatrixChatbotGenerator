import uuid
from sqlalchemy import create_engine, Column, String, Boolean, ForeignKey, Table, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from store import db_config

Base = declarative_base()

# Association tables for many-to-many relationships
user_subscribed_to_quiz = Table('user_subscribed_to_quiz', Base.metadata,
                                Column('user_id', String, ForeignKey('user.id')),
                                Column('quiz_id', String, ForeignKey('quiz.id')),
                                Column('room_id', String),
                                Column('messages_per_day', Integer)
                                )

user_asked_question = Table('user_asked_question', Base.metadata,
                            Column('user_id', String, ForeignKey('user.id')),
                            Column('question_id', String, ForeignKey('question.id')),
                            Column('ts', DateTime)
                            )


class User(Base):
    __tablename__ = 'user'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    quizzes = relationship("Quiz", secondary=user_subscribed_to_quiz, back_populates="users")
    questions = relationship("Question", secondary=user_asked_question, back_populates="users")
    last_questions = relationship("LastQuestion", back_populates="user")


class Quiz(Base):
    __tablename__ = 'quiz'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    messages_per_day = Column(Integer)
    short_id = Column(Integer, unique=True, nullable=False)

    questions = relationship("Question", back_populates="quiz")
    users = relationship("User", secondary=user_subscribed_to_quiz, back_populates="quizzes")


class Question(Base):
    __tablename__ = 'question'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(String)
    is_essay = Column(Boolean)
    is_multiple_choice = Column(Boolean)
    quiz_id = Column(String, ForeignKey('quiz.id'))

    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("Answer", back_populates="question")
    feedback = relationship("Feedback", back_populates="question")
    users = relationship("User", secondary=user_asked_question, back_populates="questions")


class Answer(Base):
    __tablename__ = 'answer'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    identifier = Column(String)
    text = Column(String)
    is_correct = Column(Boolean)
    question_id = Column(String, ForeignKey('question.id'))

    question = relationship("Question", back_populates="answers")


class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    identifier = Column(String)
    text = Column(String)
    question_id = Column(String, ForeignKey('question.id'))

    question = relationship("Question", back_populates="feedback")


class LastQuestion(Base):
    __tablename__ = 'last_question'
    user_id = Column(String, ForeignKey('user.id'), primary_key=True)
    quiz_id = Column(String, ForeignKey('quiz.id'), primary_key=True)
    question_id = Column(String, ForeignKey('question.id'))
    room_id = Column(String)
    answered = Column(Boolean)
    asked_ts = Column(DateTime)
    answered_ts = Column(DateTime)

    user = relationship("User", back_populates="last_questions")
    quiz = relationship("Quiz")
    question = relationship("Question")


# Create the database
engine = create_engine(db_config.Config.get_db_uri())
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()
