from flask import Flask, request, jsonify
from store.models import Session, Quiz, Question

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


@app.route('/api/quizzes/<quiz_name>', methods=['GET'])
def quiz_exists(quiz_name):
    quiz = session.query(Quiz).filter_by(name=quiz_name).first()
    if quiz:
        return jsonify({'id': quiz.id}), 200
    return jsonify({'error': 'Quiz not found'}), 404


@app.route('/api/quizzes', methods=['POST'])
def add_quiz():
    data = request.get_json()
    new_quiz = Quiz(name=data['name'], messages_per_day=data['messages_per_day'])
    session.add(new_quiz)
    session.commit()
    return jsonify({'id': new_quiz.id}), 201


@app.route('/api/quizzes/<quiz_id>/questions', methods=['POST'])
def add_question(quiz_id):
    data = request.get_json()
    new_question = Question(
        quiz_id=quiz_id,
        type=data['type'],
        text=data['text']
    )
    session.add(new_question)
    session.commit()
    return jsonify({'id': new_question.id}), 201


@app.route('/helloworld', methods=['GET'])
def helloworld():
    return jsonify('Hello World')


def main():
    app.run(host='0.0.0.0', port=2713)


if __name__ == '__main__':
    main()
