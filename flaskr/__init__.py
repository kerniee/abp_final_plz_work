from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import sys
import os

logging.basicConfig(level=logging.DEBUG)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    return


# To make pyinstaller work
if getattr(sys, 'frozen', False):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    template_folder = os.path.join(base_path, 'templates')
    static_folder = os.path.join(base_path, 'static')
    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder)
else:
    app = Flask(__name__)
    base_path = app.instance_path
    app.logger.info('Use normal')


# Not working in pyinstaller
# app.config.from_object('config')
# app.config.from_pyfile('config.py')

app.config.update(
    DEBUG=True,
    SQLALCHEMY_ECHO=True,
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(base_path, 'sqlite.db')
)

db = SQLAlchemy(app)

from . import views, models
