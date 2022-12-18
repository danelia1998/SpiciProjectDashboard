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
app.config['MAIL_USERNAME'] = 'spicisender@gmail.com'
app.config['MAIL_PASSWORD'] = 'BES5vjImrKWk1Gxq'
mail = Mail(app);

def userTable():
    with sqlite3.connect('tableData.db') as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Clients")
        rows = cur.fetchall()
        return render_template('dataTemplate.html', rows=rows)

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

def createDataTable():
    with sqlite3.connect('tableData.db') as db:
        cursor = db.cursor()
        cursor.execute("""	CREATE TABLE IF NOT EXISTS Clients(
						Name text,
						Surname text,
						Age text,
						Company text,
						Email text,
						Title text,
						PhoneNumber text,
						Primary Key(Email))
				""")
        db.commit()
    print('CREATE')

create()
createDataTable()

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/addNew')
def addNew():
    return render_template('newContact.html')

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

@app.route('/tableData')
def insert():
    with sqlite3.connect('tableData.db') as db:
        cursor = db.cursor()
        cursor.execute("""	INSERT INTO Clients (Name, Surname, Age, Company, Email, Title, PhoneNumber)
						VALUES ("Davit", "Danelia", "23", "Microsoft", "davit.danelia.2@btu.edu.ge", "SDET", "557345566")
				""")
        cursor.execute("""	INSERT INTO Clients (Name, Surname, Age, Company, Email, Title, PhoneNumber)
        						VALUES ("Kvicha", "Kvarackhelia", "20", "Football", "Kvarackhelia@gmail.com", "Footballer", "557111111")
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
        db.commit();
        return render_template('newContact.html')
    # return request.form['uname'] + ' added'

@app.route('/addContact', methods=['POST'])
def addContact():
    with sqlite3.connect('tableData.db') as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO Clients (Name, Surname, Age, Company, Email, Title, PhoneNumber) VALUES (?,?,?,?,?,?,?)",
                       (request.form['Name'], request.form['Surname'], request.form['Age'], request.form['Company'],
                        request.form['Email'], request.form['Title'], request.form['PhoneNumber']))
        db.commit();
        return userTable();
    # return request.form['uname'] + ' added'

@app.route('/verify', methods=['POST'])
def verify():
    with sqlite3.connect('login.db') as db:
        cursor = db.cursor();
        cursor.execute("SELECT * FROM Users WHERE Email=? AND Password=?",
                       (request.form['uname'], request.form['psw']))
        result = cursor.fetchall()
        if len(result) == 0:
            return 'email / password not recognised'
        else:
            session.permanent = True
            session['email'] = request.form['uname']
            return userTable();
            # return 'welcome ' + request.form['uname']

@app.route('/un')
def un():
    if 'email' in session:
        return 'Logged in as %s' % escape(session['email'])
    return render_template('main.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('un'))

