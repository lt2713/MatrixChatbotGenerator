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

    def print(self):
        print("Homeserver:", self.get_homeserver())
        print("User ID:", self.get_user_id())
        print("Password:", self.get_password())


# Example usage
if __name__ == "__main__":
    bot_config = ChatbotConfig()
    bot_config.print()

