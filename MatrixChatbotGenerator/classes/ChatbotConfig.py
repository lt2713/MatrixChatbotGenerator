from classes.ConfigManager import ConfigManager


class ChatbotConfig:
    def __init__(self):
        self.config = ConfigManager.load_config()

    def get_homeserver(self):
        return self.config['Matrix']['homeserver']

    def get_user_id(self):
        return self.config['Matrix']['user_id']

    def get_access_token(self):
        return self.config['Matrix']['access_token']


# Example usage
if __name__ == "__main__":
    bot_config = ChatbotConfig()
    print("Homeserver:", bot_config.get_homeserver())
    print("User ID:", bot_config.get_user_id())
    print("Access Token:", bot_config.get_access_token())
