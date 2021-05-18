from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pymongo

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qna.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

questions_db_client = pymongo.MongoClient("mongodb://localhost:27017/")
questions_db = questions_db_client["vscribe"]
questions_collection = questions_db["qna"]

from vscribe import routes
from vscribe.models import *
db.create_all()