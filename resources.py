from flask import Flask, session, url_for, make_response
import json, hashlib, codecs, re, random
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
    json.dump(data, open(filename, 'w'), sort_keys=True, indent=3)

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

def verify_submission(text): # 0 means successful, positive integers represent error codes  
    if len(text) < 100:
        print("register: return-code 1.0")
        return 1
    elif len(text.split()) > 150:
        print("register: return-code 2.0")
        return 2
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

# Calculate user ranking:
def level(user, schooldata):
    ranking = 0
    for school in schooldata:
        for review in schooldata[school]["Reviews"]:
            if review == user:
                for rating in schooldata[school]["Reviews"][review]["Ratings"]:
                    ranking += schooldata[school]["Reviews"][review]["Ratings"][rating]
    if ranking < 0: # normalize negatives
        ranking = 0
    print("Ranking = " + str(ranking))
    return (2*ranking+(1/4))**(1/2)-(1/2)

# Stop caching Schools.json
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

""" #Random crap from messing around with sqlite:
def setupDB():
    cur = CONNECT.cursor()

    #cur.execute("CREATE TABLE schools (name TEXT, city TEXT, state TEXT, lat REAL, lon REAL)")
    #cur.execute("CREATE TABLE reviews (user TEXT, school TEXT, content TEXT, base INTEGER)")
    #cur.execute("CREATE TABLE ratings (user TEXT, author TEXT, school TEXT, sign BOOLEAN)")

    # Populate school data
    #for school in SCHOOLDATA:
    #    data = [(school, SCHOOLDATA[school]["City"], SCHOOLDATA[school]["State"], SCHOOLDATA[school]["Lat"], SCHOOLDATA[school]["Lon"])]
    #    cur.executemany("INSERT INTO schools (name, city, state, lat, lon) VALUES (?, ?, ?, ?, ?)", data)

    num = cur.execute("SELECT COUNT(*) FROM reviews").fetchall()[0][0]
    print(num)
    CONNECT.commit()
    CONNECT.close()
"""


"""
Module that provides a class that filters profanities
by leoluk
"""
class ProfanitiesFilter(object):
    def __init__(self, ignore_case=True, replacements="$@%-?!", 
                 complete=True, inside_words=False):
        """
        Inits the profanity filter.

        ignore_case -- ignore capitalization
        replacements -- string with characters to replace the forbidden word
        complete -- completely remove the word or keep the first and last char?
        inside_words -- search inside other words?

        """

        # This is embarrassing enough as it is. Just dont.
        self.badwords = [
        '2g1c', '2 girls 1 cup', 'acrotomophilia', 'anal', 'anilingus', 'anus', 'arsehole', 'ass', 'asshole', 'assmunch', 'auto erotic', 'autoerotic', 'babeland', 'baby batter', 'ball gag', 'ball gravy', 'ball kicking', 'ball licking', 'ball sack', 'ball sucking', 'bangbros', 'bareback', 'barely legal', 'barenaked', 'bastardo', 'bastinado', 'bbw', 'bdsm', 'beaver cleaver', 'beaver lips', 'bestiality', 'bi curious', 'big black', 'big breasts', 'big knockers', 'big tits', 'bimbos', 'birdlock', 'bitch', 'black cock', 'blonde action', 'blonde on blonde action', 'blow j', 'blow your l', 'blue waffle', 'blumpkin', 'bollocks', 'bondage', 'boner', 'boob', 'boobs', 'booty call', 'brown showers', 'brunette action', 'bukkake', 'bulldyke', 'bullet vibe', 'bung hole', 'bunghole', 'busty', 'butt', 'buttcheeks', 'butthole', 'camel toe', 'camgirl', 'camslut', 'camwhore', 'carpet muncher', 'carpetmuncher', 'chocolate rosebuds', 'circlejerk', 'cleveland steamer', 'clit', 'clitoris', 'clover clamps', 'clusterfuck', 'cock', 'cocks', 'coprolagnia', 'coprophilia', 'cornhole', 'cum', 'cumming', 'cunnilingus', 'cunt', 'darkie', 'date rape', 'daterape', 'deep throat', 'deepthroat', 'dick', 'dildo', 'dirty pillows', 'dirty sanchez', 'dog style', 'doggie style', 'doggiestyle', 'doggy style', 'doggystyle', 'dolcett', 'domination', 'dominatrix', 'dommes', 'donkey punch', 'double dong', 'double penetration', 'dp action', 'eat my ass', 'ecchi', 'ejaculation', 'erotic', 'erotism', 'escort', 'ethical slut', 'eunuch', 'faggot', 'fecal', 'felch', 'fellatio', 'feltch', 'female squirting', 'femdom', 'figging', 'fingering', 'fisting', 'foot fetish', 'footjob', 'frotting', 'fuck', 'fucking', 'fuck buttons', 'fudge packer', 'fudgepacker', 'futanari', 'g-spot', 'gang bang', 'gay sex', 'genitals', 'giant cock', 'girl on', 'girl on top', 'girls gone wild', 'goatcx', 'goatse', 'gokkun', 'golden shower', 'goo girl', 'goodpoop', 'goregasm', 'grope', 'group sex', 'guro', 'hand job', 'handjob', 'hard core', 'hardcore', 'hentai', 'homoerotic', 'honkey', 'hooker', 'hot chick', 'how to kill', 'how to murder', 'huge fat', 'humping', 'incest', 'intercourse', 
        'jack off', 'jail bait', 'jailbait', 'jerk off', 'jigaboo', 'jiggaboo', 'jiggerboo', 'jizz', 'juggs', 'kike', 'kinbaku', 'kinkster', 'kinky', 'knobbing', 'leather restraint', 'leather straight jacket', 'lemon party', 'lolita', 'lovemaking', 'make me come', 'male squirting', 'masturbate', 'menage a trois', 'milf', 'missionary position', 'motherfucker', 'mound of venus', 'mr hands', 'muff diver', 'muffdiving', 'nambla', 'nawashi', 'negro', 'neonazi', 'nig nog', 'nigga', 'nigger', 'nimphomania', 'nipple', 'nipples', 'nsfw images', 'nude', 'nudity', 'nympho', 'nymphomania', 'octopussy', 'omorashi', 'one cup two girls', 'one guy one jar', 'orgasm', 'orgy', 'paedophile', 'panties', 'panty', 'pedobear', 'pedophile', 'pegging', 'penis', 'phone sex', 'piece of shit', 'piss pig', 'pissing', 'pisspig', 'playboy', 'pleasure chest', 'pole smoker', 'ponyplay', 'poof', 'poop chute', 'poopchute', 'porn', 'porno', 'pornography', 'prince albert piercing', 'pthc', 'pubes', 'pussy', 'queaf', 'raghead', 'raging boner', 'rape', 'raping', 'rapist', 'rectum', 'reverse cowgirl', 'rimjob', 'rimming', 'rosy palm', 'rosy palm and her 5 sisters', 'rusty trombone', 's&m', 'sadism', 'scat', 'schlong', 'scissoring', 'semen', 'sex', 'sexo', 'sexy', 'shaved beaver', 'shaved pussy', 'shemale', 'shibari', 'shit', 'shota', 'shrimping', 'slanteye', 'slut', 'smut', 'snatch', 'snowballing', 'sodomize', 'sodomy', 'spic', 'spooge', 'spread legs', 'strap on', 'strapon', 'strappado', 'strip club', 'style doggy', 'suck', 'sucks', 'suicide girls', 'sultry women', 'swastika', 'swinger', 'tainted love', 'taste my', 'tea bagging', 'threesome', 'throating', 'tied up', 'tight white', 'tit', 'tits', 'titties', 'titty', 'tongue in a', 'topless', 'tosser', 'towelhead', 'tranny', 'tribadism', 'tub girl', 'tubgirl', 'tushy', 'twat', 'twink', 'twinkie', 'two girls one cup', 'undressing', 'upskirt', 'urethra play', 'urophilia', 'vagina', 'venus mound', 'vibrator', 'violet blue', 'violet wand', 'vorarephilia', 'voyeur', 'vulva', 'wank', 'wet dream', 'wetback', 'white power', 'women rapping', 'wrapping men', 'wrinkled starfish', 'xx', 'xxx', 'yaoi', 'yellow showers', 'yiffy', 'zoophilia'
        ]

        self.ignore_case = ignore_case
        self.replacements = replacements
        self.complete = complete
        self.inside_words = inside_words

    def _make_clean_word(self, length):
        """
        Generates a random replacement string of a given length
        using the chars in self.replacements.

        """
        return ''.join([random.choice(self.replacements) for i in
                  range(length)])

    def __replacer(self, match):
        value = match.group()
        if self.complete:
            return self._make_clean_word(len(value))
        else:
            return value[0]+self._make_clean_word(len(value)-2)+value[-1]

    def clean(self, text):
        """Cleans a string from profanity."""
        regexp_insidewords = {
            True: r'(%s)',
            False: r'\b(%s)\b',
            }
        regexp = (regexp_insidewords[self.inside_words] % 
                  '|'.join(self.badwords))
        r = re.compile(regexp, re.IGNORECASE if self.ignore_case else 0)
        return r.sub(self.__replacer, text)
