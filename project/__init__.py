from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
app.secret_key=app.config.get('SECRET_KEY')

from project import views, models
