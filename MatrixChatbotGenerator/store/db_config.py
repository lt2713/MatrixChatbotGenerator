class Config:
    LOCAL_DB_PATH = 'sqlite:///quizbot.db'
    NETWORK_DB_PATH = 'sqlite:////path/to/network/db/quizbot.db'

    @staticmethod
    def get_db_uri():
        return Config.LOCAL_DB_PATH
        # return Config.NETWORK_DB_PATH
