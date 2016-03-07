# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin

from werkzeug.contrib.fixers import ProxyFix

# App initialization
app = Flask(__name__)
app.config.from_object('config')
app.wsgi_app = ProxyFix(app.wsgi_app)

# Logging with Rotating File Setup
handler = RotatingFileHandler(app.config.get('LOG_FILE'), maxBytes=10000, backupCount=5)
handler.setLevel(logging.DEBUG)
handler.setFormatter(
    logging.Formatter(fmt='%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s', datefmt='%b %d %H:%M:%S')
)
app.logger.addHandler(handler)

# Login manager initialization
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'
login_manager.session_protection = 'strong'

# Database initilization
db = SQLAlchemy(app)


# Admin initialization
from app.models import AuthIndex
from app.models import UserView

admin = Admin(app, 'Ansen Admin', index_view=AuthIndex(), template_mode='bootstrap3')

admin.add_view(UserView(db.session, endpoint='user'))

# Importing the views
from app.views import *
