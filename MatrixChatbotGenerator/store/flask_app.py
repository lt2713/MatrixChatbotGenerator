import uuid

from flask import Flask, request, jsonify
from store.models import Quiz, Question, Answer, Feedback
from store.db_operations import get_all_quizzes, count_subscribers, get_all_questions_for_quiz, get_quiz_by_id, \
    update_quiz_attributes, delete_quiz_by_id, add_quiz_to_db, add_db_question_to_db, add_db_answer_to_db, \
    add_db_feedback_to_db
app = Flask(__name__)
ssl_enabled = False


@app.route('/quizzes', methods=['GET'])
def fetch_all_quizzes():
    quizzes = get_all_quizzes()
    quizzes_with_subscribers = []
    for quiz in quizzes:
        subscriber_count = count_subscribers(quiz.id)
        quizzes_with_subscribers.append({
            'id': quiz.id,
            'name': quiz.name,
            'messages_per_day': quiz.messages_per_day,
            'subscribers': subscriber_count
        })
    return jsonify(quizzes_with_subscribers)


@app.route('/quiz/<quiz_id>/questions', methods=['GET'])
def fetch_questions_for_quiz(quiz_id):
    questions = get_all_questions_for_quiz(quiz_id)
    return jsonify([{'id': question.id, 'type': question.type, 'text': question.text} for question in questions])


@app.route('/quizzes/<quiz_id>', methods=['PUT'])
def update_quiz(quiz_id):
    data = request.get_json()
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404

    quiz.name = data['name']
    quiz.messages_per_day = data['messages_per_day']
    if update_quiz_attributes(quiz_id, quiz.name, quiz.messages_per_day):
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


@app.route('/quizzes/<quiz_name>', methods=['GET'])
def quiz_exists(quiz_name):
    quiz_id = quiz_exists(quiz_name)
    if quiz_id:
        return jsonify({'id': quiz_id}), 200
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


def main():
    if ssl_enabled:
        app.run(host='0.0.0.0', port=2713,  ssl_context=('cert.pem', 'key.pem'))
    else:
        app.run(host='0.0.0.0', port=2713)


if __name__ == '__main__':
    main()
