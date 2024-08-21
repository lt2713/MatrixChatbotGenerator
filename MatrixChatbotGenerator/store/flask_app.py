import os
import uuid

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from store.models import Quiz, Question, Answer, Feedback
from store.db_operations import get_all_quizzes, count_subscribers, get_all_questions_for_quiz, get_quiz_by_id, \
    update_quiz_attributes, delete_quiz_by_id, add_quiz_to_db, add_db_question_to_db, add_db_answer_to_db, \
    add_db_feedback_to_db, count_questions

ssl_enabled = False
app = Flask(__name__)
load_dotenv()

FLASK_PORT = os.getenv('FLASK_PORT')
FLASK_HOST = os.getenv('FLASK_HOST')


@app.route('/quizzes', methods=['GET'])
def fetch_all_quizzes():
    quizzes = get_all_quizzes()
    quizzes_with_subscribers = []
    for quiz in quizzes:
        subscriber_count = count_subscribers(quiz.id)
        question_count = count_questions(quiz.id)
        quizzes_with_subscribers.append({
            'id': quiz.id,
            'name': quiz.name,
            'messages_per_day': quiz.messages_per_day,
            'subscribers': subscriber_count,
            'questions': question_count
        })
    return jsonify(quizzes_with_subscribers)


@app.route('/quiz/<quiz_id>/questions', methods=['GET'])
def fetch_questions_for_quiz(quiz_id):
    questions = get_all_questions_for_quiz(quiz_id)
    return jsonify([{'id': question.id, 'text': question.text, 'is_multiple_choice':
                     question.is_multiple_choice, 'is_essay': question.is_essay} for question in questions])


@app.route('/quizzes/<quiz_id>', methods=['PUT'])
def update_quiz(quiz_id):
    data = request.get_json()
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404

    name = data['name']
    messages_per_day = data['messages_per_day']
    if update_quiz_attributes(quiz_id, name, messages_per_day):
        return jsonify({'message': 'Quiz updated successfully'}), 200
    else:
        return jsonify({'error': 'Quiz not updated'}), 400


@app.route('/quizzes/<quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404

    delete_quiz_by_id(quiz_id)
    return jsonify({'message': 'Quiz deleted successfully'}), 200


@app.route('/quizzes', methods=['POST'])
def add_quiz():
    data = request.get_json()
    new_quiz = Quiz(name=data['name'], messages_per_day=data['messages_per_day'], short_id=0)
    add_quiz_to_db(None, new_quiz)

    return jsonify({'id': new_quiz.id}), 201


@app.route('/quizzes/<quiz_id>/questions', methods=['POST'])
def add_question(quiz_id):
    data = request.get_json()
    new_question = Question(
        quiz_id=quiz_id,
        text=data['text'],
        is_essay=data['is_essay'],
        is_multiple_choice=data['is_multiple_choice']
    )
    add_db_question_to_db(new_question)

    # Add answers
    for answer in data.get('answers', []):
        new_answer = Answer(
            id=str(uuid.uuid4()),
            identifier=answer['identifier'],
            text=answer['text'],
            is_correct=answer['is_correct'],
            question_id=new_question.id
        )
        add_db_answer_to_db(new_answer)

    # Add feedbacks
    for feedback in data.get('feedback', []):
        new_feedback = Feedback(
            id=str(uuid.uuid4()),
            identifier=feedback['identifier'],
            text=feedback['text'],
            question_id=new_question.id
        )
        add_db_feedback_to_db(new_feedback)

    return jsonify({'id': new_question.id}), 201


@app.route('/helloworld', methods=['GET'])
def helloworld():
    return jsonify('Hello World')


@app.route('/quizbot_info', methods=['GET'])
def quizbot_info():
    matrix_host = os.getenv('MATRIX_HOST')
    matrix_user = os.getenv('MATRIX_USER')
    return jsonify({
        "matrix_host": matrix_host,
        "matrix_user": matrix_user
    })


def main():
    if ssl_enabled:
        app.run(host=FLASK_HOST, port=FLASK_PORT,  ssl_context=('cert.pem', 'key.pem'))    # Adjust port number
    else:
        app.run(host=FLASK_HOST, port=FLASK_PORT)  # Adjust port number


if __name__ == '__main__':
    main()
