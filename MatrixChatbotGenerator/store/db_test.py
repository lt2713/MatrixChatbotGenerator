from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import db_config
from store.models import User, Quiz, Question, Answer, Feedback

engine = create_engine(db_config.Config.get_db_uri())
Session = sessionmaker(bind=engine)
session = Session()

# Example of adding a quiz and a question
quiz = Quiz(id="quiz1", name="Math Quiz")
session.add(quiz)

question1 = Question(id="question1", type="multiple_choice", text="What is 2 + 2?", quiz=quiz)
session.add(question1)

answer11 = Answer(id="answer11", identifier="A", text="4", is_correct=True, question=question1)
answer12 = Answer(id="answer12", identifier="B", text="5", is_correct=False, question=question1)
session.add(answer11)
session.add(answer12)

feedback11 = Feedback(id="feedback11", identifier="Correct", text="Correct! 2 + 2 is 4.", question=question1)
feedback12 = Feedback(id="feedback12", identifier="InCorrect", text="Wrong! 2 + 2 is 4.", question=question1)
session.add(feedback11)
session.add(feedback12)

question2 = Question(id="question2", type="multiple_choice", text="What is 2 / 0?", quiz=quiz)
session.add(question2)

answer21 = Answer(id="answer21", identifier="A", text="2", is_correct=False, question=question2)
answer22 = Answer(id="answer22", identifier="B", text="0", is_correct=False, question=question2)
answer23 = Answer(id="answer23", identifier="C", text="Infinity", is_correct=False, question=question2)
answer24 = Answer(id="answer24", identifier="D", text="Undefined", is_correct=True, question=question2)
session.add(answer21)
session.add(answer22)
session.add(answer23)
session.add(answer24)

feedback21 = Feedback(id="feedback21", identifier="Correct", text="Correct!", question=question2)
feedback22 = Feedback(id="feedback22", identifier="InCorrect", text="Wrong!", question=question2)
session.add(feedback21)
session.add(feedback22)


session.commit()
