from flask import Flask, render_template, request, session, flash, url_for
from flask_mail import Mail, Message
import os, json, re, flask_sijax
from resources import *

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kjhscollegeindex@gmail.com'
app.config['MAIL_PASSWORD'] = 'GoRams!!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
flask_sijax.Sijax(app)

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
        password = hash(request.form.get('inputPassword'))
        if username in USERDATA.keys() and USERDATA[username]["password"] == password:
            session['user'] = username
            session['name'] = USERDATA[username]["name"]
            flash("Logged In!")
            return main()
        return render_template('login.html', session=session, error=True)
    return render_template('login.html', session=session, error=False)

@app.route("/logout", methods=['GET'])
def logout():
    bkgdcolor = session['bkgd']
    session.clear()
    session['bkgd'] = bkgdcolor
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

@app.route("/bkgdblue", methods=['GET', 'POST'])
def bkgdblue():
    session['bkgd'] = "blue"
    return settings()

@app.route("/bkgdgreen", methods=['GET', 'POST'])
def bkgdgreen():
    session['bkgd'] = "green"
    return settings()

@app.route("/bkgdsunset", methods=['GET', 'POST'])
def bkgdsunset():
    session['bkgd'] = "sunset"
    return settings()

@app.route("/bkgdcity", methods=['GET', 'POST'])
def bkgdcity():
    session['bkgd'] = "city"
    return settings()

@app.route("/bkgdclouds", methods=['GET', 'POST'])
def bkgdclouds():
    session['bkgd'] = "clouds"
    return settings()

@app.route("/bkgdmountains", methods=['GET', 'POST'])
def bkgdmountains():
    session['bkgd'] = "mountains"
    return settings()

@app.route("/bkgdtartan", methods=['GET', 'POST'])
def bkgdtartan():
    session['bkgd'] = "tartan"
    return settings()

@app.route("/bkgdplaid", methods=['GET', 'POST'])
def bkgdplaid():
    session['bkgd'] = "plaid"
    return settings()

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)

# Old bkgd http://www.zastavki.com/pictures/originals/2014/Nature___Seasons___Summer_White_clouds_and_green_field_083051_.jpg