from flask import Flask, session, url_for, make_response
import json, hashlib, codecs, re
from functools import wraps, update_wrapper
from datetime import datetime


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

# College Search Algorithm
def search(key, array):
    results = []
    for item in array:
        if key.lower() in item.lower():
            results.append(item)
    return results

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return update_wrapper(no_cache, view)