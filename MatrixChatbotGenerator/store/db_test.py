from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from store import db_config
from store.models import User, Quiz, Question, Answer, Feedback

engine = create_engine(db_config.Config.get_db_uri())
Session = sessionmaker(bind=engine)
session = Session()


def create_quiz(quiz_id, name, messages_per_day):
    quiz = Quiz(id=quiz_id, name=name, messages_per_day=messages_per_day)
    session.add(quiz)
    return quiz


def create_question(question_id, quiz, text, question_type="Multiple Choice"):
    question = Question(id=question_id, is_essay=False, is_multiple_choice=True, text=text, quiz=quiz)
    session.add(question)
    return question


def create_answer(answer_id, question, identifier, text, is_correct):
    answer = Answer(id=answer_id, identifier=identifier, text=text, is_correct=is_correct, question=question)
    session.add(answer)


def create_feedback(feedback_id, question, identifier, text):
    feedback = Feedback(id=feedback_id, identifier=identifier, text=text, question=question)
    session.add(feedback)


def create_test_data():
    # Example of adding a quiz and a question
    # Create Math Quiz
    math_quiz = create_quiz("quiz1", "Math Quiz", messages_per_day=1)

    # Question 1
    math_question1 = create_question("question1", math_quiz, "What is 2 + 2?")
    create_answer("answer11", math_question1, "A", "4", True)
    create_answer("answer12", math_question1, "B", "5", False)
    create_feedback("feedback11", math_question1, "Correct", "Correct! 2 + 2 is 4.")
    create_feedback("feedback12", math_question1, "InCorrect", "Wrong! 2 + 2 is 4.")

    # Question 2
    math_question2 = create_question("question2", math_quiz, "What is 2 / 0?")
    create_answer("answer21", math_question2, "A", "2", False)
    create_answer("answer22", math_question2, "B", "0", False)
    create_answer("answer23", math_question2, "C", "Infinity", False)
    create_answer("answer24", math_question2, "D", "Undefined", True)
    create_feedback("feedback21", math_question2, "Correct", "Correct!")
    create_feedback("feedback22", math_question2, "InCorrect", "Wrong!")

    # Question 3
    math_question3 = create_question("question3", math_quiz, "What is the square root of 16?")
    create_answer("answer31", math_question3, "A", "2", False)
    create_answer("answer32", math_question3, "B", "4", True)
    create_answer("answer33", math_question3, "C", "8", False)
    create_answer("answer34", math_question3, "D", "16", False)
    create_feedback("feedback31", math_question3, "Correct", "Correct! The square root of 16 is 4.")
    create_feedback("feedback32", math_question3, "InCorrect", "Wrong! The square root of 16 is 4.")

    # Question 4
    math_question4 = create_question("question4", math_quiz, "What is the result of 3 * 3?")
    create_answer("answer41", math_question4, "A", "6", False)
    create_answer("answer42", math_question4, "B", "9", True)
    create_answer("answer43", math_question4, "C", "12", False)
    create_answer("answer44", math_question4, "D", "15", False)
    create_feedback("feedback41", math_question4, "Correct", "Correct! 3 * 3 is 9.")
    create_feedback("feedback42", math_question4, "InCorrect", "Wrong! 3 * 3 is 9.")

    # Question 5
    math_question5 = create_question("question5", math_quiz, "What is the value of pi (approx)?")
    create_answer("answer51", math_question5, "A", "2.14", False)
    create_answer("answer52", math_question5, "B", "3.14", True)
    create_answer("answer53", math_question5, "C", "4.14", False)
    create_answer("answer54", math_question5, "D", "5.14", False)
    create_feedback("feedback51", math_question5, "Correct", "Correct! The approximate value of pi is 3.14.")
    create_feedback("feedback52", math_question5, "InCorrect", "Wrong! The approximate value of pi is 3.14.")

    # Create Python Programming Quiz
    python_quiz = create_quiz("quiz2", "Python Programming - Beginner", messages_per_day=1)

    # Question 1
    python_question1 = create_question("python_question1", python_quiz, "Which of the following is a "
                                                                        "valid variable name "
                                                                        "in Python?")
    create_answer("python_answer11", python_question1, "A", "1variable", False)
    create_answer("python_answer12", python_question1, "B", "variable1", True)
    create_answer("python_answer13", python_question1, "C", "variable-1", False)
    create_answer("python_answer14", python_question1, "D", "variable@1", False)
    create_feedback("python_feedback11", python_question1, "Correct", "Correct! 'variable1' is a valid "
                                                                      "variable name in "
                                                                      "Python.")
    create_feedback("python_feedback12", python_question1, "InCorrect", "Incorrect. Variable names cannot start with a "
                                                                        "number or contain special characters.")

    # Question 2
    python_question2 = create_question("python_question2", python_quiz, "Which keyword is used to define a"
                                                                        " function in "
                                                                        "Python?")
    create_answer("python_answer21", python_question2, "A", "func", False)
    create_answer("python_answer22", python_question2, "B", "def", True)
    create_answer("python_answer23", python_question2, "C", "function", False)
    create_answer("python_answer24", python_question2, "D", "define", False)
    create_feedback("python_feedback21", python_question2, "Correct", "Correct! 'def' is used to define a function in "
                                                                      "Python.")
    create_feedback("python_feedback22", python_question2, "InCorrect", "Incorrect. The correct keyword is 'def'.")

    # Question 3
    python_question3 = create_question("python_question3", python_quiz, "Which of the following is used to start a "
                                                                        "comment in Python?")
    create_answer("python_answer31", python_question3, "A", "//", False)
    create_answer("python_answer32", python_question3, "B", "#", True)
    create_answer("python_answer33", python_question3, "C", "/*", False)
    create_answer("python_answer34", python_question3, "D", "<!--", False)
    create_feedback("python_feedback31", python_question3, "Correct", "Correct! '#' is used to start a c"
                                                                      "omment in Python.")
    create_feedback("python_feedback32", python_question3, "InCorrect", "Incorrect. '#' is used to start a comment in "
                                                                        "Python.")

    # Question 4
    python_question4 = create_question("python_question4", python_quiz, "How do you create a variable with the numeric "
                                                                        "value 5 in Python?")
    create_answer("python_answer41", python_question4, "A", "x = 5", True)
    create_answer("python_answer42", python_question4, "B", "int x = 5", False)
    create_answer("python_answer43", python_question4, "C", "x := 5", False)
    create_answer("python_answer44", python_question4, "D", "x <- 5", False)
    create_feedback("python_feedback41", python_question4, "Correct", "Correct! 'x = 5' creates a variable with the "
                                                                      "numeric value 5.")
    create_feedback("python_feedback42", python_question4, "InCorrect", "Incorrect. 'x = 5' is the correct way "
                                                                        "to create "
                                                                        "a variable with the numeric value 5.")
    # Question 5
    python_question5 = create_question("python_question5", python_quiz, "What is the output of print(2 ** 3)?")
    create_answer("python_answer51", python_question5, "A", "5", False)
    create_answer("python_answer52", python_question5, "B", "6", False)
    create_answer("python_answer53", python_question5, "C", "8", True)
    create_answer("python_answer54", python_question5, "D", "9", False)
    create_feedback("python_feedback51", python_question5, "Correct", "Correct! 'print(2 ** 3)' outputs 8.")
    create_feedback("python_feedback52", python_question5, "InCorrect", "Incorrect. 'print(2 ** 3)' outputs 8.")

    # Commit the changes
    session.commit()

    # Commit the changes
    session.commit()

def main():
    create_test_data()


if __name__ == '__main__':
    main()

