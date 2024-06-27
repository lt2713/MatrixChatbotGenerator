import configparser
import os
from cryptography.fernet import Fernet

# Paths to the config and key files
CONFIG_FILE = './data/config.ini'
KEY_FILE = './data/secret.key'


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
                config[name] = {'server': 'https://ltquiz.duckdns.org', 'user_id': 'quizbot', 'password':
                                self.encrypt_password('botquiz')}
            elif name == 'Matrix':
                config[name] = {'server': 'https://matrix-client.matrix.org', 'user_id': '@lt2713b:matrix.org',
                                'password': self.encrypt_password('4Rz5EdP6Yem$R9W')}
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
