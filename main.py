from flask import Flask, render_template, session, redirect, url_for, request
from flask_mail import Mail, Message
import sqlite3
import os
from markupsafe import escape
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)
app.config['MAIL_SERVER'] = 'smtp-relay.sendinblue.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'daneliatemur@gmail.com'
app.config['MAIL_PASSWORD'] = 'CYPVpav51nOKzbxU'

mail = Mail(app)


@app.route('/')
def home():
    return render_template('main.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/passwordRecovery', methods=['GET', 'POST'])
def password_recovery():

    if request.method == 'POST':
        with sqlite3.connect('login.db') as db:
            print(request.form['uname'])
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Users WHERE Email=?", [request.form['uname']])
            result = cursor.fetchall()
            print(result[0])
            first = result[0][1]
            print(first)
        msg = Message('Password Reset', sender='noreply@demo.com', recipients=['daneliatemur@gmail.com'])
        msg.body = "Hi! There was a request to change your password! Your password is : " + first
        mail.send(msg)
        return 'SENT EMAIL'
    return render_template('forgotPassword.html')


def create():
    with sqlite3.connect('login.db') as db:
        cursor = db.cursor()
        cursor.execute("""	CREATE TABLE IF NOT EXISTS Users(
						Email text,
						Password text,
						Primary Key(Email))
				""")
        db.commit()
    print('CREATE')


create()


@app.route('/insert')
def insert():
    with sqlite3.connect('login.db') as db:
        cursor = db.cursor()
        cursor.execute("""	INSERT INTO Users (Email, Password)
						VALUES ("danelia@gmail.com", "1234567dd")
				""")
        db.commit()
    return 'INSERT'


@app.route('/select')
def select():
    try:
        with sqlite3.connect('login.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Users")
            result = cursor.fetchall()
            if len(result) == 0:
                return 'no records'
            else:
                return ','.join(map(str, result))
    except Exception as e:
        return str(e)


@app.route('/add', methods=['POST'])
def add():
    with sqlite3.connect('login.db') as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO Users (Email, Password) VALUES (?,?)",
                       (request.form['uname'], request.form['psw']))
        db.commit()
    return request.form['uname'] + ' added'


@app.route('/verify', methods=['POST'])
def verify():
    with sqlite3.connect('login.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Users WHERE Email=? AND Password=?",
                       (request.form['uname'], request.form['psw']))
        result = cursor.fetchall()
        if len(result) == 0:
            return 'email / password not recognised'
        else:
            session.permanent = True
            session['email'] = request.form['uname']
            return 'welcome ' + request.form['uname']


# @app.route('/table')
# def select():
# 	con = sqlite3.connect('login.db')
# 	cur = con.cursor()
# 	cur.execute("SELECT * FROM Users")
# 	rows = cur.fetchall()
# 	return render_template('table.html', rows=rows)

@app.route('/un')
def un():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['email'])
    return 'You are not logged in'


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('un'))
