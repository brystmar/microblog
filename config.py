import os

class Config(object):
    # prefer secret keys set at the environment level, providing an alternative if that doesn't exist
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'