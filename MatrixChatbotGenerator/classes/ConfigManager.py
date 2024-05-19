import configparser
import os

# Determine the absolute path of the configuration file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.ini')


class ConfigManager:
    @staticmethod
    def load_config():
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)
        else:
            config['Matrix'] = {'homeserver': '', 'user_id': '', 'access_token': ''}
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
        return config

    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
