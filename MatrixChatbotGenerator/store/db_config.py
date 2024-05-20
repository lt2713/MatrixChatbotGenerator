import os


class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file
    LOCAL_DB_PATH = f'sqlite:///{os.path.join(BASE_DIR, "quizbot.db")}'
    NETWORK_DB_PATH = 'sqlite:////path/to/network/db/quizbot.db'  # Ensure the path is accessible over the network

    @staticmethod
    def get_db_uri():
        return Config.LOCAL_DB_PATH
        # return Config.NETWORK_DB_PATH
