from classes.ChatbotConfig import ChatbotConfig
from classes.ConfigManager import ConfigManager
from structures.transaction import Transaction
from structures.questions import Questions
from nio import AsyncClient, MatrixRoom, RoomMessageText, SyncResponse, LoginResponse, InviteMemberEvent, MegolmEvent
import asyncio
import logging
import json
import os
import signal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

        self.config.print()

        # Path to store the next_batch token
        self.next_batch_file = 'next_batch_token.json'
        self.load_next_batch()

    async def send_message(self, room_id, message):
        await self.client.room_send(
            room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message}
        )

    def process_message(self, message):
        message_lower = message.lower()
        words = message_lower.split()
        if message.lower().startswith("quiz"):
            return "Let's start the quiz!"
        elif words[0] in ('help', '!help'):
            return self.message_help()
        else:
            return "I didn't understand that. Type 'quiz' to start."

    @staticmethod
    def message_help():
        return ('Hello, I am the Quizbot. Try out one of the following commands: \n'
                '!help \t\t\t\t\t show the help menu\n'
                '!quizzes \t\t\t\t\t show available quizzes\n'
                '!subscribed \t\t\t\t show subscribed quizzes\n'
                '!subscribe &quiz \t\t\t subscribe to given quiz\n'
                '!unsubscribe &quiz \t\t unsubscribe from given quiz\n'
                '!nextquestion &quiz \t\t get the next question from given quiz\n'
                )

    async def message_callback(self, room: MatrixRoom, event):
        if event.sender != self.user:
            logger.info(f"Received message from user: {event.sender}")
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
                print(f'Unknown event type:')
                return  # Unknown event type, skip processing

            response_message = self.process_message(message)
            await self.send_message(room.room_id, response_message)

    async def invite_callback(self, room: MatrixRoom, event: InviteMemberEvent):
        if event.membership == "invite":
            await self.client.join(room.room_id)
            logger.info(f"Joined room: {room.room_id}")

    async def run(self):
        self.client.add_event_callback(self.message_callback, RoomMessageText)
        self.client.add_response_callback(self.sync_callback, SyncResponse)
        self.client.add_event_callback(self.invite_callback, InviteMemberEvent)
        self.client.add_event_callback(self.message_callback, MegolmEvent)
        await self.login()

        try:
            logger.info("Starting sync...")
            await self.client.sync_forever(timeout=30000)  # Adjust timeout as needed
        except Exception as e:
            logger.error(f"Error during sync: {e}")

    async def login(self):
        response = await self.client.login(self.password)
        if isinstance(response, LoginResponse):
            print("Login successful!")
        else:
            print("Login failed!")

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

