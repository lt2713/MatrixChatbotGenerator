from classes.ConfigManager import ConfigManager


class ChatbotConfig:
    def __init__(self):
        self.config = ConfigManager.load_config()

    def get_homeserver(self):
        return self.config['Matrix']['homeserver']

    def get_user_id(self):
        return self.config['Matrix']['user_id']

    def get_password(self):
        return self.config['Matrix']['password']

    def get(self):
        return f"Homeserver: {self.get_homeserver()}\t" \
               f"User ID: {self.get_user_id()}\t" \
               f"Password: {self.get_password()}\t"


# Example usage
if __name__ == "__main__":
    bot_config = ChatbotConfig()
    print(bot_config.get())

