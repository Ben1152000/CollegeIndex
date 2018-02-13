from flask import Flask, render_template, request, session, flash, url_for, send_from_directory
from flask_mail import Mail, Message
import os, json, re, flask_sijax, math, sqlite3, subprocess
from geocoder import google
from resources import *

app = Flask(__name__)

# Read API Keys
MAPKEY = open("APIkeys.txt").read().split()[0]
GEOKEY = open("APIkeys.txt").read().split()[1]
EMAILPASS = open("APIkeys.txt").read().split()[2]

# Configure Email Server
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kjhscollegeindex@gmail.com'
app.config['MAIL_PASSWORD'] = EMAILPASS
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
SCHOOLDATA = json.load(open('data/schools.json'))

# Set up SQL Database
CONNECT = sqlite3.connect('data/schools.db', timeout=20)

# Create profanity filter
FILTER = ProfanitiesFilter()

@app.route("/")
def main():
    return render_template('home.html', session=session, key=MAPKEY)

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
            # Tell session that user is logged in:
            print(data, data["username"])
            session['user'] = data["username"]
            session['name'] = data["name"]
            if "verify" in data: del data["verify"] # Don't store the verified password!
            if "username" in data: del data["username"] # Username is key, not value
            USERDATA[session['user']] = data # Add user data to file
            write(USERDATA, 'users.json')
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
            if request.method == 'POST':
                school = request.form.get('name')
                text = request.form.get('review')
                result = verify_submission(school, text)
                if result != 0:
                    return render_template('submit.html', session=session, error=result, data=sorted(SCHOOLDATA.keys()))
                else:
                    school = request.form.get('name')
                    name = session['user']
                    ratings = [int(request.form.get('taste')), int(request.form.get('texture')), int(request.form.get('tummy feel'))]
                    review = FILTER.clean(request.form.get('review')) # Hit it with dat filter
                    base = math.floor(level(name, SCHOOLDATA))
                    SCHOOLDATA[school]["Reviews"][name] = {"Taste": ratings[0], "Texture": ratings[1], "Tummy Feel": ratings[2], "Review": review, "Base Rating": base, "Ratings": { name: 1 }}
                    write(SCHOOLDATA, "data/schools.json")
                    return render_template('thanks.html', session=session)
            return render_template('submit.html', session=session, data=sorted(SCHOOLDATA.keys()))
        print(USERDATA[session['user']]["confirmed"])
        return confirm()
    return register()

@app.route("/account")
def account():
    if isLoggedIn(session):
        userlevel = math.floor(level(session['user'], SCHOOLDATA))
        print("Level = " + str(userlevel))
        progress = (level(session['user'], SCHOOLDATA) - userlevel) * 100 + 0.1
        return render_template('account.html', session=session, level=userlevel, progress=progress)
    return main()

@app.route("/send-confirmation")
def send_confirmation():
    if isLoggedIn(session):
        code = hash(session["user"])[:5]
        msg = Message("Confirm your account",
                    sender="kjhscollegeindex@gmail.com",
                    body = session["name"][0] + ",\n\nThank you for signing up at College Index!\nHere is your confirmation code: " + code + "\n\nThanks,\nBen Darnell",
                    recipients=[USERDATA[session['user']]["email"]])
        mail.send(msg)
        return render_template('confirm.html', session=session, error=0)
    return main()

@app.route("/confirm", methods=['GET', 'POST'])
def confirm():
    if isLoggedIn(session):
        if request.method == 'POST':
            username = session['user']
            if request.form.get('confirmCode') == hash(session['user'])[:5]:
                USERDATA[session['user']]["confirmed"] = True
                write(USERDATA, "users.json")
                return render_template('submit.html', session=session, data=sorted(SCHOOLDATA.keys()))
            return render_template('confirm.html', session=session, error=1)
        return send_confirmation()
    return main()

@app.route("/newschool", methods=['GET', 'POST'])
def newschool():
    if isLoggedIn(session):
        if request.method == 'POST':
            if True: # Feature temporarily disabled
                return render_template('newschool.html', session=session, error=1)
            name = request.form.get("schoolName")
            address = request.form.get("inputAddress")
            city = request.form.get("inputCity")
            state = request.form.get("inputState")
            fullAddress = address + ", " + city + ", " + state
            latlng = google(fullAddress, key=GEOKEY).latlng
            print({"City": city, "State": state, "Lat": latlng[0], "Lon": latlng[1], "Reviews": {}})
            SCHOOLDATA[name] = {"City": city, "State": state, "Lat": latlng[0], "Lon": latlng[1], "Reviews": {}}
            write(SCHOOLDATA, "data/schools.json")
        return render_template('newschool.html', session=session)
    return register()

@app.route('/data/<path:filepath>')
@nocache # stops data caching
def data(filepath):
    return send_from_directory('data', filepath)

@app.route('/downvote', methods=['POST'])
def downvote():
    school = request.form["School"]
    user = request.form["User"]
    author = request.form["Review"]
    if user in SCHOOLDATA[school]["Reviews"][author]["Ratings"] and SCHOOLDATA[school]["Reviews"][author]["Ratings"][user] == -1:
        del SCHOOLDATA[school]["Reviews"][author]["Ratings"][user]
    else:
        SCHOOLDATA[school]["Reviews"][author]["Ratings"][user] = -1
    write(SCHOOLDATA, "data/schools.json")
    return json.dumps({})

@app.route('/upvote', methods=['POST'])
def upvote():
    school = request.form["School"]
    user = request.form["User"]
    author = request.form["Review"]
    if user in SCHOOLDATA[school]["Reviews"][author]["Ratings"] and SCHOOLDATA[school]["Reviews"][author]["Ratings"][user] == 1:
        del SCHOOLDATA[school]["Reviews"][author]["Ratings"][user]
    else:
        SCHOOLDATA[school]["Reviews"][author]["Ratings"][user] = 1
    write(SCHOOLDATA, "data/schools.json")
    return json.dumps({})

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    host = str(subprocess.check_output(['ipconfig', 'getifaddr', 'en0']))[2:-3] # change host to equal "localhost" when offline
    app.run(debug=True, use_reloader=False, host=host, port="5000") # change use_reloader to True when running
    