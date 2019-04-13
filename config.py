# from app.creds import email_creds, ms_translator
from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    # prefer secret keys set at the environment level, providing an alternative if that doesn't exist
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # use the environment's db url; if missing, use this sqlite path
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')

    # should SQLAlchemy send a notification to the app every time an object changes?
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # email server config.  For virtual server: python -m smtpd -n -c DebuggingServer localhost:8025
    MAIL_SERVER = os.environ.get('MAIL_SERVER')  # or 'smtp.gmail.com'

    MAIL_PORT = int(os.environ.get('MAIL_PORT')) or 25  # default port for non-SSL email
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [os.environ.get('ADMINS')]

    if MAIL_SERVER != 'smtp.gmail.com':
        MAIL_PORT = int(os.environ.get('MAIL_PORT')) or 25  # default port for non-SSL email
        MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None

    POSTS_PER_PAGE = 10
    LANGUAGES = ['en', 'es']

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY') or None
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL') or None
