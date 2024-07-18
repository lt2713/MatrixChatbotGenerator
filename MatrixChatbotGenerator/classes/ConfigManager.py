import configparser
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Paths to the config and key files
CONFIG_FILE = './data/config.ini'
KEY_FILE = './data/secret.key'

load_dotenv()

DB_URL = os.getenv('DB_URL')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')


class ConfigManager:
    def __init__(self):
        self.ensure_data_directory_exists()
        self.key = self.load_key()

    @staticmethod
    def load_key():
        if not os.path.exists(KEY_FILE):
            key = Fernet.generate_key()
            with open(KEY_FILE, 'wb') as key_file:
                key_file.write(key)
        else:
            with open(KEY_FILE, 'rb') as key_file:
                key = key_file.read()
        return key


    @staticmethod
    def ensure_data_directory_exists():
        if not os.path.exists('./data'):
            os.makedirs('./data')

    def load_config(self, name):
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)
        else:
            if name == 'Db':
                config[name] = {'server': DB_URL, 'user_id': DB_USER, 'password':
                                self.encrypt_password(DB_PASSWORD)}
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
        return config

    @staticmethod
    def encrypt_password(password):
        key = ConfigManager.load_key()
        cipher_suite = Fernet(key)
        encrypted_password = cipher_suite.encrypt(password.encode())
        return encrypted_password.decode()

    @staticmethod
    def decrypt_password(encrypted_password):
        key = ConfigManager.load_key()
        cipher_suite = Fernet(key)
        decrypted_password = cipher_suite.decrypt(encrypted_password.encode())
        return decrypted_password.decode()

    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
