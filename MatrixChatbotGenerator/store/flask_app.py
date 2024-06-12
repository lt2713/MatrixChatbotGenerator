import uuid

from flask import Flask, request, jsonify
from store.models import Session, Quiz, Question, Answer, Feedback, user_subscribed_to_quiz
from store.db_operations import add_quiz_to_db
app = Flask(__name__)
ssl_enabled = False

# Use the existing session from models.py
session = Session()


@app.route('/quizzes', methods=['GET'])
def fetch_all_quizzes():
    quizzes = session.query(Quiz).all()
    quizzes_with_subscribers = []
    for quiz in quizzes:
        subscriber_count = session.query(user_subscribed_to_quiz).filter_by(quiz_id=quiz.id).count()
        quizzes_with_subscribers.append({
            'id': quiz.id,
            'name': quiz.name,
            'messages_per_day': quiz.messages_per_day,
            'subscribers': subscriber_count
        })
    return jsonify(quizzes_with_subscribers)


@app.route('/quiz/<quiz_id>/questions', methods=['GET'])
def fetch_questions_for_quiz(quiz_id):
    questions = session.query(Question).filter_by(quiz_id=quiz_id).all()
    return jsonify([{'id': question.id, 'type': question.type, 'text': question.text} for question in questions])


@app.route('/quizzes/<quiz_id>', methods=['PUT'])
def update_quiz(quiz_id):
    data = request.get_json()
    quiz = session.query(Quiz).filter_by(id=quiz_id).first()
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404

    quiz.name = data['name']
    quiz.messages_per_day = data['messages_per_day']
    session.commit()
    return jsonify({'message': 'Quiz updated successfully'}), 200


@app.route('/quizzes/<quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    quiz = session.query(Quiz).filter_by(id=quiz_id).first()
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404

    session.delete(quiz)
    session.commit()
    return jsonify({'message': 'Quiz deleted successfully'}), 200


@app.route('/quizzes/<quiz_name>', methods=['GET'])
def quiz_exists(quiz_name):
    quiz = session.query(Quiz).filter_by(name=quiz_name).first()
    if quiz:
        return jsonify({'id': quiz.id}), 200
    return jsonify({'error': 'Quiz not found'}), 404


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
    session.add(new_question)
    session.commit()

    # Add answers
    for answer in data.get('answers', []):
        new_answer = Answer(
            id=str(uuid.uuid4()),
            identifier=answer['identifier'],
            text=answer['text'],
            is_correct=answer['is_correct'],
            question_id=new_question.id
        )
        session.add(new_answer)

    # Add feedbacks
    for feedback in data.get('feedback', []):
        new_feedback = Feedback(
            id=str(uuid.uuid4()),
            identifier=feedback['identifier'],
            text=feedback['text'],
            question_id=new_question.id
        )
        session.add(new_feedback)

    session.commit()
    return jsonify({'id': new_question.id}), 201


@app.route('/helloworld', methods=['GET'])
def helloworld():
    return jsonify('Hello World')


def main():
    if ssl_enabled:
        app.run(host='0.0.0.0', port=2713,  ssl_context=('cert.pem', 'key.pem'))
    else:
        app.run(host='0.0.0.0', port=2713)


if __name__ == '__main__':
    main()
