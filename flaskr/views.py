from flask import render_template, request
from . import app, db
from.models import *


@app.route('/')
def hello():
    try:
        users = User.query.all()
    except:
        users = []
    return render_template('index.html', users=users)


@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        # TODO: add proper handling
        username = request.data
        username = 'admin'
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        return 'OK'
    except Exception as e:
        return str(e)
