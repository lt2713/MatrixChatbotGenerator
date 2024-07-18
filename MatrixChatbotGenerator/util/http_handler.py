import requests
from requests.auth import HTTPBasicAuth

from classes.ConfigManager import ConfigManager


class HttpHandler:
    def __init__(self, url=None, user=None, password=None):
        self.cm = ConfigManager()
        self.config = self.cm.load_config('Db')
        if url and user and password:
            self.api_url = url
            self.user = user
            self.password = password
        else:
            self.load_config()
        self.auth = HTTPBasicAuth(self.user, self.password)

    def load_config(self):
        self.api_url = self.config['Db']['server']
        self.user = self.config['Db']['user_id']
        self.password = ConfigManager.decrypt_password(self.config['Db']['password'])

    def get(self, path):
        response = requests.get(f'{self.api_url}{path}', auth=self.auth)
        return response

    def post(self, path, data):
        response = requests.post(f'{self.api_url}{path}', json=data, auth=self.auth)
        return response

    def put(self, path, data):
        response = requests.put(f'{self.api_url}{path}', json=data, auth=self.auth)
        return response

    def delete(self, path):
        response = requests.delete(f'{self.api_url}{path}', auth=self.auth)
        return response

    def test_connection(self):
        if not self.api_url:
            return False
        response = requests.get(f'{self.api_url}/helloworld', auth=self.auth)
        if response.status_code == 200:
            return True
        else:
            return False

    def get_url(self):
        return self.api_url

    def get_user(self):
        return self.user

    def get_password(self):
        return self.password

    def get_auth(self):
        return self.auth

    def set_url(self, url):
        self.api_url = url

    def set_user(self, user):
        self.user = user
        self.update_auth()

    def set_password(self, password):
        self.password = password
        self.update_auth()

    def update_auth(self):
        if self.user and self.password:
            self.auth = HTTPBasicAuth(self.user, self.password)
