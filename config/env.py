from os import environ
from pathlib import Path

from dotenv import load_dotenv, dotenv_values

load_dotenv()


class Env:
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent.parent.resolve()
        env_vars = environ.items() | dotenv_values(self.BASE_DIR / 'config/config.env').items()
        [setattr(self, k, v) for k, v in env_vars]

    def __getattr__(self, item):
        if item in environ:
            setattr(self, item, (value := environ[item]))
            return value


env = Env()
