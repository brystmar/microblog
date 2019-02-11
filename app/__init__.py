# initialization file that defines this package's name as "app"
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app import routes