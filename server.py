#!/usr/bin/python3
# -*- coding: utf-8 -*-
#heartranked is FREEDOM SOFTWARE by King Robin Johannes
#don't worry, information want's to be free. nobody can stop it. Bless.

import time, datetime, os, sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import json
import requests
import subprocess
import web
import hashlib
import random
import markdown
import re
import unicodedata
import urllib
from pathlib import Path
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.oggvorbis import OggVorbis
from PIL import Image
from PIL import ImageSequence
import settings

urls = (
    '/?','heartranked',
    '/trust', 'trust',
    "/stats?", "stats",
    "/login?", "login",
    "/logout", "logout",
    "/invites?", "invites",
    "/users","users",
    "/like?","like",
    "/imageapi?","imageapi",
    "/u/(.*)?", "user",
    "/forgotpass?", "forgotpass",
    "/register?", "register",
    "/tuning?", "tuning",
    '/editor?', 'editor',
    '/save', 'savepost',
    '/upload', 'upload',
    '/rendered', 'rendered',
    '/uploads?', 'uploads',
    '/p?', 'pull',
    '/c?', 'config')

#Load from settings
webmaster = settings.webmaster
baseurl = settings.baseurl
sitename = settings.sitename
siteslogan = settings.siteslogan
siteurl = baseurl
postadmin = settings.postadmin
postadmin_signature = settings.postadmin_signature
heart=settings.heart
hearted=settings.hearted
zipandship=settings.zipandship
#load msg
postadmin_msg_new=settings.postadmin_msg_new
postadmin_msg_new_long=settings.postadmin_msg_new_long
welcome=settings.welcome
welcome_long=settings.welcome_long
basedir = os.path.dirname(os.path.realpath(__file__))+'/'
templatedir = basedir + 'html/'
staticdir = basedir + 'static/'
web.config.debug = False
app = web.application(urls, globals())
store = web.session.DiskStore(basedir + 'sessions')
render = web.template.render(templatedir, base="base")
renderop = web.template.render(templatedir, base="op")
rendersplash = web.template.render(templatedir, base="splash")
session = web.session.Session(app,store,initializer={'login':0, 'privilege':0, 'bag':[], 'sessionkey':'empty','postid':'','backurl':'','user':'','search':'', 'bildsida':'', 'feedbase':'', 'timebase':'', 'usrfeed':'', 'saveto':''})

allowedchar = 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'

datetimeformat="%Y-%m-%d %H:%M:%S"

# --- Parameters (often called N, r, p) ---
# N (n): CPU/Memory cost factor. Must be a power of 2 (e.g., 2**14 = 16384).
# r: Block size factor (typically 8).
# p: Parallelization factor (typically 1).
# klen: Desired key length (e.g., 32 for a 256-bit key).
N_COST = 16384  # Adjust this for desired security/speed tradeoff
R_BLOCK_SIZE = 8
P_PARALLELIZATION = 1
KEY_LENGTH = 32

def runfirst():
    os.makedirs(basedir+'p/posts',exist_ok=True)
    os.makedirs(basedir+'p/zipped',exist_ok=True)
    os.makedirs(basedir+'p/comborank',exist_ok=True)
    os.makedirs(basedir+'p/heartrank',exist_ok=True)
    os.makedirs(basedir+'p/deleted',exist_ok=True)
    os.makedirs(basedir+'u/',exist_ok=True)
    os.makedirs(basedir+'r/',exist_ok=True)
    os.makedirs(basedir+'r/visitors',exist_ok=True)
    os.makedirs(basedir+'r/invites',exist_ok=True)
    os.makedirs(basedir+'r/trusted',exist_ok=True)
    os.makedirs(basedir+'r/users',exist_ok=True)
    os.makedirs(basedir+'r/stopflood',exist_ok=True)
    os.makedirs(basedir+'r/stopresetpass',exist_ok=True)

runfirst()

def hash_password(password: str) -> bytes:
    # 1. Generate a random, unique salt for each password
    salt = os.urandom(16) 
    # 2. Derive the key (hash)
    # The 'password' must be bytes, so we use .encode('utf-8')
    key = hashlib.scrypt(
        password.encode('utf-8'),
        salt=salt,
        n=N_COST,
        r=R_BLOCK_SIZE,
        p=P_PARALLELIZATION,
        dklen=KEY_LENGTH
    ) 
    # 3. Store the salt AND the key (hash) together
    return salt + key

def verify_password(stored_hash_with_salt: bytes, provided_password: str) -> bool:
    # 1. Separate the salt and the stored key
    salt = stored_hash_with_salt[:16] # Assuming 16 bytes for the salt
    stored_key = stored_hash_with_salt[16:]
    # 2. Re-derive the key from the provided password using the stored salt and parameters
    # **Crucially, use the exact same n, r, p, and dklen parameters!**
    try:
        derived_key = hashlib.scrypt(
            provided_password.encode('utf-8'),
            salt=salt,
            n=N_COST,
            r=R_BLOCK_SIZE,
            p=P_PARALLELIZATION,
            dklen=KEY_LENGTH
        )
        # 3. Compare the newly derived key with the stored key
        # Use a constant-time comparison (like `hmac.compare_digest` if available,
        # but Python's standard byte comparison is often okay here too)
        return derived_key == stored_key
    except ValueError:
        # This can happen if parameters like dklen are wrong during verification
        return False

def logged():
    if session.login > 0:
        return True
    else:
        return False

class createpost:
    def __init__(self, name, value):
        self.name = name
        self.value = value

def savetext(thename, description):
    with open(basedir+thename, "w") as f:
        f.write(description)

def savetofile(thename, description):
    with open(basedirthename, "w") as f:
        f.write(description)

def loadtext(thename):
    if os.path.exists(basedir+thename):
        with open(basedir+thename, 'r') as f:
            description = f.read()
        return description
    return ''

def savejson(name, thedict):
    #full path to filename
    #save to next line make an ID automatically, you have to check the save to know how to load it.
    #loadfile check if record exist, first in line is the record hash and update if it exists
    #make users in a folder as files first is username username will always be user record
    #hearts will be files as usernames with timestamp in a hearts folder in post folder. be stored and checked in u/hearts and post/hearts
    # be sure to add home domain setting to username
    #make save list a dict use same names
    print(thedict)
    print('this to be saved')
    thename=basedir+name
    if os.path.exists(thename):
        with open(thename, 'r') as f:
            p=json.load(f)
        print(p)
        print('this to be saved to')
        p.update(thedict)
        with open(thename, "w") as f:
            json.dump(p,f)
    else:
        with open(thename, "w") as f:
            #f.write(str(i) + ',')
            print('saving json')
            json.dump(thedict,f)

def loadjson(name):
    settings = ''
    thename=basedir+name
    if os.path.exists(thename):
        with open(thename, 'r') as f:
            settings = json.load(f)
            #for key, i in settings.items():
            #    createpost(key,i)
    return settings

def deletepost(thefile):
    os.system('rm '+thefile)

def adduser(name, password, mail):
    originalname=name
    name=safe_filename(name[:12])
    password_hashed=hash_password(password).hex()
    tot = len(os.listdir(basedir+'r/users/'))
    #print(password_hashed)
    print('users alltsomallt: ' + str(tot))
    if tot > 1:
        adminlevel=3
    else:
        adminlevel=5
    thedict={'name':name, 'displayname':originalname, 'password':password_hashed,'mail':mail,'adminlevel':adminlevel}
    savejson('r/users/'+name, thedict)
    #savetext('r/user/'+name,password_hashed)
    print("new user added")
    return

def updateuser(displayname, password, mail):
    password_hashed=hash_password(password).hex()
    tot = len(os.listdir(basedir+'r/users/'))
    thedict={'displayname':displayname, 'password':password_hashed,'mail':mail}
    savejson('r/users/'+session.user, thedict)
    print("user info updated")
    return

def safe_filename(name: str, max_length: int = 100, replacement: str = "-") -> str:
    """
    Convert a filename into a web-safe version.
    """
    if not name:
        return "file"
    #Normalize unicode (é → e, etc.)
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    #Replace spaces and common separators with the replacement char
    name = re.sub(r'[\s_]+', replacement, name)
    #Remove any character that is not alphanumeric, hyphen, underscore, or dot
    name = re.sub(r'[^a-zA-Z0-9.\-_]', '', name)
    #Replace multiple replacement chars with single one
    name = re.sub(re.escape(replacement) + r'+', replacement, name)
    #Remove leading/trailing replacement chars and dots
    name = name.strip(replacement + '.')
    #Prevent empty or hidden files
    if not name or name.startswith('.'):
        name = "file" + name
    #Enforce max length (leave room for extension)
    if len(name) > max_length:
        name = name[:max_length]
    return name.lower()

def adminlevel(user):
    level=loadjson('r/users/'+user)
    #1 session logout, web.py bug
    #2 rights to see pics and comment
    #3 rights to upoload
    #5 superadmin
    session.login = int(level['adminlevel'])
    return

def stopresetpass(mail):
    t = None
    if os.path.exists(basedir+'r/stopresetpass/'+mail) == True:
        t=loadjson('r/stopresetpass/'+mail)
    else:
        thedict={'timeadded':time.time()}
        savejson('r/stopresetpass/'+mail, thedict)
        return 
    thedict={'timeadded':time.time()}
    savejson('r/stopresetpass/'+mail, thedict)
    latest = time.time() - t['timeadded']
    print(latest)
    if latest < 600:
        print('mail is in password reset spam filter')
        return True
    else:
        return False

def stopflood(ip,referer):
    t = 0
    if os.path.exists(basedir+'r/stopflood/'+ip) == True:
        t=loadjson('r/stopflood/'+ip)
    else:
        thedict={'timeadded':time.time()}
        savejson('r/stopflood/'+ip, thedict)
        return
    thedict={'timeadded':time.time()}
    savejson('r/stopflood/'+ip, thedict)
    try:
        latest = time.time() - t
        print(latest)
    except:
        latest = 10
        pass
    if latest < 1:
        print('flooding recognized!')
        return True
    else:
        return False

def getinvitation(secretinvitation):
    os.makedirs(basedir+'r/invites/'+session.user+'/',exist_ok=True)
    invite=loadjson('r/invites/'+session.user+'/'+secretinvitation)
    print(invite)
    if invite['secretinvitekey'] == secretinvitation:
        return True
    return False

class trust():
    form = web.form.Form(
    web.form.Textbox('servername', web.form.notnull, description="server:"),
    web.form.Textbox('port', description="port:"),
    web.form.Textbox('user', web.form.notnull, description="user:"),
    web.form.Password('password', web.form.notnull, description="passcode:"),
    web.form.Button('Trust'))
    def GET(self):
        os.makedirs(basedir+'r/trusted/'+session.user+'/',exist_ok=True)
        i = web.input(remove=None)
        if i.remove != None:
            os.system('rm '+basedir+'r/trusted/'+session.user+'/'+i.remove)
            return web.seeother('/trust')
        trusted=os.listdir(basedir+'r/trusted/'+session.user+'/')
        trustedlist=[]
        for t in trusted:
            trusted=loadjson('r/trusted/'+session.user+'/'+t)
            trustedlist.append(trusted)
        trustform = self.form()
        return render.trust(trustform, trustedlist)
    def POST(self):
        i = web.input(port='')
        referer = web.ctx.env.get('HTTP_REFERER',baseurl)
        ip = web.ctx['ip']
        stopflood(ip, referer)
        loginform = self.form()
        i = web.input()
        #password_hashed=hash_password(i.password).hex()
        thedict={'servername':i.servername, 'port':i.port, 'user':i.user, 'password':i.password}
        savejson('r/trusted/'+session.user+'/'+i.servername,thedict)
        return web.seeother('/trust')

class login():
    form = web.form.Form(
    web.form.Textbox('user', web.form.notnull, description="your registered mail account:"),
    web.form.Password('password', web.form.notnull, description="and your passcode please:"),
    web.form.Button('Login'))
    def GET(self):
        users=os.listdir(basedir+'r/users/')
        if len(users) == 0:
            result = subprocess.run(['whoami'], capture_output=True, text=True)
            adduser('op', 'blessyou', result.stdout.rstrip()+'@localhost')
        visitorlog()
        fejl = ''
        resetpasslink = False
        i = web.input(error=None)
        if i.error == 'fejl':
            fejl = 'wrong passcode!'
            resetpasslink = True
        if i.error == 'tom':
            fejl = 'didnt work'
        if session.login < 3:
            loginform = self.form()
            return render.login(loginform, fejl, resetpasslink)
        if session.login == 3:
            return web.seeother('/')
        if session.login == 5:
            raise web.seeother('/')
    def POST(self):
        visitorlog()
        referer = web.ctx.env.get('HTTP_REFERER',baseurl)
        ip = web.ctx['ip']
        stopflood(ip, referer)
        loginform = self.form()
        i = web.input()
        if i.user == '' or i.password == '':
            raise web.seeother('/login?error=tom')
        rymdadmins = []
        users = os.listdir(basedir+'r/users/')
        for r in users:
            admin=loadjson('r/users/'+r)
            rymdadmins.append(admin)
        #if not rymdadmins:
        #    raise web.seeother('/register')
        for p in rymdadmins:
            if p['name'].lower() == i['user'].lower() or p['mail'].lower() == i['user'].lower():
                passcode=bytes.fromhex(p['password'])
                if verify_password(passcode,i.password):
                    session.user = p['name']
                    adminlevel(p['name'])
                    if session.login == 5:
                        print('ACCESS!')
                        raise web.seeother('/')
                    if session.backurl != '':
                        backurl = session.backurl
                        session.backurl = ''
                        raise web.seeother(backurl)
                    else:
                        raise web.seeother('/')
        return web.seeother('/login?error=fejl')

class register():
    form = web.form.Form(
    web.form.Textbox('invite', description="invitation code (do not edit):"),
    web.form.Textbox('user', description="name:"),
    web.form.Password('password', description="passcode:"),
    web.form.Textbox('mail', description="mail:"),
    web.form.Button('JOIN'))
    def GET(self):
        visitorlog()
        registerform = self.form()
        w = web.input(invite=None)
        formfail = ''
        n = ''
        m = ''
        if getinvitation(w.invite):
            try:
                if w.fail == 'namn':
                    formfail = 'hey, need a name. If ya don lik ya real name imagination buddy'
                if w.namn:
                    n = w.namn
                if w.epost:
                    m = w.epost
                elif w.epost == '':
                    formfail = 'we need an email, if u loose your passcode for example...'
                if w.fail == 'notmail':
                    formfail = 'uhm, this is not an email'
                elif w.fail == 'nametaken':
                    formfail = 'Name already taken'
                elif w.fail == 'mailtaken':
                    formfail = 'You already got a account on this email. Try reset your passcode'
                elif w.fail == 'kortlosen':
                    formfail = 'Too shoort passcode. Min 5 char.'
            except:
                pass
            totusers = len(os.listdir(basedir+'r/users/'))
            registerform.fill(user=urllib.parse.unquote_plus(n), mail=urllib.parse.unquote_plus(m), invite=w.invite)
            return render.register(registerform, formfail, totusers)
        else:
            return web.seeother('/oopsie')
    def POST(self):
        visitorlog()
        registerform = self.form()
        i = web.input(invite=None)
        if getinvitation(i.invite):
            r = '&namn=' + i.user + '&epost=' + i.mail
            urllib.parse.quote_plus(r)
            if i.user == '':
                raise web.seeother('/register?invite='+i.invite+'&fail=namn'+r)
            if '@' not in i.mail:
                raise web.seeother('/register?invite='+i.invite+'&fail=notmail'+r)
            if len(i.password) < 5:
                raise web.seeother('/register?invite='+i.invite+'&fail=kortlosen'+r)
            rymdadmins = []
            users = os.listdir(basedir+'r/users/')
            for r in users:
                admin=loadjson('r/users/'+r)
                rymdadmins.append(admin)
            for p in rymdadmins:
                if p['name'].lower() == i.user.lower():
                    raise web.seeother('/register?invite='+i.invite+'&fail=nametaken' +r)
                if p['mail'].lower() == i.mail.lower():
                    raise web.seeother('/register?invite='+i.invite+'&fail=mailtaken' +r)
            adduser(i.user, i.password, i.mail.lower())
            #Send mail (change messages in settings.py)
            sendmail(postadmin, postadmin_msg_new, postadmin_msg_new_long+i.user+' '+i.mail)
            #Send mail to new user
            sendmail(i.mail, welcome, welcome_long+i.user)
            #session.login = 3
            #session.user = safe_filename(i.user)
            #add user to matrix
            #os.system("register_new_matrix_user -u "+i.user+" -p "+i.password+" --no-admin -c /etc/matrix-synapse/homeserver.yaml") 
            return web.seeother('/login')
        else:
            raise web.seeother('/oopsie')

class welcome():
    def GET(self):
        if session.login > 2:
            backurl = ''
            if session.backurl != '':
                backurl = session.backurl
                session.backurl = ''
            return render.ny(session.user, backurl)

class like:
    def POST(self):
        if session.user != '':
            i = web.input(unlike=None, like=None, hate=None, unhate=None, user=None, imghash=None)
            user = i.user
            postid = i.imghash
            mail=''
            displayname=''
            rymdadmins=[]
            users = os.listdir(basedir+'r/users/')
            for r in users:
                admin=loadjson('r/users/'+r)
                rymdadmins.append(admin)
            for r in rymdadmins:
                if r['name']==session.user:
                    if 'displayname' in r:
                        displayname=r['displayname']
                    if 'mail' in r:
                        mail=r['mail']
            os.makedirs(basedir+'p/posts/'+postid+'/hearts/',exist_ok=True)
            os.makedirs(basedir+'p/heartrank/',exist_ok=True)
            os.makedirs(basedir+'u/'+session.user+'/posts/'+postid+'/hearts/',exist_ok=True)
            try:
                l = loadjson('p/posts/'+postid+'/hearts/'+session.user)
            except:
                l={}
            print(session.user)
            if l:
                user_likes = True
            else:
                user_likes = False
            if user_likes == False:
                try:
                    l=len(os.listdir(basedir+'p/posts/'+postid+'/hearts/'))
                except:
                    l=0
                l=l+1
                thedict={'hearts':l}
                savejson('p/posts/'+postid+'/meta',thedict)
                os.system('rm '+basedir+'p/heartrank/'+postid+'-'+str(int(l-1)).zfill(16))
                os.system('cp '+basedir+'p/posts/'+postid+'/meta '+basedir+'p/heartrank/'+postid+'-'+str(int(l)).zfill(16))
                thedict={'hearts':l,'name':session.user,'mail':mail,'displayname':displayname,'timeadded':formattime()}
                savejson('p/posts/'+postid+'/hearts/'+session.user, thedict)
                savejson('u/'+session.user+'/posts/'+postid+'/hearts/'+session.user, thedict)
                user_likes = True
            elif user_likes == True:
                try:
                    l=len(os.listdir(basedir+'p/posts/'+postid+'/hearts/'))
                except:
                    l=0
                if l > 0:
                    l=l-1
                    thedict={'hearts':l}
                    savejson('p/posts/'+postid+'/meta',thedict)
                    deletepost(basedir+'u/'+session.user+'/posts/'+postid+'/hearts/'+session.user)
                    deletepost(basedir+'p/posts/'+postid+'/hearts/'+session.user)
                    os.system('rm '+basedir+'p/heartrank/'+postid+'-'+str(int(l+1)).zfill(16))
                    os.system('cp '+basedir+'p/posts/'+postid+'/meta '+basedir+'p/heartrank/'+postid+'-'+str(int(l)).zfill(16))
                user_likes = False
            likes = len(os.listdir(basedir+'p/posts/'+postid+'/hearts/'))
            # Example: Update like count in your database
            # This is a placeholder; replace with your database logic
            # Return JSON response
            web.header('Content-Type', 'application/json')
            return json.dumps({'likes': likes, 'user_likes': user_likes ,'heart':heart,'hearted':hearted})

class user():
    def GET(self, user):
        data = web.input(soundname=None, onair=None, public=None, showuploads=None)
        if user == session.user:
            if data.public and data.soundname:
                public=data.public
                thedict={'timeadded':formattime()}
                savejson('p/posts/'+postid+'/meta')
            elif data.showuploads=='yes':
                uploads = []
                uploads = get_files_by_time('public_html/u/' + user + '/images/web/',newest_first=True)
                return render.showuploads(uploads,user,allowedchar, random)
            elif data.onair and data.soundname:
                onair={"onair":data.onair}
                savejson('p/posts/'+postid+'/meta')
            #soundname='aurora_ruderalis-greatful_bread'
            #filetype='flac'
            #postid = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
            usersounds=loadjson('r/users/'+user)
            #sounds=os.listdir(basedir+'p/posts/')
            creditsounds = []
            #for i in sounds:
            #    creditsounds.append(loadjson('p/posts/'+i))
            #for i in creditsound:
            #    try:
            #        credits=i['musicians'].split(',')
            #    except:
            #        credits=''
            #    for u in credits:
            #        if u.strip().lower() == user.strip().lower():
            #            creditsounds.append(i.title)
            return render.user(usersounds,creditsounds,user,datetime,str,int)
        return web.seeother('/login')

class invites():
    form = web.form.Form(
    web.form.Textbox('mail', description="epost:"), 
    web.form.Button('Skicka'))
    def GET(self):
        if session.login > 2:
            os.makedirs(basedir+'r/invites/'+session.user+'/',exist_ok=True)
            invites=[]
            v = get_files_by_time('r/invites/'+session.user,newest_first=True) 
            if v:
                for i in v:
                    invite=loadjson('r/invites/'+session.user+'/'+i)
                    invites.append(invite)
            tuningform = self.form()
            w = web.input(epost=None, render=None)
            formfail = ''
            if w.epost == '':
                formfail = formfail + 'you have to put your email in'
            if w.render == 'yes':
                secretinvitekey = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
                thedict={"secretinvitekey":secretinvitekey,"timeadded":formattime(),"creator":session.user, "accepted":''}
                savejson('r/invites/'+session.user+'/'+secretinvitekey, thedict)
                raise web.seeother('/invites')
            return render.invites(tuningform, formfail, session.user, invites)
    def POST(self):
        if session.login > 2:
            user = loadjson('r/users/'+session.user)
            tuningform = self.form()
            i = web.input()
            if i.mail == '':
                raise web.seeother('/invites?fail=nomail')
            if '@' not in i.mail:
                raise web.seeother('/tuning?fail=notmail') 
            secretinvitekey = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
            thedict={"secretinvitekey":secretinvitekey,"timeadded":formattime(),"creator":session.user, "accepted":''}
            savejson('r/invites/'+session.user+'/'+secretinvitekey, thedict)
            msg = "YO! You are the One! " + user.name + " is your Morpheous. Follow this rabbit https://robinbackman.com/register?invite="+secretinvitekey 
            sendmail(i.mail, 'Invitation to HEART RANKED!', msg)
        return web.seeother('/')

class tuning():
    form = web.form.Form(
    web.form.Textbox('user', description="synligt namn:"),
    web.form.Password('password', description="lösenord:"),
    web.form.Password('newpassword', description="nytt lösen (ifall du vill byta):"),
    web.form.Password('newpassword2', description="nytt lösen igen:"),
    web.form.Textbox('mail', description="epost:"), 
    web.form.Button('Spara'))
    def GET(self):
        if session.login > 2:
            user = loadjson('r/users/'+session.user)
            tuningform = self.form()
            w = web.input(namn=None,epost=None,fail=None,upd=None)
            formfail = ''
            if w.fail == 'wrongpass':
                formfail = formfail + 'wrong passcode'
            if w.fail == 'nopass':
                formfail = formfail + 'you have to write passcode'
            if w.namn == '':
                formfail = formfail + 'whats your displayname'
            if w.epost == '':
                formfail = formfail + 'write your email please'
            elif w.fail == 'notmail':
                formfail = formfail + 'email please'
            if w.fail == 'nametaken':
                formfail = formfail + 'name is taken! choose another'
            if w.fail == 'mailtaken':
                formfail = formfail + 'mail address taken'
            if w.fail == 'kortlosen':
                formfail = formfail + '5 characters minimum'
            if w.fail == 'newpass':
                formfail = formfail + 'new passcode doesnt match'
            if w.upd == 'yes':
                formfail = 'Yes, your account has been tuned in thanks!'
            tuningform.fill(user=user['displayname'], mail=user['mail'])
            return render.tuning(tuningform, formfail, user['name'])
        else:
            return web.seeother('/register')
    def POST(self):
        if session.login > 2:
            tuningform = self.form()
            i = web.input()
            if i.password == '':
                raise web.seeother('/tuning?fail=nopass')
            rymdadmins = []
            users = os.listdir(basedir+'r/users/')
            for r in users:
                admin=loadjson('r/users/'+r)
                rymdadmins.append(admin)
            for p in rymdadmins:
                print(p)
                if p['name'] == session.user:
                    passcode=bytes.fromhex(p['password'])
                    if verify_password(passcode,i.password):
                        #check if display name taken
                        for a in rymdadmins:
                            if i.user in a['displayname'] and a['name'] != session.user:
                                raise web.seeother('/tuning?fail=nametaken')
                            if i.mail in a['mail'] and i.mail != p['mail']:
                                raise web.seeother('/tuning?fail=mailtaken')
                        if i.newpassword != '':
                            if i.newpassword != i.newpassword2:
                                raise web.seeother('/tuning?fail=newpass')
                            if len(i.newpassword) < 5:
                                raise web.seeother('/tuning?fail=kortlosen')
                            else:
                                #update with password change
                                updateuser(i.user,i.newpassword,i.mail)
                                return web.seeother('/tuning?upd=yes')
                        if '@' not in i.mail:
                            raise web.seeother('/tuning?fail=notmail')
                        #update without passwordchange
                        thedict={'displayname':i.user,'mail':i.mail.lower()}
                        savejson('r/users/'+session.user, thedict)
                        return web.seeother('/tuning?upd=yes')
                    else:
                        raise web.seeother('/tuning?fail=wrongpass')

class forgotpass():
    form = web.form.Form(
            web.form.Textbox('mail', web.form.notnull, description="email:"),
            web.form.Button('Send me new passcode'))
    def GET(self):
        fejl = ''
        i = web.input(error=None)
        if i.error == 'fejl':
            fejl = 'no email like that sorry!'
        elif i.error == 'done':
            fejl = 'your passcode is updated and sent to your mail'
        elif i.error == 'nej':
            fejl = 'nope, dont worky'
        elif i.error == 'stopresetpass':
            fejl = 'Already sent passcode to mail'
        if session.login < 3:
            loginform = self.form()
            return render.forgotpass(loginform, fejl)
        if session.login == 3:
            return web.seeother('/s')
        if session.login == 5:
            raise web.seeother('/s')
    def POST(self):
        referer = web.ctx.env.get('HTTP_REFERER',baseurl)
        ip = web.ctx['ip']
        stopflood(ip, referer)
        sendpassform = self.form()
        if not sendpassform.validates():
            raise web.seeother('/forgotpass?error=fejl')
        else:
            i = web.input()
            if '@' not in i.mail:
                raise web.seeother('/forgotpass?error=fejl')
            rymdadmins = []
            users = os.listdir(basedir+'r/users/')
            for r in users:
                admin=loadjson('r/users/'+r)
                rymdadmins.append(admin)
            for p in rymdadmins:
                if p['mail'].lower() == i.mail.lower():
                    passfilter = stopresetpass(i.mail.lower())
                    if passfilter == True:
                        raise web.seeother('/forgotpass?error=stopresetpass')
                    unencrypted_password = ('%06x' % random.randrange(16**6))
                    password = unencrypted_password.encode("utf-8")
                    password_hashed=hash_password(password).hex()
                    thedict={'password':password_hashed}
                    savejson('r/users/'+session.user, thedict)
                    print("lösenordet uppdaterat!")
                    msg = "Your new passcode is: " + unencrypted_password
                    sendmail(p.mail, 'Heart Ranked Passcode', msg)
                    raise web.seeother('/forgotpass?error=done')
            raise web.seeother('/forgotpass?error=fejl')

def sendmail(email, subject, msg):
    #Send mail
    try:
        echomsg = subprocess.Popen(('echo', msg+'\n'+postadmin_signature), stdout=subprocess.PIPE)
        sendmsg = subprocess.check_output(('mail', '-r', postadmin, '-s', subject, email), stdin=echomsg.stdout)
        echomsg.wait()
    except:
        print('no mail server found')
        #subprocess.call(['echo', msg, '|', 'mail', '-r', postadmin,'-s', subject, email])

def get_new_frames(gif, scale):
    new_frames = []
    actual_frames = gif.n_frames
    for frame in range(actual_frames):
        gif.seek(frame)
        new_frame = Image.new('RGBA', gif.size)
        new_frame.paste(gif)
        new_frame.thumbnail(scale, Image.Resampling.LANCZOS)
        new_frames.append(new_frame)
    return new_frames

def save_new_gif(new_frames, old_gif_information, new_path):
    new_frames[0].save(new_path,
                       save_all = True,
                       append_images = new_frames[1:],
                       duration = old_gif_information['duration'],
                       loop = old_gif_information['loop'],
                       background = old_gif_information['background'],
                       extension = old_gif_information['extension'] ,
                       transparency = old_gif_information['transparency'])

def resize_gif(input_path, output_path, max_size):
    input_image = Image.open(input_path)
    frames = list(_thumbnail_frames(input_image,max_size))
    output_image = frames[0]
    output_image.save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        disposal=input_image.disposal_method,
        **input_image.info,
    )

def _thumbnail_frames(image,max_size):
    for frame in ImageSequence.Iterator(image):
        new_frame = frame.copy()
        new_frame.thumbnail(max_size, Image.Resampling.LANCZOS)
        yield new_frame

def scale_gif(path, scale, new_path=None):
    gif = Image.open(path)
    if not new_path:
        new_path = path
    old_gif_information = {
        'loop': bool(gif.info.get('loop', 1)),
        'duration': gif.info.get('duration', 40),
        'background': gif.info.get('background', 223),
        'extension': gif.info.get('extension', (b'NETSCAPE2.0')),
        'transparency': gif.info.get('transparency', 223)
    }
    new_frames = get_new_frames(gif, scale)
    save_new_gif(new_frames, old_gif_information, new_path)


def getdisplayname(user):
    try:
        displayname = loadjson('r/users/'+session.user)
        displayname = displayname.displayname
    except:
        displayname = user
    return displayname

#-------------Get files and sort em by date modified---------------

def get_dirs_by_time(path, reverse=False):
    """Return names of immediate subdirectories, sorted by modification time."""
    path=basedir+path
    with os.scandir(path) as it:
        return sorted(
            (e.name for e in it if e.is_dir(follow_symlinks=False)),
            key=lambda name: os.stat(os.path.join(path, name)).st_mtime,
            reverse=reverse,
        )

def get_posts_by_time(path,reverse):
    posts = os.listdir(path)
    timebased=[]
    for p in posts:
        l=loadjson('p/posts/'+p+'/meta')
        timebased.append((l['postid'],l['timeadded']))
    fmt = datetimeformat
    sorted_posts = sorted(timebased, key=lambda x: datetime.datetime.strptime(x[1], fmt),reverse=reverse)
    return sorted_posts

def get_files_by_time(directory: str = ".", newest_first: bool = True):
    path = Path(basedir+directory) 
    #Get all files (exclude directories and hidden files if you want)
    files = [f for f in path.iterdir() if f.is_file()]
    #Sort by modification time
    sorted_files = sorted(
        files,
        key=lambda f: f.stat().st_mtime,   # last modified timestamp
        reverse=newest_first
    ) 
    # Return just the file names (as strings)
    return [f.name for f in sorted_files]

def getfiles(filmfolder):
    #get a list of films, in order of settings.p file last modified
    films_sorted = []
    films = next(os.walk(filmfolder))[1]
    for i in films:
        uploaded = os.listdir(filmfolder + i + '/')
        for f in uploaded:
            if os.path.isfile(filmfolder + i + '/'+f) == True:
                #DUUUUUUDE HERE CHECK IF OLDER THAN
                lastupdate = os.path.getmtime(filmfolder + i + '/' + f)
                films_sorted.append((i,f,lastupdate))
        else:
            films_sorted.append((i,f,0))
    films_sorted = sorted(films_sorted, key=lambda tup: tup[2], reverse=True)
    return films_sorted

def callsubprocess(cmd):
    subprocess.call(cmd.split())

def visitorlog():
    ip = web.ctx['ip']
    referer = web.ctx.env.get('HTTP_REFERER', 'none')
    environ = web.ctx.env.get('HTTP_USER_AGENT', 'dunno')
    last = get_files_by_time('r/visitors/',newest_first=True)
    stopflood(ip, referer)
    country='local loco'
    countrycode='fi'
    if last:
        lastip=loadjson('r/visitors/'+last[0])
    else:
        lastip=''
        try:
            country = ''
            country = os.popen('geoiplookup '+ip).read()
            print(country)
            if country != '':
                countrycode = country.split(':')[1].split(',')[0].lower().strip()
                country = country.split(':')[1].split(',')[1].strip()
            else:
                country='none'
        except:
            country='local loco'
            countrycode='fi'
        thedict={'ip':ip,'referer':referer,'environ':environ,'country':country,'countrycode':countrycode,'time':formattime()}
        savejson('r/visitors/'+ip,thedict)
        print("added to visitor log")
    if lastip != ip:
        try:
            country = ''
            country = os.popen('geoiplookup '+ip).read()
            #print(soundtype)
            countrycode = country.split(':')[1].split(',')[0].lower().strip()
            country = country.split(':')[1].split(',')[1].strip()
            thedict={'ip':ip,'referer':referer,'environ':environ,'country':country,'countrycode':countrycode,'time':formattime()}
            savejson('r/visitors/'+ip,thedict)
        except:
            pass
        print("added to visitor log")
    return

def getvisitors():
    visitors=[]
    v = get_files_by_time('r/visitors/',newest_first=True) 
    if v:
        for i in v:
            visit=loadjson('r/visitors/'+i)
            visitors.append(visit)
            print(visit)
    total=len(os.listdir(basedir+'r/visitors/'))
    unique=[]
    for i in visitors:
        for p in visitors:
            if i['ip'] == p['ip']:
                unique.append(i)
    uniquevisits=len(unique)
    return visitors, total, uniquevisits

def getvisits():
    visitors=[]
    #v=os.listdir(basedir+'r/visitors/')
    v = get_files_by_time('r/visitors/',newest_first=True) 
    for i in v:
        visit=loadjson('r/visitors/'+i)
        visitors.append(visit)
    total=len(os.listdir(basedir+'r/visitors/'))
    unique=[]
    for i in visitors:
        for p in visitors:
            if i['ip'] == p['ip']:
                unique.append(i)
    uniquevisits=len(unique)
    countrylist=[]
    for i in visitors:
        if i['countrycode'] not in countrylist:
            countrylist.append(i['countrycode'])
    return countrylist, total, uniquevisits

class stats:
    def GET(self):
        p = web.input(logfilter=None)
        visitors, total, unique = getvisitors()
        return rendersplash.stats(visitors, total, unique, p.logfilter)

class logout:
    def GET(self):
        session.login = 0
        session.user = None
        raise web.seeother('/')

def getlikes(postid, user):
    user_likes = False
    os.makedirs(basedir+'p/posts/'+postid+'/hearts/',exist_ok=True)
    try:
        l=len(os.listdir(basedir+'p/posts/'+postid+'/hearts/'))
        print(os.listdir(basedir+'p/posts/'+postid+'/hearts/'))
    except:
        l=0
    if user != None:
        m=loadjson('/p/posts/'+postid+'/hearts/'+user)
        if m:
            user_likes = True
        else:
            user_likes = False
    if l >= 0:
        if user_likes: 
            likes = hearted+" " + str(l)
        else: 
            if l > 0:
                likes = heart+" " + str(l)
            else:
                likes = heart
        return likes

def postexist(postid):
    try:
        l=loadjson('/p/posts/'+postid+'/meta')
    except:
        return False
    try:
        if l['postid'] != None:
            return True
        else:
            return False
    except:
        return False
    return False

def getcombines(postid):
    try:
        l=len(os.listdir(basedir+'p/posts/'+postid+'/combos/'))
    except:
        l=0
    print(postid)
    if int(l) > 0:
        return "⚭ " + str(l)
    else:
        return ''

def pushcombines(postid):
    try:
        l=len(os.listdir(basedir+'p/posts/'+postid+'/combos/'))
    except:
        l=0
    #thedict={'combines':l}
    #savejson('/p/posts/'+postid+'/meta',thedict)
    if l >= 0:
            return "⚭ " + str(l)
    else:
        return ''

def formattime():
    current_time = time.gmtime()
    str_time = time.strftime(datetimeformat, current_time)
    return str_time

def sort_by_name_then_time(path):
    sortedposts=[]
    heartrank=os.listdir(basedir+path)
    for h in heartrank:
        postid=h.split('-')[0]
        postrank=h.split('-')[1]
        sortedposts.append((postrank,postid))
    heartrank=sorted(sortedposts, reverse=True)
    return heartrank

def rankrender():
    posts = os.listdir(basedir+'p/posts')
    os.system('rm -r '+basedir+'p/heartrank')
    os.system('rm -r '+basedir+'p/comborank')
    os.makedirs(basedir+'p/comborank',exist_ok=True)
    os.makedirs(basedir+'p/heartrank',exist_ok=True)
    for postid in posts:
        try:
            l=len(os.listdir(basedir+'p/posts/'+postid+'/hearts/'))
        except:
            l=0
        thedict={'hearts':l}
        savejson('p/posts/'+postid+'/meta',thedict)
        os.system('cp '+basedir+'p/posts/'+postid+'/meta '+basedir+'p/heartrank/'+postid+'-'+str(int(l)).zfill(16))
        try:
            l=len(os.listdir(basedir+'p/posts/'+postid+'/combos/'))
        except:
            l=0
        thedict={'combos':l}
        savejson('p/posts/'+postid+'/meta',thedict)
        os.system('cp '+basedir+'p/posts/'+postid+'/meta '+basedir+'p/comborank/'+postid+'-'+str(int(l)).zfill(16))

rankrender()

def getfeed():
    timebase=session.timebase
    feedbase=session.feedbase
    usr=session.usrfeed
    if feedbase == '':
        feedbase = 'time'
    if timebase == '':
        timebase = 'week'
    now = datetime.datetime.now()
    goodies=[]
    #HEARTS
    #SAVE HEARTRANKING EVERY MINUTE CHECK BOTH USER LIKES AND POST LIKES IF IT CHECKS OUT GOOD IT NOT WRITE ERROR AT LEAST (A BACKEND PROGRAM, RUNS EVERY MINUTE AND COUNTS LIKES AND WRITES THE HEARTRANKING FOR TODAY. HEARTRANKING STAYES SAVED FOREVER IN FOLDERS BY DAYS. IT IS A FOLDER WITH NUMBERS. starting with 0000000000000001 pointing to postid. simple. effective.
    #backend program will also sync posts and likes to trustees
    if feedbase == "heart" and timebase == "today":
        one_day_before = now - datetime.timedelta(days=1)
        posts = sort_by_name_then_time('p/heartrank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "heart" and timebase == "week":
        one_day_before = now - datetime.timedelta(weeks=1)
        posts = sort_by_name_then_time('p/heartrank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "heart" and timebase == "month":
        one_day_before = now - datetime.timedelta(weeks=4)
        posts = sort_by_name_then_time('p/heartrank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "heart" and timebase == "year":
        one_day_before = now - datetime.timedelta(weeks=54)
        posts = sort_by_name_then_time('p/heartrank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "heart" and timebase == "" or feedbase == "heart" and timebase == "all":
        posts = sort_by_name_then_time('/p/heartrank/')
        for p in posts:
            p=p[1]
            l=loadjson('p/posts/'+p+'/meta')
            if usr=='':
                goodies.append(l)
            if usr==l['creator']:
                goodies.append(l)
    #TIME
    elif feedbase == "time" and timebase == "today":
        one_day_before = now - datetime.timedelta(days=1)
        posts = get_posts_by_time(basedir+'p/posts/',reverse=True)
        print('fuuuuuuuuuu')
        print(posts)
        for p in posts:
            p=p[0]
            #check modtime here day
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "time" and timebase == "week":
        one_day_before = now - datetime.timedelta(weeks=1)
        posts = get_posts_by_time(basedir+'p/posts/',reverse=True)
        for p in posts:
            p=p[0]
            #check modtime here day
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "time" and timebase == "month":
        one_day_before = now - datetime.timedelta(weeks=4)
        posts = get_posts_by_time(basedir+'p/posts/',reverse=True)
        for p in posts:
            p=p[0]
            #check modtime here day
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "time" and timebase == "year":
        one_day_before = now - datetime.timedelta(weeks=54)
        posts = get_posts_by_time(basedir+'p/posts/',reverse=True)
        for p in posts:
            p=p[0]
            #check modtime here day
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "time" and timebase == "" or  feedbase == "time" and timebase == "all":
        posts = get_posts_by_time(basedir+'p/posts/',reverse=True)
        for p in posts:
            p=p[0]
            l=loadjson('p/posts/'+p+'/meta')
            if usr=='':
                goodies.append(l)
            if usr==l['creator']:
                goodies.append(l)

    #COMBO
    elif feedbase == "combo" and timebase == "today":
        one_day_before = now - datetime.timedelta(days=1)
        posts = sort_by_name_then_time('p/comborank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "combo" and timebase == "week":
        one_day_before = now - datetime.timedelta(weeks=1)
        posts = sort_by_name_then_time('p/comborank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "combo" and timebase == "month":
        one_day_before = now - datetime.timedelta(weeks=4)
        posts = sort_by_name_then_time('p/comborank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "combo" and timebase == "year":
        one_day_before = now - datetime.timedelta(weeks=54)
        posts = sort_by_name_then_time('p/comborank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                if usr=='':
                    goodies.append(l)
                if usr==l['creator']:
                    goodies.append(l)
    elif feedbase == "combo" and timebase == "" or  feedbase == "combo" and timebase == "all":
        posts = sort_by_name_then_time('p/comborank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            l=loadjson('p/posts/'+p+'/meta')
            if usr=='':
                goodies.append(l)
            if usr==l['creator']:
                goodies.append(l)
    elif feedbase == "Idontevenknow":
        print('write your own custom feed here')
    else:
        posts = os.listdir('p/posts/')
        for p in posts:
            l=loadjson('p/posts/'+p+'/meta')
            if usr=='':
                goodies.append(l)
            if usr==l['creator']:
                goodies.append(l)
    return goodies

def getcombofeed(show):
    timebase=session.timebase
    feedbase=session.feedbase
    if feedbase == "heart":
        posts = sort_by_name_then_time('p/heartrank/')
        comboposts=[]
        for p in posts: 
            p=p[1]
            l=loadjson('p/posts/'+p+'/meta')
            if 'combine' in l:
                if l['combine'] == show:
                    comboposts.append(l)
    elif feedbase == "combo":
        posts = sort_by_name_then_time('p/comborank/')
        comboposts=[]
        for p in posts:
            p=p[1]
            l=loadjson('p/posts/'+p+'/meta')
            if 'combine' in l:
                if l['combine'] == show:
                    comboposts.append(l)
    else:
        posts = get_dirs_by_time('p/posts/',reverse=True)
        comboposts=[]
        for p in posts:
            l=loadjson('p/posts/'+p+'/meta')
            if 'combine' in l:
                if l['combine'] == show:
                    comboposts.append(l)
    return comboposts

def userimage(user):
    usrimg = ''
    i = staticdir+'users/'+user+'/images/thumb/'+user
    print(i)
    if os.path.isfile(i+'.jpeg'):
        usrimg='static/users/'+user+'/images/thumb/'+user+'.jpeg'
    elif os.path.isfile(i+'.jpg'):
        usrimg='static/users/'+user+'/images/thumb/'+user+'.jpg'
    elif os.path.isfile(i+'.png'):
        usrimg='static/users/'+user+'/images/thumb/'+user+'.png'
    elif os.path.isfile(i+'.gif'):
        usrimg='static/users/'+user+'/images/thumb/'+user+'.gif'
    if usrimg != '':
        imghtml='<img class="usrimg" src="'+usrimg+'">'
        return imghtml
    else:
        return 

class heartranked:
    form = web.form.Form(web.form.Textbox('search', web.form.notnull, description="or search"))
    def GET(self):
        siterendered=formattime()
        visitorlog()
        visitors, total, unique = getvisits()
        print(visitors)
        print(str(total))
        print(str(unique))
        searchform = self.form()
        bildpersida = 1000
        session.search = ''
        session.bildsida = 0
        i = web.input(publised=None, public=None, show=None, remove=None, edit=None, feedbase=None, timebase=None, usrfeed=None)
        #search
        try:
            bilder_totalt=os.listdir(basedir+'p/posts/')
            tot = len(bilder_totalt)
            print('bilder alltsomallt: ' + str(tot))
        except:
            print("inga bilder")
            tot = 0
        #print('session search: ' + session.search)
        try:
            if i.search == '':
                session.search = ''
                session.bildsida = 0
            elif i.search != "":
                session.search = urllib.parse.unquote_plus(i.search)
                session.bildsida = 0
        except:
            pass
        if session.search != '':
            search_result = []
            tot = 0
            try:
                for i in bilder_totalt:
                    searchthis=loadjson('p/posts/'+i+'/meta')
                    for p in dir(searchthis):
                        if session.search in p:
                            search_result.append(searchthis)
                            tot=tot+1
            except:
                pass
            try:
                print(search_result)
                print('sökta bilder: ' + str(tot))
            except:
                pass
        try:
            if i.page == "next":
                if session.bildsida < tot:
                    session.bildsida += bildpersida
            if i.page == "back":
                if session.bildsida > bildpersida:
                    session.bildsida -= bildpersida
                else:
                    session.bildsida = 0
        except:
            pass
        limit = session.bildsida + bildpersida
        offset = session.bildsida
        #EOF search
        print(session.bildsida)
        bilder=[]
        if session.search == '':
            posts=os.listdir(basedir+'p/posts/')
            for p in posts:
                this=loadjson('p/posts/'+p+'/meta')
                bilder.append(this)
        else:
            bilder = search_result
        if i.feedbase == None:
            feedbase = ''
        else:
            feedbase = i.feedbase
            session.feedbase = feedbase
        if i.timebase == None:
            timebase = ''
        else:
            timebase = i.timebase
            session.timebase = timebase
        if i.timebase == None:
            timebase = ''
        else:
            timebase = i.timebase
            session.timebase = timebase
        if i.usrfeed == None:
            usrfeed = ''
        else:
            usrfeed = i.usrfeed
            session.usrfeed = usrfeed
        if session.user=='':
            free_hash_for_user = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[:4]
            #session.user = 'heart_'+free_hash_for_user
            session.user = None
        if i.edit != None:
            session.postid=i.edit
            raise web.seeother('/editor?public=yes') 
        if i.remove != None:
            try:
                post=loadjson('p/posts/'+i.remove+'/meta')
                if post['creator'] == session.user:
                    os.makedirs(basedir+'u/'+session.user+'/deleted/', exist_ok=True)
                    os.makedirs(basedir+'p/deleted/', exist_ok=True)
                    os.system('mv '+basedir+'u/'+session.user+'/posts/'+i.remove+' '+basedir+'u/'+session.user+'/deleted/')
                    os.system('mv '+basedir+'p/posts/'+i.remove+' '+basedir+'p/deleted/')
                    print('move to a deleted folder, make backend clean things up for real')
            except:
                pass
        if session.login > 3:
            try:
                if i.delete != '':
                    return web.seeother('/remove/' + i.delete)
            except:
                pass
            rights = 'admin'
        elif session.login > 2:
            rights = 'mod'
        else:
            rights = 'spacer'
        return rendersplash.heartranked(markdown, visitors, total, unique, logged, rights, session.user, getlikes, formattime, feedbase, tot, limit, offset, bildpersida, session.search, bilder, searchform, getcombines, timebase, getfeed, getcombofeed, userimage, postexist, i.show, loadjson, loadtext, len, heart, hearted, sitename, siteslogan, siterendered, siteurl, session.usrfeed)
    def POST(self):
        searchform = self.form()
        i = web.input()
        if i.search != '':
            raise web.seeother('/?search='+i.search)

def zippitandshippit(postid):
    #also zippit here!
    os.makedirs(basedir+'r/trusted/'+session.user+'/', exist_ok=True)
    os.system('ln -s '+basedir+'p/zipped '+staticdir+'users/'+session.user+'/zipped')
    os.system('cd '+basedir+'p/posts/ && zip -o -r '+postid+'.zip '+postid )
    os.system('mv '+basedir+'p/posts/'+postid+'.zip '+basedir+'/p/zipped/')
    #LETS SHIPPIT!
    trustedlist=[]
    trusted=os.listdir(basedir+'r/trusted/'+session.user+'/')
    for t in trusted:
        trusted=loadjson('r/trusted/'+session.user+'/'+t)
        trustedlist.append(trusted)
    for t in trustedlist:
        url=t['servername']+':'+t['port']
        for a in allowedchar:
            if '.'+a in t['servername']: #is webaddress use https
                url='https://'+t['servername']
        passcode=t['password']
        trustedlogin = ['curl','-X','POST', url+'/login', '-i', '-b', basedir+'/sessions/sessions-'+session.user, '-c',basedir+'/sessions/sessions-'+session.user, '-d', 'user='+t['user'], '-d', 'password='+passcode]
        subprocess.check_output(trustedlogin)
        #OK GOT EM COOKIES LES DO IT DO IT DO IT SHIPPIT!
        shippit = ['curl','-X', 'POST', '--verbose', '--header', 'Content-Type: multipart/form-data', '-F', 'files=@'+basedir+'p/zipped/'+postid+'.zip;type=application/zip', '-b', basedir+'/sessions/sessions-'+session.user, '-c',basedir+'/sessions/sessions-'+session.user, url+'/upload']
        subprocess.check_output(shippit)

storage = {"content": ""}
class editor:
    def GET(self):
        if logged():
            i = web.input(publish=None, public=None, new=None, combine=None, remix=None, saveto='')
            if i.saveto != '':
                if session.login == 5:
                    session.saveto=i.saveto
            if i.combine != None:
                if session.user:
                    text=''
                    text2=''
                    session.postid = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
                    os.makedirs(basedir+'u/'+session.user+'/posts/'+session.postid, exist_ok=True)
                    thedict={'postid':session.postid, 'siteurl':siteurl, 'timeadded':formattime(), 'creator':session.user, 'combine':i.combine}
                    savejson('u/'+session.user+'/posts/'+session.postid+'/meta',thedict)
            if i.remix != None:
                if session.user:
                    text=''
                    text2=''
                    try:
                        olduser=loadjson('p/posts/'+i.remix+'/meta')
                        text=loadtext('p/posts/'+i.remix+'/intro')
                        text2=loadtext('p/posts/'+i.remix+'/post')
                    except:
                        pass
                    try:
                        olduser = olduser['creator']
                    except:
                        olduser = ''
                    if olduser != '':
                        allcreators = olduser+','+session.user
                    else:
                        allcreators = session.user
                    session.postid = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
                    os.makedirs(basedir+'u/'+session.user+'/posts/'+session.postid, exist_ok=True)
                    thedict={'postid':session.postid,  'siteurl':siteurl,'timeadded':formattime(), 'creator':allcreators, 'remix':i.remix}
                    os.makedirs(basedir+'p/posts/'+i.remix+'/remix', exist_ok=True)
                    savetext('p/posts/'+i.remix+'/remix/'+session.postid,session.user)

                    savejson('u/'+session.user+'/posts/'+session.postid+'/meta',thedict)
                    savetext('u/'+session.user+'/posts/'+session.postid+'/post', text2)
                    savetext('u/'+session.user+'/posts/'+session.postid+'/intro', text)
            if session.postid != '':
                if i.public=='yes':
                    try:
                        text=loadtext('p/posts/'+session.postid+'/intro')
                    except:
                        session.postid = ''
                else:
                    try:
                        text=loadtext('u/'+session.user+'/posts/'+session.postid+'/intro')
                    except:
                        text = ''
                if i.public=='yes':
                    try:
                        text2=loadtext('p/posts/'+session.postid+'/post')
                    except:
                        session.postid = ''
                else:
                    try:
                        text2=loadtext('u/'+session.user+'/posts/'+session.postid+'/post')
                    except:
                        text2=''
            else:
                text = ''
                text2 = ''
            if i.saveto != '':
                text=i.saveto
                text2=loadtext(i.saveto)
            if i.new == 'yes':
                session.postid = ''
                raise web.seeother('/editor')
            if i.publish == 'yes' and text != '' and i.public == None and logged() and len(text) < 256:
                if session.saveto != '':
                    session.saveto=''       
                    raise web.seeother('/')
                c=loadjson('u/'+session.user+'/posts/'+session.postid+'/meta')
                if 'combine' in c:
                    if c['combine'] != '':
                        #calculate comborank
                        os.makedirs(basedir+'p/posts/'+c['combine']+'/combos', exist_ok=True)
                        savetext('p/posts/'+c['combine']+'/combos/'+session.postid,session.user)
                        os.makedirs(basedir+'p/heartrank/',exist_ok=True)
                        try:
                            l=len(os.listdir(basedir+'p/posts/'+session.postid+'/combos/'))
                        except:
                            l=0
                        thedict={'combos':l}
                        savejson('p/posts/'+c['combine']+'/meta',thedict)
                        os.system('rm '+basedir+'p/comborank/'+session.postid+'-'+str(int(l)).zfill(16))
                        os.system('cp '+basedir+'p/posts/'+session.postid+'/meta '+basedir+'p/comborank/'+session.postid+'-'+str(int(l)).zfill(16))
                description1 = text
                description2 = text2
                soundname = safe_filename(description1[0:27])
                thedict={'soundname':soundname}
                savejson('u/'+session.user+'/posts/'+session.postid+'/meta',thedict)
                os.system('cp -r '+basedir+'u/'+session.user+'/posts/'+session.postid+' '+basedir+'p/posts/')
                #symlinkthis(session.postid, session.user)
                #also zippit here!
                #os.system('zip -r '+basedir+'p/zipped/'+session.postid+'.zip '+basedir+'p/posts/'+session.postid )
                #os.system('cd '+basedir+'p/posts/ && zip -o -r '+session.postid+'.zip '+session.postid )
                #os.system('mv '+basedir+'p/posts/'+session.postid+'.zip '+basedir+'/p/zipped/')
                if zipandship == 'yes' or zipandship == 'True' or zipandship == 'y' or zipandship == 'Y':
                    zippitandshippit(session.postid)
                raise web.seeother('/')
            return rendersplash.editor(storage, text, text2, markdown, safe_filename, session.postid, i.public, logged(), session.user, i.combine, i.remix, session.saveto)

class savepost:
    def POST(self):
        data = json.loads(web.data())
        text = data.get("text", "")
        text2 = data.get("text2", "")
        if session.saveto != '':
            savetext(text, text2)
        else:
            if session.postid == '':
                session.postid = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
                os.makedirs(basedir+'u/'+session.user+'/posts/'+session.postid,exist_ok=True)
                thedict={'postid':session.postid, 'siteurl':siteurl, 'timeadded':formattime(), 'creator':session.user}
                savejson('u/'+session.user+'/posts/'+session.postid+'/meta',thedict)
                savetext('u/'+session.user+'/posts/'+session.postid+'/intro', text)
                savetext('u/'+session.user+'/posts/'+session.postid+'/post', text2)
            else:
                os.makedirs(basedir+'u/'+session.user+'/posts/'+session.postid,exist_ok=True)
                thedict={'postid':session.postid, 'siteurl':siteurl, 'timeadded':formattime(), 'creator':session.user}
                savejson('u/'+session.user+'/posts/'+session.postid+'/meta',thedict)
                savetext('u/'+session.user+'/posts/'+session.postid+'/intro', text)
                savetext('u/'+session.user+'/posts/'+session.postid+'/post', text2)
                print('post saved!')
        return "ok"  # simple response

class imageapi:
    def POST(self):
        action = ''
        data = json.loads(web.data())
        image = data.get("image", "")
        action = data.get("action", "")
        original_thumb = Image.open(staticdir+'users/'+session.user+'/images/thumb/'+image) 
        original_web = Image.open(staticdir+'users/'+session.user+'/images/web/'+image) 
        if action != '':
            if action == 'rotateright' and image != None:
                o_thumb=original_thumb.rotate(270)
                o_web=original_web.rotate(270)
            if action == 'rotateleft' and image != None:
                o_thumb=original_thumb.rotate(90)
                o_web=original_web.rotate(90)
            o_thumb.save(staticdir+'users/'+session.user+'/images/thumb/'+image)
            o_web.save(staticdir+'users/'+session.user+'/images/web/'+image)
        return  # simple response

class rendered:
    def GET(self):
        description=''
        description2=''
        try:
            description=loadtext('u/'+session.user+'/posts/'+session.postid+'/intro')
        except:
            pass
        try:
            description2=loadtext('u/'+session.user+'/posts/'+session.postid+'/post')
        except:
            pass
        return markdown.markdown(description+'\n\n---\n\n'+description2)

def get_new_frames(gif, scale):
    new_frames = []
    actual_frames = gif.n_frames
    for frame in range(actual_frames):
        gif.seek(frame)
        new_frame = Image.new('RGBA', gif.size)
        new_frame.paste(gif)
        new_frame.thumbnail(scale, Image.Resampling.LANCZOS)
        new_frames.append(new_frame)
    return new_frames

def save_new_gif(new_frames, old_gif_information, new_path):
    new_frames[0].save(new_path,
                       save_all = True,
                       append_images = new_frames[1:],
                       duration = old_gif_information['duration'],
                       loop = old_gif_information['loop'],
                       background = old_gif_information['background'],
                       extension = old_gif_information['extension'] ,
                       transparency = old_gif_information['transparency'])

def scale_gif(path, scale, new_path=None):
    gif = Image.open(path)
    if not new_path:
        new_path = path
    old_gif_information = {
        'loop': bool(gif.info.get('loop', 1)),
        'duration': gif.info.get('duration', 40),
        'background': gif.info.get('background', 223),
        'extension': gif.info.get('extension', (b'NETSCAPE2.0')),
        'transparency': gif.info.get('transparency', 223)
    }
    new_frames = get_new_frames(gif, scale)
    save_new_gif(new_frames, old_gif_information, new_path)

def getallmedia(media_dir, extensions):
    files = []
    for ext in extensions:
        c=list(Path(media_dir).rglob('*.'+ext))
        for a in c:
            files.append(str(a))
    print('wasassssup!?')
    print(files)
    return files

def symlinkmedia(mediafile,postid,user): 
    fixstatic = mediafile.split('/posts/'+postid+'/')[1]
    symlinkfile = staticdir + 'users/' + user + '/'+fixstatic
    symlinkdir=symlinkfile.rsplit('/',1)[0]
    os.makedirs(symlinkdir, exist_ok=True)
    os.system('ln -sf '+mediafile+' '+symlinkfile)

def symlinkthis(postid,user):
    extensions=['zip','pdf','txt','md','mp4','jpeg','jpg','png','gif','wav','flac','mp3','ogg']
    mediafiles = getallmedia(basedir+'u/'+user+'/posts/'+postid,extensions)
    for m in mediafiles:
        symlinkmedia(m,postid,user)
    print(mediafiles)

#symlinkthis('cd449464ec08fc7aa967d9b2795')

class upload:
    def POST(self):
        if logged():
            if session.postid == '':
                session.postid = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
                os.makedirs(basedir+'u/'+session.user+'/posts/'+session.postid,exist_ok=True)
            try:
                extensions=['zip','pdf','txt','md','mp4','jpeg','jpg','png','gif','wav','flac','mp3','ogg']
                saved_files = []
                # Best way for multiple files in web.py
                input_data = web.webapi.rawinput()
                uploaded = input_data.get('files')
                print('LETS GO!')
                print(session.user)
                print(input_data)
                print(uploaded)
                if not isinstance(uploaded, list):
                    uploaded = [uploaded] if uploaded else []
                for f in uploaded:
                    if f and hasattr(f, 'filename') and f.filename:
                        # Sanitize filename a bit
                        imgdir = basedir + 'u/' + session.user + '/temp/'
                        os.system('mkdir -p ' + imgdir)
                        safe_name = safe_filename(os.path.basename(f.filename))
                        filepath = os.path.join(imgdir, safe_name)
                        with open(filepath, 'wb') as out:
                            out.write(f.file.read())  # Important: use .file.read()
                        saved_files.append(safe_name)
                        ##---------- UPLOAD SOUND ----------
                        imgname=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
                        filetype = imgname.split('.')[-1].lower()
                        soundfile=safe_name
                        print(filetype)
                        if filetype == 'zip':
                            print('incoming!')
                            usersound = basedir + 'u/' + session.user + '/zipped/'
                            os.system('mkdir -p ' + usersound)
                            os.system('mv ' + imgdir + soundfile + ' ' + usersound + soundfile)
                            os.system('cd '+usersound+' && unzip -o '+soundfile+' -d '+basedir+'u/'+session.user+'/posts/')
                            os.system('cd '+usersound+' && unzip -o '+soundfile+' -d '+basedir+'p/posts/')
                            mediafiles = getallmedia(basedir+'p/posts/'+soundfile.split('.zip')[0],extensions)
                            print('wowoweewaa')
                            print(basedir+'p/posts/'+soundfile.split('.zip')[0])
                            print(mediafiles)
                            for m in mediafiles:
                                symlinkmedia(m,soundfile.split('.zip')[0],session.user)
                        elif filetype == 'pdf' or filetype == 'txt' or filetype == 'md':
                            usersound = basedir + 'u/' + session.user + '/posts/'+session.postid+'/docs/'
                            os.system('mkdir -p ' + usersound)
                            os.system('mv ' + imgdir + soundfile + ' ' + usersound + soundfile)
                            symlinkmedia(usersound + soundfile,session.postid,session.user)
                        elif filetype == 'mp4':
                            usersound = basedir + 'u/' + session.user + '/posts/'+session.postid+'/films/'
                            os.system('mkdir -p ' + usersound)
                            os.system('mv ' + imgdir + soundfile + ' ' + usersound + soundfile)
                            symlinkmedia(usersound + soundfile,session.postid,session.user)
                        elif filetype == 'jpeg' or filetype == 'jpg' or filetype == 'png' or filetype == 'gif':
                            usersound = basedir + 'u/' + session.user + '/posts/'+session.postid+'/images/'
                            os.system('mkdir -p ' + usersound)
                            os.makedirs(usersound + 'web/', exist_ok=True)
                            os.makedirs(usersound + 'thumb/', exist_ok=True)
                            os.system('mv ' + imgdir + soundfile + ' ' + usersound + soundfile)
                            symlinkmedia(usersound + soundfile,session.postid,session.user)
                            if filetype == 'gif':
                                scale_gif(usersound+soundfile, [900,900], usersound+'web/'+soundfile)
                                scale_gif(usersound+soundfile, [300,300], usersound+'thumb/'+soundfile)
                                symlinkmedia(usersound + 'web/' + soundfile,session.postid,session.user)
                                symlinkmedia(usersound + 'thumb/' + soundfile,session.postid,session.user)
                            else:
                                ##---------- OPEN FILE & CHEKC IF JPEG --------
                                image = Image.open(usersound + soundfile)
                                ##---------- RESIZE IMAGE -----------
                                image.thumbnail((900,900), Image.Resampling.LANCZOS)
                                image.save(usersound + 'web/' + soundfile)
                                symlinkmedia(usersound + 'web/' + soundfile,session.postid,session.user)
                                image.thumbnail((300,300), Image.Resampling.LANCZOS)
                                image.save(usersound + 'thumb/' + soundfile)
                                symlinkmedia(usersound + 'thumb/' + soundfile,session.postid,session.user)
                                print('images resized images')
                        elif filetype == 'wav' or filetype == 'flac' or filetype == 'mp3' or filetype == 'ogg':
                            usersound = basedir + 'u/' + session.user + '/posts/'+session.postid+'/sounds/'
                            os.system('mkdir -p ' + usersound)
                            os.system('mv ' + imgdir + soundfile + ' ' + usersound + soundfile)
                            soundlenght = os.popen('mediainfo --Inform="General;%Duration%" ' + usersound + soundfile).read()
                            print('sound lenght:' + str(soundlenght))
                            soundtype = os.popen('mediainfo --Inform="General;%Format%" ' + usersound + soundfile).read()
                            print(soundtype)
                            if 'Ogg' in soundtype:
                                #os.system('ffmpeg -i '+usersound+soundfile+' '+usersound+soundname+'.wav')
                                print('ogg file found, converting to flac')
                                os.system('ffmpeg -i ' + usersound + soundfile +' '+ usersound + soundname + '.flac') 
                                print('converting to mp3')
                                os.system('ffmpeg -y -loglevel 1 -i ' + usersound + soundname + '.flac -c:a libmp3lame -b:a 192k ' + usersound + soundname + '.mp3') 
                            if 'MPEG Audio' in soundtype:
                                print('mp3 file found, converting to flac')
                                os.system('ffmpeg -i ' + usersound + soundfile + ' ' + usersound + soundname + '.flac') 
                                print('converting to ogg')
                                os.system('ffmpeg -i ' + usersound + soundname +'.flac '+ usersound + soundname + '.ogg') 
                                print('Wave file found, converting to flac')
                            if 'Wave' in soundtype:
                                print('Wave file found, converting to flac')
                                os.system('flac ' + usersound + soundfile + ' ' + usersound + soundname + '.flac') 
                                os.system('sox -V1 ' + usersound + soundfile + ' ' + usersound + soundname + '.ogg') 
                                os.system('ffmpeg -y -loglevel 1 -i ' + usersound + soundfile + ' -c:a libmp3lame -b:a 192k ' + usersound + soundname + '.mp3') 
                            if 'FLAC' in soundtype:
                                print('FLAC file found, converting to mp3 and ogg')
                                os.system('sox -V1 ' + usersound + soundfile + ' ' + usersound + soundname + '.ogg') 
                                os.system('ffmpeg -y -loglevel 1 -i ' + usersound + soundfile + ' -c:a libmp3lame -b:a 192k ' + usersound + soundname + '.mp3')
                        saved_files.append(safe_name)
                        print(f"✅ Saved: {safe_name}")  # This will show in console for debugging
                    else:
                        print("⚠️ Skipped invalid file object")
            except Exception as e:
                print("Upload error:", str(e))
                return f"❌ Error: {str(e)}"
            if saved_files:
                return f"✅ Successfully uploaded {len(saved_files)} file(s): {', '.join(saved_files)}"
            else:
                return "❌ No files received. Check console for details."
        else:
            print('access denied')

class uploads:
    def GET(self):
        if logged():
            uploaded = getfiles(staticdir+'upload/')
            return render.uploads(uploaded)

class pull:
    def GET(self):
        extensions=['zip','pdf','txt','md','mp4','jpeg','jpg','png','gif','wav','flac','mp3','ogg']
        i = web.input(name=None,postid=None) #GET LIST WITH NAME JSON WHY NOT?! 
        if i.name != None and i.postid != None:
            print(i.name)
            print(i.postid)
            posts = get_dirs_by_time('p/posts/', reverse=True)
            try:
                posts = posts[:posts.index(i.postid)] #MUST GET POST LIST FROM SERVER API INSTEAD DUDE
            except:
                posts = get_dirs_by_time('p/posts/', reverse=True)
            postdict={}
            print(posts)
            for p in posts:
                l=loadjson('p/posts/'+p+'/meta')
                postdict.update({l['postid']:{'postid': l['postid'], 'name': l['creator']}})
            web.header('Content-Type', 'application/json')
            web.header('Access-Control-Allow-Origin', '*')  # helps with browser/script access
            return json.dumps(postdict)
        else:
            if logged():
                trusted=os.listdir(basedir+'r/trusted/'+session.user+'/')
                trustedlist=[]
                for t in trusted:
                    trusted=loadjson('r/trusted/'+session.user+'/'+t)
                    trustedlist.append(trusted)
                for t in trustedlist:
                    print('pulling from '+t['servername'])
                    #posts = getpostsfromse}erver(
                    #postid = get_dirs_by_time('p/posts/', reverse=True)[0]
                    postid=''
                    pullposts = requests.get('https://'+t['servername']+'/pull?name='+t['user']+'&postid='+postid).json()
                    print('https://'+t['servername']+'/pull?name='+t['user']+'&postid='+postid)
                    print(pullposts)
                    print('FUUUUUUUUUUU')
                    #zippandshipp=[]
                    #if t['user']!=None:
                    #    users = os.listdir(basedir+'r/users/')
                    #    for r in users:
                    #        if r['name']==t['user']:
                    #            for p in posts:
                    #                if p['creator']==r['name']:
                    #                    pullnunzip.append(p)
                    for p in pullposts:
                        print('hold on pulling new posts')
                        print(p)
                        print(pullposts[p]['name'])
                        os.system('wget -O '+basedir+'p/zipped/'+pullposts[p]['postid']+'.zip https://'+t['servername']+'/static/users/'+pullposts[p]['name']+'/zipped/'+pullposts[p]['postid']+'.zip')
                        os.system('cd '+basedir+'p/zipped/ && unzip -o '+pullposts[p]['postid']+'.zip -d '+basedir+'u/'+session.user+'/posts/')
                        os.system('cd '+basedir+'p/zipped/ && unzip -o '+pullposts[p]['postid']+'.zip -d '+basedir+'p/posts/')
                        mediafiles = getallmedia(basedir+'p/posts/'+pullposts[p]['postid'],extensions)
                        print('wowoweewaa')
                        print(basedir+'p/posts/'+pullposts[p]['postid'])
                        print(mediafiles)
                        for m in mediafiles:
                            symlinkmedia(m,pullposts[p]['postid'],session.user)
                #finally render rank
                rankrender()
            else:
                print('no access!')

class config:
    def GET(self):
        if logged():
            if session.login == 5:
                i = web.input(do=None)
                if i.do!=None:
                    raise web.seeother('/editor?saveto='+i.do)

#Load from settings
standalone = settings.standaloneserver
if standalone == 'yes' or standalone == 'True' or standalone == 'y' or standalone == 'Y':
    app.run()
else:
    application = app.wsgifunc()
