# initialization file that defines this package's name as "app"
import os
import logging
from flask import Flask, request
from config import Config
from flask_babel import Babel, lazy_gettext as _l
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import SMTPHandler, RotatingFileHandler

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')
db = SQLAlchemy(app)
babel = Babel(app)
bootstrap = Bootstrap(app)
mail = Mail(app)
migrate = Migrate(app, db)
moment = Moment(app)

# error logging
if not app.debug:  # don't send emails when in debug mode.  To use a virtual server instead: python -m smtpd -n -c DebuggingServer localhost:8025
    # specify email details
    if app.config['MAIL_SERVER']:  # ensure there's an email server configured
        auth = None

        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

        if app.config['MAIL_USE_TLS']:
            secure = ()
        else:
            secure = None

        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Error',
            credentials=auth, secure=secure)

        # set the write level to 'error'
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # specify parameters for writing to the log file
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # set the write level to 'info'
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


from app import routes, models, errors
