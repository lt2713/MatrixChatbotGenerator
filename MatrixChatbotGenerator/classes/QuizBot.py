import re
from classes.ChatbotConfig import ChatbotConfig
from classes.ConfigManager import ConfigManager
from store.db_operations import *
from nio import AsyncClient, MatrixRoom, RoomMessageText, SyncResponse, LoginResponse, InviteMemberEvent, MegolmEvent
from util import utility_functions as util
import asyncio
import json
import os
import signal

# Set up logging
logger = util.create_logger('quizbot')


class Quizbot:
    def __init__(self, transaction=None, questions=None):
        self.transaction = transaction if transaction else None
        self.questions = questions if questions else None
        self.config = ChatbotConfig()
        self.homeserver = self.config.get_homeserver()
        self.user = self.config.get_user_id()
        encrypted_password = self.config.get_password()

        self.password = ConfigManager.decrypt_password(encrypted_password)
        self.client = AsyncClient(self.homeserver, self.user)

        logger.info(self.config.get())

        # Path to store the next_batch token
        self.next_batch_file = '../data/next_batch_token.json'
        self.load_next_batch()

    @staticmethod
    def message_help():
        return ('Hello, I am the Quizbot. Try out one of the following commands: \n'
                'help \t\t\t\t\t show the help menu\n'
                'quizzes \t\t\t\t\t show available quizzes\n'
                'subscribed \t\t\t\t show subscribed quizzes\n'
                'subscribe quiz_name\t\t subscribe to given quiz\n'
                'unsubscribe quiz_name\t\t unsubscribe from given quiz\n'
                'nextquestion quiz_name\t get the next question from given quiz\n'
                'reset quiz_name\t\t\t reset the quiz for me \n'
                'delete quiz_name\t\t\t delete the quiz\n'
                )

    def quizzes_list(self):
        quizzes = fetch_all_quizzes()
        if len(quizzes) == 0:
            return 'There are no quizzes available.'
        result = 'Enter "subscribe" and the quiz name to subscribe to a Quiz.\nThese are the available quizzes:\n'
        for quiz in quizzes:
            result += '- ' + quiz.name + '\n'
        return result

    def subscribe(self, user_id, room_id, quiz_name):
        quiz_id = get_quiz_id_by_name(quiz_name)
        if not quiz_id:
            return 'This Quiz does not exist.'
        if not user_exists(user_id):
            create_user(user_id)
        if is_user_subscribed(user_id, quiz_id):
            return 'You are already subscribed to the Quiz.'
        if subscribe_user_to_quiz(user_id, quiz_id, room_id):
            return f'You have successfully subscribed to the Quiz "{quiz_name}".'
        else:
            return "I'm sorry, that didn't work."

    def subscribed_quizzes(self, user_id):
        quizzes = get_subscribed_quizzes(user_id)
        if not quizzes or len(quizzes) == 0:
            response = 'You are not subscribed to any Quiz.'
        else:
            response = 'You are subscribed to the following Quizzes: \n'
            for quiz in quizzes:
                response += quiz.name
        return response

    def unsubscribe(self, user_id, quiz_name):
        quiz_id = get_quiz_id_by_name(quiz_name)
        if not quiz_id:
            return 'This Quiz does not exist.'
        if not is_user_subscribed(user_id, quiz_id):
            return f'You are not subscribed to the Quiz "{quiz_name}".'
        if unsubscribe_user_from_quiz(user_id, quiz_id):
            return f'You have successfully unsubscribed from the Quiz "{quiz_name}".'
        else:
            return "I'm sorry, that didn't work."

    def next_question(self, user_id, quiz_name):
        if not quiz_name and count_subscribed_quizzes(user_id) == 1:
            quiz_id = get_subscribed_quizzes(user_id)[0].id
        else:
            quiz_id = get_quiz_id_by_name(quiz_name)
        if not quiz_id:
            return 'This Quiz does not exist.'
        if not is_user_subscribed(user_id, quiz_id):
            return f'You are not subscribed to the Quiz "{quiz_name}".'
        if has_open_question(user_id):
            return 'You still have an open question. Please try to answer that first.'
        question = get_unanswered_question(user_id, quiz_id)
        if question:
            return self.ask_question(quiz_id, user_id, question)
        else:
            unsubscribe_user_from_quiz(user_id, quiz_id)
            return 'There is no question left i could ask you.'

    def ask_question(self, quiz_id, user_id, db_question):
        question = convert_question_model_to_question(db_question)
        if ask_question_to_user(user_id, quiz_id, question.id):
            return question.get()
        else:
            return 'There was an unexpected error trying to ask a question.'

    def process_answer(self, user_id, message):
        open_question = get_open_question(user_id)
        question = convert_question_model_to_question(open_question)
        response = ' '
        if question.type == 'Essay Question':
            response = 'Thanks for answering the open question. '
            model_answer = get_model_answer(question.id)
            if model_answer:
                response += 'Here is a model answer:\n'
                response += model_answer.text
        if question.type in ('Multiple Choice', 'Multiple Correct', 'True - False'):
            result = self.check_multiple_choice_answer(message, question)
            fb = get_feedback(question.id, True if result == 'Correct' else False)
            if result == 'Correct':
                response = 'You gave the correct answer.\n'
            elif result == 'Partly Correct':
                response = 'Your answer is partly correct. \n'
            else:
                response = 'Your answer is incorrect. \n'
            if fb.text:
                response += fb.text
            else:
                if result != 'Correct':
                    response += 'The correct answer is: \n'
                    for answer in question.answers:
                        if answer.correct:
                            response += answer.identifier + ') ' + answer.text + '\n'
        update_user_answered_question(user_id, question.id)
        update_last_question(user_id, open_question.quiz_id, question.id, True)
        if not get_unanswered_question(user_id, open_question.quiz_id):
            response += '\nCongratulations, you have completed the quiz.'
            unsubscribe_user_from_quiz(user_id, open_question.quiz_id)
        return response

    def check_multiple_choice_answer(self, user_input, question):
        # Create answer map
        answer_map = self.create_answers_map(question.answers)
        # Separate correct and incorrect answers
        correct_answers = {answer.identifier.lower() for answer in question.answers if answer.correct}

        # Normalize the user input
        user_answers = self.normalize_user_input(user_input, question)
        user_answers_set = set(user_answers)
        # Determine the result
        if user_answers_set == correct_answers:
            return "Correct"
        elif user_answers_set & correct_answers:
            return "Partly Correct"
        else:
            return "Incorrect"

    def delete_quiz(self, quiz_name):
        quiz_id = get_quiz_id_by_name(quiz_name)
        if not quiz_id:
            return 'This Quiz does not exist.'
        if delete_quiz_by_id(quiz_id):
            return 'The Quiz has been deleted.'
        else:
            return "I'm sorry, that didn't work."

    def reset_quiz(self, user_id, quiz_name):
        quiz_id = get_quiz_id_by_name(quiz_name)
        if not quiz_id:
            return 'This Quiz does not exist.'
        if reset_quiz_by_id(quiz_id, user_id):
            return 'The Quiz has been reset.'
        else:
            return "I'm sorry, that didn't work."

    async def send_message(self, room_id, message):
        logger.info(f"sending message to room id {room_id}: {message}")
        await self.client.room_send(
            room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message}
        )

    def process_message(self, message, room_id, user_id):
        message_lower = message.lower()
        words = message_lower.split()
        command = words[0]
        parameter = message[len(words[0]):].strip() if len(words) > 1 else None

        if message.lower().startswith('hello'):
            return "Hello!"
        elif command in ('help', '!help') and len(words) == 1:
            return self.message_help()
        elif command in ('quizzes', 'quizzes') and len(words) == 1:
            return self.quizzes_list()
        elif command in ('subscribe', '!subscribe', 'unsubscribe', '!unsubscribe', '!sub', '!unsub'):
            if command in ('subscribe', '!subscribe', '!sub'):
                return self.subscribe(user_id, room_id, parameter)
            else:
                return self.unsubscribe(user_id, parameter)
        elif command == 'subscribed':
            return self.subscribed_quizzes(user_id)
        elif command in ('nextquestion', '!nextquestion', '!nq'):
            return self.next_question(user_id, parameter)
        elif command in ('delete', '!delete'):
            return self.delete_quiz(parameter)
        elif command in ('reset', '!reset'):
            return self.reset_quiz(user_id, parameter)
        elif has_open_question(user_id):
            return self.process_answer(user_id, message)
        else:
            return "I didn't understand that. Type 'help' to see what I can understand."

    async def message_callback(self, room: MatrixRoom, event):
        if event.sender != self.user:
            if isinstance(event, MegolmEvent):
                # Decrypt the MegolmEvent to get the plaintext message
                # message = event.parse_encrypted_event()
                # print(message)
                message = ' '
                if event.decrypted:
                    message = event.body
                else:
                    message = ' '
                    logger.error(f"Encrypted messages are not supported")
                    return
            elif isinstance(event, RoomMessageText):
                message = event.body
            else:
                logger.info(f'Unknown event type: {event.type}')
                return  # Unknown event type, skip processing
            logger.info(f"Received message from user {event.sender}: {message}")
            response_message = self.process_message(message, room.room_id, event.sender)
            await self.send_message(room.room_id, response_message)

    async def invite_callback(self, room: MatrixRoom, event: InviteMemberEvent):
        if event.membership == "invite":
            await self.client.join(room.room_id)
            logger.info(f"Joined room: {room.room_id}")
            message = f"Hi {event.sender.split(':')[0].lstrip('@')}, I'm a Quizbot. " \
                      f"You can subscribe to the quizzes I have available. I will " \
                      f"then start to ask you questions and give you feedback for your answers. To start, " \
                      f"type 'quizzes' and I will show you the list of quizzes I know. Type 'help' to see which " \
                      f"commands I understand. "
            await self.send_message(room.room_id, message)

    def normalize_user_input(self, user_input, question):
        # Remove any unwanted characters and split the input
        user_input = re.sub(r'[^\w\s]', '', user_input.lower())
        tokens = re.split(r'\s+|and', user_input)
        # Map possible text answers to their identifiers
        answer_map = self.create_answers_map(question.answers)
        normalized_answers = []
        for token in tokens:
            token = token.strip()
            if token in answer_map:
                normalized_answers.append(answer_map[token])
            elif token in answer_map.values():
                normalized_answers.append(token)
        return normalized_answers

    @staticmethod
    def create_answers_map(answers):
        answer_map = {}
        for answer in answers:
            answer_map[answer.text.lower()] = answer.identifier.lower()
        return answer_map

    async def run(self):
        self.client.add_event_callback(self.message_callback, RoomMessageText)
        self.client.add_response_callback(self.sync_callback, SyncResponse)
        self.client.add_event_callback(self.invite_callback, InviteMemberEvent)
        self.client.add_event_callback(self.message_callback, MegolmEvent)
        await self.login()

        while True:
            try:
                logger.info("Starting sync...")
                await self.client.sync_forever(timeout=30000)  # Adjust timeout as needed
            except Exception as e:
                logger.error(f"Error during sync: {e}")
                logger.info("Retrying after error...")
                await asyncio.sleep(5)

    async def login(self):
        response = await self.client.login(self.password)
        if isinstance(response, LoginResponse):
            logger.info("Login successful!")
        else:
            logger.error("Login failed!")

    def load_next_batch(self):
        """Load the next_batch token from a file."""
        if os.path.exists(self.next_batch_file):
            with open(self.next_batch_file, 'r') as file:
                data = json.load(file)
                self.client.next_batch = data.get('next_batch', None)
                logger.info(f"Loaded next_batch token: {self.client.next_batch}")

    def save_next_batch(self, next_batch):
        """Save the next_batch token to a file."""
        with open(self.next_batch_file, 'w') as file:
            json.dump({'next_batch': next_batch}, file)
            # logger.info(f"Saved next_batch token: {next_batch}")

    async def sync_callback(self, response: SyncResponse):
        if isinstance(response, SyncResponse):
            self.save_next_batch(response.next_batch)
            # logger.info("Sync completed successfully.")
        else:
            logger.error("Sync failed.")

    async def close(self):
        logger.info("Closing client session...")
        await self.client.close()
        logger.info("Client session closed.")


def handle_exit(signum, frame, bot, loop):
    logger.info("Signal received, exiting...")
    loop.create_task(bot.close())
    # Delay stopping the loop to give the close task time to finish
    loop.call_soon(loop.stop)


async def main():
    quizbot = Quizbot()

    loop = asyncio.get_event_loop()

    # Register signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda s, f: handle_exit(s, f, quizbot, loop))

    await quizbot.run()

    # Give time for pending tasks to complete
    pending = asyncio.all_tasks(loop)
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)


if __name__ == '__main__':
    asyncio.run(main())

