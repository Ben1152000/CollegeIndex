from flask import Flask, render_template, request, session, flash, url_for
from flask_mail import Mail, Message
import os, json, re, flask_sijax
from resources import *

app = Flask(__name__)

# Configure Email Server
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kjhscollegeindex@gmail.com'
app.config['MAIL_PASSWORD'] = 'GoRams!!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Implement Sijax
path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
flask_sijax.Sijax(app)

# Open json files
USERDATA = json.load(open('users.json'))
SCHOOLDATA = json.load(open('static/data/schools.json'))

@app.route("/")
def main():
    return render_template('home.html', session=session)

@app.route("/about")
def about():
    return render_template('about.html', session=session)

@app.route("/settings")
def settings():
    return render_template('settings.html', session=session)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = parseData(request.form)
        result = verify_registration(data, USERDATA)
        if result != 0:
            return render_template('register.html', session=session, error=result)
        else:
            if "verify" in data: del data["verify"]
            USERDATA[data["username"]] = data
            write(USERDATA, 'users.json')
            session['user'] = data["username"]
            session['name'] = data["name"]
            return main()
    return render_template('register.html', session=session, error=0)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('inputName')
        password = hashNsalt(request.form.get('inputPassword'), username)
        if username in USERDATA.keys() and USERDATA[username]["password"] == password:
            session['user'] = username
            session['name'] = USERDATA[username]["name"]
            flash("Logged In!")
            return main()
        return render_template('login.html', session=session, error=True)
    return render_template('login.html', session=session, error=False)

@app.route("/logout", methods=['GET'])
def logout():
    if "bkgd" in session.keys():
        bkgdcolor = session['bkgd']
        session.clear()
        session['bkgd'] = bkgdcolor
    else:
        session.clear()
    return main()

@app.route("/submit", methods=['GET', 'POST'])
def submit():
    if isLoggedIn(session):
        if USERDATA[session['user']]["confirmed"] == True:
            print("YEY")
            if request.method == 'POST':
                name = request.form.get('name')
                return render_template('thanks.html', session=session)
            return render_template('submit.html', session=session, data=sorted(SCHOOLDATA.keys()))
        print(USERDATA[session['user']]["confirmed"])
        return confirm()
    return main()

@app.route("/account")
def account():
    if isLoggedIn(session):
        return render_template('account.html', session=session)
    return main()

@app.route("/send-confirmation")
def send_confirmation():
    if isLoggedIn(session):
        code = hash(session["user"])[:5]
        msg = Message("Confirm your account",
                    sender="kjhscollegeindex@gmail.com",
                    body = session["name"][0] + ",\n\nThank you for signing up at College Index!\nHere is your confirmation code: " + code + "\n\nThanks,\nBen Darnell",
                    recipients=["benjamindarnell00@gmail.com"])
        mail.send(msg)
        return confirm()
    return main()

@app.route("/confirm", methods=['GET', 'POST'])
def confirm():
    if isLoggedIn(session):
        if request.method == 'POST':
            username = session['user']
            if request.form.get('confirmCode') == hash(USERDATA[session['user']]["username"])[:5]:
                USERDATA[session['user']]["confirmed"] = True
                write(USERDATA, "users.json")
                return render_template('submit.html', session=session, data=sorted(SCHOOLDATA.keys()))
            return render_template('confirm.html', session=session, error=1)
        return render_template('confirm.html', session=session, error=0)
    return main()

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    #app.run(debug=True, host="192.168.2.147")
    app.run(debug=True)