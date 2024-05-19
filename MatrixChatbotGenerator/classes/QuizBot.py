from classes.ChatbotConfig import ChatbotConfig
from classes.ConfigManager import ConfigManager
from nio import AsyncClient, MatrixRoom, RoomMessageText, SyncResponse, LoginResponse, InviteMemberEvent, MegolmEvent
import asyncio
import logging
import json
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Quizbot:
    def __init__(self):
        self.config = ChatbotConfig()
        self.homeserver = self.config.get_homeserver()
        self.user = self.config.get_user_id()
        encrypted_password = self.config.get_password()
        self.password = ConfigManager.decrypt_password(encrypted_password)
        # self.client = AsyncClient(self.homeserver, self.user)
        self.store_path = "store/"
        self.client = AsyncClient(self.homeserver, self.user, store_path=self.store_path)
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
            logger.info(f"Saved next_batch token: {next_batch}")

    async def sync_callback(self, response: SyncResponse):
        if isinstance(response, SyncResponse):
            self.save_next_batch(response.next_batch)
            logger.info("Sync completed successfully.")
        else:
            logger.error("Sync failed.")

    def process_message(self, message):
        if message.lower().startswith("quiz"):
            return "Let's start the quiz!"
        else:
            return "I didn't understand that. Type 'quiz' to start."

    async def message_callback(self, room: MatrixRoom, event):
        if event.sender != self.user:
            if isinstance(event, MegolmEvent):
                # Decrypt the MegolmEvent to get the plaintext message
                message = event.parse_encrypted_event()
                print(message)
                print('Event detected')
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


async def main():
    quizbot = Quizbot()
    await quizbot.run()

if __name__ == '__main__':
    asyncio.run(main())

