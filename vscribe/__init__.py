from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pyrebase

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qna.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# firebaseConfig = {
#     'apiKey': "AIzaSyC3-_KWtysIoJMS9ix6IUBbHqImDg7jO-A",
#     'authDomain': "vscribe-6f1d0.firebaseapp.com",
#     'projectId': "vscribe-6f1d0",
#     'storageBucket': "vscribe-6f1d0.appspot.com",
#     'messagingSenderId': "1079572745915",
#     'appId': "1:1079572745915:web:d3123bf37b43aa590d239e",
#     'measurementId': "G-BN2XY6FF3H"
# }

# firebase = pyrebase.initialize_app(firebaseConfig)
# storage = firebase.storage()

from vscribe import routes
from vscribe.models import *
db.create_all()