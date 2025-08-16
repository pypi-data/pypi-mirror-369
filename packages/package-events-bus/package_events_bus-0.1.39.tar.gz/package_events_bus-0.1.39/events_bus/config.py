import os
from os import _Environ
import dotenv
import logging


class Config:
    def __init__(self,
                 envs: _Environ[str] = None,
                 env_file: str = None):
        self.__envs = envs
        self.__env_file = env_file
        self.__load()

    def set_envs(self, envs: _Environ[str], env_file: str = None):
        """Set the environment variables."""
        self.__envs = envs
        if env_file is not None:
            self.__env_file = env_file
        self.__load()

    def __load(self):
        if self.__envs is None:
            dotenv.load_dotenv(self.__env_file)
            self.__envs = os.environ
        self.MAX_NUMBER_OF_MESSAGES = int(
            self.__envs.get('MAX_NUMBER_OF_MESSAGES', 5))
        self.WAIT_TIME_SECONDS = int(
            self.__envs.get('WAIT_TIME_SECONDS', 20))
        self.VISIBILITY_TIMEOUT = int(
            self.__envs.get('VISIBILITY_TIMEOUT', 30))
        self.AWS_CLIENT_URL = self.__envs.get('AWS_CLIENT_URL', None)
        self.AWS_REGION_NAME = self.__envs.get('AWS_REGION_NAME', 'us-east-2')
        self.SLEEP_BETWEEN_MESSAGES_SECONDS = int(
            self.__envs.get('SLEEP_BETWEEN_MESSAGES_SECONDS', 10))
        self.ERROR_SLEEP_SECONDS = int(
            self.__envs.get('ERROR_SLEEP_SECONDS', 5))
        logging.info(
            f'Config loaded: {self.__envs}, env_file: {self.__env_file}')
