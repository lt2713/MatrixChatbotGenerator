from classes.ChatbotConfig import ChatbotConfig
from nio import AsyncClient, MatrixRoom, RoomMessageText, LoginResponse
import asyncio


class Quizbot:
    def __init__(self):
        self.config = ChatbotConfig()
        self.homeserver = self.config.get_homeserver()
        self.user = self.config.get_user_id()
        self.access_token = self.config.get_access_token()


