from classes.ConfigManager import ConfigManager


class ChatbotConfig:
    def __init__(self):
        self.name = 'Matrix'
        cm = ConfigManager()
        self.config = cm.load_config(self.name)

    def get_homeserver(self):
        return self.config[self.name]['server']

    def get_user_id(self):
        return self.config[self.name]['user_id']

    def get_password(self):
        return self.config[self.name]['password']

    def get(self):
        return f"Homeserver: {self.get_homeserver()}\t" \
               f"User ID: {self.get_user_id()}\t" \
               f"Password: {self.get_password()}\t"


# Example usage
if __name__ == "__main__":
    bot_config = ChatbotConfig()
    print(bot_config.get())

