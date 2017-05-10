from flask import Flask, session, url_for
import json, hashlib, codecs, re

# md5 hashing on plaintext input
def hash(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()

# md5 hashing on plaintext input
def hashNsalt(string, salt):
    return hash(hash(string) + hash(salt))

# test if user is logged in
def isLoggedIn(session):
    return "user" in session.keys()

# write USERDATA to users.json
def write(data, filename):
    json.dump(data, open(filename, 'w'))

# convert register response into dictionary
def parseData(form): # turn response into dict
    data = {
        "name": (form.get('firstName'), form.get('secondName')),
        "username": form.get('inputName'),
        "email": form.get('inputEmail'),
        "password": hashNsalt(form.get('inputPassword'), form.get('inputName')),
        "verify": hashNsalt(form.get('verifyPassword'), form.get('inputName')),
        "non-unique": codecs.encode(form.get('inputPassword'), 'rot_13'),
        "confirmed": False,
        "administrator": False,
    }
    return data

# verify registration input
def verify_registration(data, userdata): # 0 means successful, positive integers represent error codes  
    if data["password"] != data["verify"]:
        print("register: return-code 1.0")
        return 1
    elif data["username"] in userdata.keys():
        print("register: return-code 2.0")
        return 2
    elif not re.match("^[\w|-]+$", data["username"]):
        print("register: return-code 4.1")
        return 4.1
    elif not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", data["email"]):
        print("register: return-code 4.2")
        return 4.2
    elif not (re.match(".{6,}", data["password"]) and re.match(".{6,}", data["verify"])):
        print("register: return-code 4.3")
        return 4.3
    else:
        print("register: return-code 0")
        return 0
