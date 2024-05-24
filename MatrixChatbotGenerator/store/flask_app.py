from flask import Flask, request, jsonify
from models import Session, Quiz, Question

app = Flask(__name__)

# Use the existing session from models.py
session = Session()


@app.route('/quizzes', methods=['GET'])
def fetch_all_quizzes():
    quizzes = session.query(Quiz).all()
    return jsonify([{'id': quiz.id, 'name': quiz.name, 'messages_per_day': quiz.messages_per_day} for quiz in quizzes])


@app.route('/quiz/<quiz_id>/questions', methods=['GET'])
def fetch_questions_for_quiz(quiz_id):
    questions = session.query(Question).filter_by(quiz_id=quiz_id).all()
    return jsonify([{'id': question.id, 'type': question.type, 'text': question.text} for question in questions])


@app.route('/helloworld', methods=['GET'])
def helloworld():
    return jsonify('Hello World')


def main():
    app.run(host='0.0.0.0', port=2713)


if __name__ == '__main__':
    main()
