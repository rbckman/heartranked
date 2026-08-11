#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time, datetime, os, sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import json
import requests
import subprocess
import web
import hashlib
import random
import settings
import markdown
import re
import bcrypt
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
    '/config', 'config')

#Load from settings
webmaster = settings.webmaster
baseurl = settings.baseurl
siteurl = baseurl
postadmin = settings.postadmin
postadmin_signature = settings.postadmin_signature
heart=settings.heart
hearted=settings.hearted
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
session = web.session.Session(app,store,initializer={'login':0, 'privilege':0, 'bag':[], 'sessionkey':'empty','postid':'','backurl':'','user':'','search':'', 'bildsida':'', 'feedbase':'', 'timebase':''})

allowedchar = 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'

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
    password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    password_hashed = bcrypt.hashpw(password, salt).decode('utf-8')
    tot = len(os.listdir(basedir+'r/users/'))
    print(password_hashed)
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
    password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    password_hashed = bcrypt.hashpw(password, salt).decode('utf-8')
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
    #level = db.query("SELECT adminlevel FROM rymdadmin WHERE name='"+user+"';")[0]
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
    invite=loadjson('r/invites/'+secretinvitation)
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

        i = web.input(remove=None)
        if i.remove != None:
            os.system('rm '+basedir+'r/trusted/'+i.remove)
            return web.seeother('/trust')
        trusted=os.listdir(basedir+'r/trusted/')
        trustedlist=[]
        for t in trusted:
            trusted=loadjson('r/trusted/'+t)
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
        thedict={'servername':i.servername, 'port':i.port, 'user':i.user, 'password':i.password}
        savejson('r/trusted/'+i.servername,thedict)
        return web.seeother('/trust')

class login():
    form = web.form.Form(
    web.form.Textbox('user', web.form.notnull, description="your registered mail account:"),
    web.form.Password('password', web.form.notnull, description="and your passcode please:"),
    web.form.Button('Login'))
    users=os.listdir(basedir+'r/users/')
    if len(users) == 0:
        result = subprocess.run(['whoami'], capture_output=True, text=True)
        adduser('op', 'blessyou', result.stdout.rstrip()+'@localhost')
    def GET(self):
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
                try:
                    encodepass = p['password'].encode("utf-8")
                except:
                    encodepass = p['password']
                if bcrypt.checkpw(i['password'].encode('utf-8'), encodepass) == True:
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
            #rymdadmins = db.select('rymdadmin', what='name, mail')
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
            #db.update('invites', where='secretinvitation="'+i.invite+'"', accepted=formattime(datetime.datetime.now()))
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
            #l = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+session.user+"';")
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
                #db.insert('likes', user=session.user, bild=postid, datum=formattime(datetime.datetime.now()))
                try:
                    l=len(os.listdir(basedir+'p/posts/'+postid+'/hearts/'))
                except:
                    l=0
                l=l+1
                #db.update('published', where='postid="'+postid+'"', hearts=l.likes)
                thedict={'hearts':l}
                savejson('p/posts/'+postid+'/meta',thedict)
                os.system('rm '+basedir+'p/heartrank/'+postid+'-'+str(int(l-1)).zfill(16))
                os.system('cp '+basedir+'p/posts/'+postid+'/meta '+basedir+'p/heartrank/'+postid+'-'+str(int(l)).zfill(16))
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
                thedict={'timeadded':formattime(datetime.datetime.now())}
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
            invites=[]
            v = get_files_by_time('r/invites/',newest_first=True) 
            if v:
                for i in v:
                    invite=loadjson('r/invites/'+i)
                    invites.append(invite)
            tuningform = self.form()
            w = web.input(epost=None, render=None)
            formfail = ''
            if w.epost == '':
                formfail = formfail + 'you have to put your email in'
            if w.render == 'yes':
                secretinvitekey = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
                thedict={"secretinvitekey":secretinvitekey,"timeadded":formattime(datetime.datetime.now()),"creator":session.user, "accepted":''}
                savejson('r/invites/'+secretinvitekey, thedict)
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
            thedict={"secretinvitekey":secretinvitekey,"timeadded":formattime(datetime.datetime.now()),"creator":session.user, "accepted":''}
            savejson('r/invites/'+secretinvitekey, thedict)
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
                    try:
                        encodepass = p['password'].encode("utf-8")
                    except:
                        encodepass = p['password']
                    if bcrypt.checkpw(i['password'].encode('utf-8'), encodepass) == True:
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
                                #password = i.newpassword.encode("utf-8")
                                #salt = bcrypt.gensalt()
                                #password_hashed = bcrypt.hashpw(password, salt)
                                #mail=i.mail.lower()
                                #thedict={'displayname':i.user,'password':password_hashed,'mail':mail}
                                #savejson('r/users/'+session.user, thedict)
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
                    salt = bcrypt.gensalt()
                    password_hashed = bcrypt.hashpw(password, salt)
                    thedict={'password':password_hashed}
                    savejson('r/users/'+p['name'], thedict)
                    print("lösenordet uppdaterat!")
                    msg = "Your new passcode is: " + unencrypted_password
                    sendmail(p.mail, 'Heart Ranked Passcode', msg)
                    raise web.seeother('/forgotpass?error=done')
            raise web.seeother('/forgotpass?error=fejl')

def sendmail(email, subject, msg):
    #Send mail
    echomsg = subprocess.Popen(('echo', msg+'\n'+postadmin_signature), stdout=subprocess.PIPE)
    sendmsg = subprocess.check_output(('mail', '-r', postadmin, '-s', subject, email), stdin=echomsg.stdout)
    echomsg.wait()
    #subprocess.call(['echo', msg, '|', 'mail', '-r', postadmin,'-s', subject, email])

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
            thedict={'ip':ip,'referer':referer,'environ':environ,'country':country,'countrycode':countrycode,'time':formattime(datetime.datetime.now())}
            savejson('r/visitors/'+ip,thedict)
        except:
            pass
        print("added to visitor log")
    if lastip != ip:
        try:
            country = ''
            country = os.popen('geoiplookup '+ip).read()
            #print(soundtype)
            countrycode = country.split(':')[1].split(',')[0].lower().strip()
            country = country.split(':')[1].split(',')[1].strip()
            #db.insert('visitors', ip=ip, referer=referer, environ=environ, country=country,  countrycode=countrycode, time=formattime(datetime.datetime.now()))
            thedict={'ip':ip,'referer':referer,'environ':environ,'country':country,'countrycode':countrycode,'time':formattime(datetime.datetime.now())}
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
    #l = db.query("SELECT Count(*) AS likes FROM likes WHERE bild='"+postid+"';")[0]
    os.makedirs(basedir+'p/posts/'+postid+'/hearts/',exist_ok=True)
    try:
        l=len(os.listdir(basedir+'p/posts/'+postid+'/hearts/'))
        print(os.listdir(basedir+'p/posts/'+postid+'/hearts/'))
    except:
        l=0
    #db.update('published', where='postid="'+postid+'"', hearts=l.likes)
    if user != None:
        #m = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+user+"';")
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
        #l = db.select('published', where="postid='"+postid+"'")[0]
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
    #l = db.query("SELECT Count(*) AS combines FROM published WHERE combine='"+postid+"';")[0]
    try:
        l=len(os.listdir(basedir+'p/posts/'+postid+'/combos/'))
    except:
        l=0
    print(postid)
    #m = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+user+"';")
    #db.update('published', where='postid="'+postid+'"', combines=0)
    if int(l) > 0:
        return "⚭ " + str(l)
    else:
        return ''

def pushcombines(postid):
    #l = db.query("SELECT Count(*) AS combines FROM published WHERE postid='"+postid+"';")[0]
    try:
        l=len(os.listdir(basedir+'p/posts/'+postid+'/combos/'))
    except:
        l=0
    #m = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+user+"';")
    #db.update('published', where='postid="'+postid+'"', combines=l.combines)
    #thedict={'combines':l}
    #savejson('/p/posts/'+postid+'/meta',thedict)
    if l >= 0:
            return "⚭ " + str(l)
    else:
        return ''

def formattime(timeadded):
    return timeadded.strftime("%Y-%m-%d %H:%M:%S")

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
        #db.update('published', where='postid="'+postid+'"', hearts=l.likes)
        thedict={'hearts':l}
        savejson('p/posts/'+postid+'/meta',thedict)
        os.system('cp '+basedir+'p/posts/'+postid+'/meta '+basedir+'p/heartrank/'+postid+'-'+str(int(l)).zfill(16))
        try:
            l=len(os.listdir(basedir+'p/posts/'+postid+'/combos/'))
        except:
            l=0
        #db.update('published', where='postid="'+postid+'"', hearts=l.likes)
        thedict={'combos':l}
        savejson('p/posts/'+postid+'/meta',thedict)
        os.system('cp '+basedir+'p/posts/'+postid+'/meta '+basedir+'p/comborank/'+postid+'-'+str(int(l)).zfill(16))

rankrender()

def getfeed():
    timebase=session.timebase
    feedbase=session.feedbase
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
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY hearts DESC LIMIT 1000;")
        #posts=os.listdir('/p/posts/')
        #make function get_files_by_time newest_first and by today week month year
        posts = sort_by_name_then_time('p/heartrank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "heart" and timebase == "week":
        one_day_before = now - datetime.timedelta(weeks=1)
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY hearts DESC LIMIT 1000;")
        posts = sort_by_name_then_time('p/heartrank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "heart" and timebase == "month":
        one_day_before = now - datetime.timedelta(weeks=4)
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY hearts DESC LIMIT 1000;")
        posts = sort_by_name_then_time('p/heartrank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "heart" and timebase == "year":
        one_day_before = now - datetime.timedelta(weeks=54)
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY hearts DESC LIMIT 1000;")
        posts = sort_by_name_then_time('p/heartrank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "heart" and timebase == "" or feedbase == "heart" and timebase == "all":
        #goodies = db.query("SELECT * FROM published ORDER BY hearts DESC LIMIT 1000;")
        posts = sort_by_name_then_time('/p/heartrank/')
        for p in posts:
            p=p[1]
            l=loadjson('p/posts/'+p+'/meta')
            goodies.append(l)

    #TIME
    elif feedbase == "time" and timebase == "today":
        one_day_before = now - datetime.timedelta(days=1)
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY ID DESC LIMIT 1000;")
        posts = get_dirs_by_time('p/posts/', reverse=True)
        print(posts)
        for p in posts:
            #check modtime here day
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "time" and timebase == "week":
        one_day_before = now - datetime.timedelta(weeks=1)
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY ID DESC LIMIT 1000;")
        posts = get_dirs_by_time('p/posts/', reverse=True)
        for p in posts:
            #check modtime here day
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "time" and timebase == "month":
        one_day_before = now - datetime.timedelta(weeks=4)
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY ID DESC LIMIT 1000;")
        posts = get_dirs_by_time('p/posts/', reverse=True)
        for p in posts:
            #check modtime here day
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "time" and timebase == "year":
        one_day_before = now - datetime.timedelta(weeks=54)
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY ID DESC LIMIT 1000;")
        posts = get_dirs_by_time('p/posts/', reverse=True)
        for p in posts:
            #check modtime here day
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "time" and timebase == "" or  feedbase == "time" and timebase == "all":
        #goodies = db.query("SELECT * FROM published ORDER BY ID DESC LIMIT 1000;")
        posts = get_dirs_by_time('p/posts/', reverse=True)
        for p in posts:
            l=loadjson('p/posts/'+p+'/meta')
            goodies.append(l)

    #COMBO
    elif feedbase == "combo" and timebase == "today":
        one_day_before = now - datetime.timedelta(days=1)
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY combines DESC LIMIT 1000;")
        posts = sort_by_name_then_time('p/comborank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "combo" and timebase == "week":
        one_day_before = now - datetime.timedelta(weeks=1)
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY combines DESC LIMIT 1000;")
        posts = sort_by_name_then_time('p/comborank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "combo" and timebase == "month":
        one_day_before = now - datetime.timedelta(weeks=4)
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY combines DESC LIMIT 1000;")
        posts = sort_by_name_then_time('p/comborank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "combo" and timebase == "year":
        one_day_before = now - datetime.timedelta(weeks=54)
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY combines DESC LIMIT 1000;")
        posts = sort_by_name_then_time('p/comborank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            lastupdate = os.path.getmtime(basedir+'p/posts/'+p+'/meta')
            if datetime.datetime.fromtimestamp(lastupdate) > one_day_before:
                l=loadjson('p/posts/'+p+'/meta')
                goodies.append(l)
    elif feedbase == "combo" and timebase == "" or  feedbase == "combo" and timebase == "all":
        #goodies = db.query("SELECT * FROM published ORDER BY combines DESC LIMIT 1000;")
        posts = sort_by_name_then_time('p/comborank/')
        for p in posts:
            #check modtime here day
            p=p[1]
            l=loadjson('p/posts/'+p+'/meta')
            goodies.append(l)
    elif feedbase == "Idontevenknow":
        #goodies = db.query("SELECT * FROM published ORDER BY combines DESC LIMIT 1000;")
        print('write your own custom feed here')
    else:
        #goodies = db.query("SELECT * FROM published ORDER BY ID DESC LIMIT 1000;")
        posts = os.listdir('p/posts/')
        for p in posts:
            l=loadjson('p/posts/'+p+'/meta')
            goodies.append(l)
    return goodies

def getcombofeed(show):
    timebase=session.timebase
    feedbase=session.feedbase
    if feedbase == "heart":
        #comboposts = db.query("SELECT * FROM published WHERE combine='"+show+"' ORDER BY hearts DESC LIMIT 1000;")
        posts = sort_by_name_then_time('p/heartrank/')
        comboposts=[]
        for p in posts: 
            p=p[1]
            l=loadjson('p/posts/'+p+'/meta')
            if 'combine' in l:
                if l['combine'] == show:
                    comboposts.append(l)
    elif feedbase == "combo":
        #comboposts = db.query("SELECT * FROM published WHERE combine='"+show+"' ORDER BY combines DESC LIMIT 1000;")
        posts = sort_by_name_then_time('p/comborank/')
        comboposts=[]
        for p in posts:
            p=p[1]
            l=loadjson('p/posts/'+p+'/meta')
            if 'combine' in l:
                if l['combine'] == show:
                    comboposts.append(l)
    else:
        #comboposts = db.query("SELECT * FROM published WHERE combine='"+show+"' ORDER BY ID DESC LIMIT 1000;")
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
    i = staticdir+'u/'+user+'/images/thumb/'+user
    print(i)
    if os.path.isfile(i+'.jpeg'):
        usrimg='/u/users/'+user+'/images/thumb/'+user+'.jpeg'
    elif os.path.isfile(i+'.jpg'):
        usrimg='/u/users/'+user+'/images/thumb/'+user+'.jpg'
    elif os.path.isfile(i+'.png'):
        usrimg='/u/users/'+user+'/images/thumb/'+user+'.png'
    elif os.path.isfile(i+'.gif'):
        usrimg='/u/users/'+user+'/images/thumb/'+user+'.gif'
    if usrimg != '':
        imghtml='<img class="usrimg" src="'+usrimg+'">'
        return imghtml
    else:
        return 

class heartranked:
    form = web.form.Form(web.form.Textbox('search', web.form.notnull, description="or search"))
    def GET(self):
        visitorlog()
        visitors, total, unique = getvisits()
        print(visitors)
        print(str(total))
        print(str(unique))
        searchform = self.form()
        bildpersida = 1000
        session.search = ''
        session.bildsida = 0
        i = web.input(publised=None, public=None, show=None, remove=None, edit=None, feedbase=None, timebase=None)
        #search
        try:
            #bilder_totalt = db.query("SELECT COUNT(*) AS sound FROM published")[0]
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
                #search_result.append(db.query("SELECT * FROM published WHERE creator LIKE '%"+session.search+"%' ORDER BY ID DESC LIMIT 1000;"))
                #tot = db.query("SELECT Count(*) AS sound FROM published WHERE creator LIKE '%"+session.search+"%';")[0]
                #b1 = tot.sound
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
            #bilder = db.query("SELECT * FROM published ORDER BY id DESC LIMIT " + str(limit) + " OFFSET " + str(offset))
            posts=os.listdir(basedir+'p/posts/')
            for p in posts:
                this=loadjson('p/posts/'+p+'/meta')
                bilder.append(this)
            #print(bilder)
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
        if session.user=='':
            free_hash_for_user = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[:4]
            #session.user = 'heart_'+free_hash_for_user
            session.user = None

        if i.edit != None:
            session.postid=i.edit
            raise web.seeother('/editor?public=yes') 
        if i.remove != None:
            try:
                #user = db.select('published', where="postid='"+i.remove+"'")[0]
                post=loadjson('p/posts/'+i.remove+'/meta')
                if post['creator'] == session.user:
                    os.makedirs(basedir+'u/'+session.user+'/deleted/', exist_ok=True)
                    os.makedirs(basedir+'p/deleted/', exist_ok=True)
                    os.system('mv '+basedir+'u/'+session.user+'/posts/'+i.remove+' '+basedir+'u/'+session.user+'/posts/deleted/')
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
        return rendersplash.heartranked(markdown, visitors, total, unique, logged, rights, session.user, getlikes, formattime, feedbase, tot, limit, offset, bildpersida, session.search, bilder, searchform, getcombines, timebase, getfeed, getcombofeed, userimage, postexist, i.show, loadjson, loadtext, len, heart, hearted)
    def POST(self):
        searchform = self.form()
        i = web.input()
        if i.search != '':
            raise web.seeother('/?search='+i.search)

storage = {"content": ""}
class editor:
    def GET(self):
        if logged():
            i = web.input(publish=None, public=None, new=None, combine=None, remix=None)
            if i.combine != None:
                if session.user:
                    text=''
                    text2=''
                    session.postid = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
                    os.makedirs(basedir+'u/'+session.user+'/posts/'+session.postid, exist_ok=True)
                    thedict={'postid':session.postid, 'siteurl':siteurl, 'timeadded':formattime(datetime.datetime.now()), 'creator':session.user, 'combine':i.combine}
                    savejson('u/'+session.user+'/posts/'+session.postid+'/meta',thedict)
            if i.remix != None:
                if session.user:
                    text=''
                    text2=''
                    try:
                        #olduser = db.select('unpublished', where="postid='"+i.remix+"'")[0]
                        olduser=loadjson('p/posts/'+i.remix+'/meta')
                        #text = db.select('unpublished', where="postid='"+i.remix+"'")[0]
                        text=loadtext('p/posts/'+i.remix+'/intro')
                        #text2 = db.select('unpublished', where="postid='"+i.remix+"'")[0]
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
                    #db.insert('unpublished', postid=session.postid, description=text, description2=text2, timeadded=formattime(datetime.datetime.now()), creator=allcreators, remix=i.remix)
                    os.makedirs(basedir+'u/'+session.user+'/posts/'+session.postid, exist_ok=True)
                    thedict={'postid':session.postid,  'siteurl':siteurl,'timeadded':formattime(datetime.datetime.now()), 'creator':allcreators, 'remix':i.remix}
                    os.makedirs(basedir+'p/posts/'+i.remix+'/remix', exist_ok=True)
                    savetext('p/posts/'+i.remix+'/remix/'+session.postid,session.user)

                    savejson('u/'+session.user+'/posts/'+session.postid+'/meta',thedict)
                    savetext('u/'+session.user+'/posts/'+session.postid+'/post', text2)
                    savetext('u/'+session.user+'/posts/'+session.postid+'/intro', text)
            if session.postid != '':
                if i.public=='yes':
                    try:
                        #text = db.select('published', where="postid='"+session.postid+"'")[0]
                        text=loadtext('p/posts/'+session.postid+'/intro')
                    except:
                        session.postid = ''
                else:
                    try:
                        #text = db.select('unpublished', where="postid='"+session.postid+"'")[0]
                        text=loadtext('u/'+session.user+'/posts/'+session.postid+'/intro')
                    except:
                        text = ''
                if i.public=='yes':
                    try:
                        #text2 = db.select('published', where="postid='"+session.postid+"'")[0]
                        text2=loadtext('p/posts/'+session.postid+'/post')
                    except:
                        session.postid = ''
                else:
                    try:
                        #text2 = db.select('unpublished', where="postid='"+session.postid+"'")[0]
                        text2=loadtext('u/'+session.user+'/posts/'+session.postid+'/post')
                    except:
                        text2=''
            else:
                text = ''
                text2 = ''
            if i.new == 'yes':
                session.postid = ''
                raise web.seeother('/editor')
            if i.publish == 'yes' and text != '' and i.public == None and logged() and len(text) < 256:
                c=loadjson('u/'+session.user+'/posts/'+session.postid+'/meta')
                if 'combine' in c:
                    if c['combine'] != '':
                        print('FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU')
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
                #session.postid = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
                os.system('cp -r '+basedir+'u/'+session.user+'/posts/'+session.postid+' '+basedir+'p/posts/')
                #also zippit here!
                #os.system('zip -r '+basedir+'p/zipped/'+session.postid+'.zip '+basedir+'p/posts/'+session.postid )
                os.system('cd '+basedir+'p/posts/ && zip -o -r '+session.postid+'.zip '+session.postid )
                os.system('mv '+basedir+'p/posts/'+session.postid+'.zip '+basedir+'/p/zipped/')
                #LETS SHIPPIT!
                trustedlist=[]
                trusted=os.listdir(basedir+'r/trusted/')
                for t in trusted:
                    trusted=loadjson('r/trusted/'+t)
                    trustedlist.append(trusted)
                for t in trustedlist:
                    url=t['servername']+':'+t['port']
                    for a in allowedchar:
                        if '.'+a in t['servername']: #is webaddress use https
                            url='https://'+t['servername']+':'+t['port']
                    trustedlogin = ['curl','-X','POST', url+'/login', '-i', '-b', basedir+'/sessions/sessions-'+session.user, '-c',basedir+'/sessions/sessions-'+session.user, '-d', 'user='+t['user'], '-d', 'password='+t['password']]
                    subprocess.check_output(trustedlogin)
                    shippit = ['curl','-X', 'POST', '--verbose', '--header', 'Content-Type: multipart/form-data', '-F', 'files=@'+basedir+'p/zipped/'+session.postid+'.zip;type=application/zip', '-b', basedir+'/sessions/sessions-'+session.user, '-c',basedir+'/sessions/sessions-'+session.user, url+'/upload']
                    subprocess.check_output(shippit)
                #OK GOT EM COOKIES LES DO IT DO IT DO IT SHIPPIT!
                raise web.seeother('/editor?public=yes')
                #db.insert('pawning', pawning=i.remix, name=session.user, timeadded=formattime(datetime.datetime.now()))
            return rendersplash.editor(storage, text, text2, markdown, safe_filename, session.postid, i.public, logged(), session.user, i.combine, i.remix)

class savepost:
    def POST(self):
        data = json.loads(web.data())
        text = data.get("text", "")
        text2 = data.get("text2", "")
        if session.postid == '':
            session.postid = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
            os.makedirs(basedir+'u/'+session.user+'/posts/'+session.postid,exist_ok=True)
            thedict={'postid':session.postid, 'siteurl':siteurl, 'timeadded':formattime(datetime.datetime.now()), 'creator':session.user}
            savejson('u/'+session.user+'/posts/'+session.postid+'/meta',thedict)
            savetext('u/'+session.user+'/posts/'+session.postid+'/intro', text)
            savetext('u/'+session.user+'/posts/'+session.postid+'/post', text2)
        else:
            os.makedirs(basedir+'u/'+session.user+'/posts/'+session.postid,exist_ok=True)
            thedict={'postid':session.postid, 'siteurl':siteurl, 'timeadded':formattime(datetime.datetime.now()), 'creator':session.user}
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

class upload:
    def POST(self):
        if logged():
            try:
                saved_files = []
                # Best way for multiple files in web.py
                input_data = web.webapi.rawinput()
                uploaded = input_data.get('files')
                print('LETS GO!')
                print(session.user)
                print(input_data)
                print(uploaded)
                # Make sure it's always a list
                if not isinstance(uploaded, list):
                    uploaded = [uploaded] if uploaded else []
                for f in uploaded:
                    if f and hasattr(f, 'filename') and f.filename:
                        # Sanitize filename a bit
                        imgdir = staticdir + 'users/' + session.user + '/temp/'
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
                        elif filetype == 'pdf' or filetype == 'txt' or filetype == 'md':
                            usersound = staticdir + 'users/' + session.user + '/docs/'
                            os.system('mkdir -p ' + usersound)
                            os.system('mv ' + imgdir + soundfile + ' ' + usersound + soundfile)
                        elif filetype == 'mp4':
                            usersound = staticdir + 'users/' + session.user + '/films/'
                            os.system('mkdir -p ' + usersound)
                            os.system('mv ' + imgdir + soundfile + ' ' + usersound + soundfile)
                        elif filetype == 'jpeg' or filetype == 'jpg' or filetype == 'png' or filetype == 'gif':
                            userpics = staticdir + 'users/' + session.user + '/images/'
                            os.system('mkdir -p ' + userpics)
                            os.system('mv ' + imgdir + soundfile + ' ' + userpics + soundfile)
                            if filetype == 'gif':
                                scale_gif(userpics+soundfile, [900,900], userpics+'web/'+soundfile)
                                scale_gif(userpics+soundfile, [300,300], userpics+'thumb/'+soundfile)
                            else:
                                ##---------- OPEN FILE & CHEKC IF JPEG --------
                                image = Image.open(userpics + soundfile)
                                try:
                                    os.makedirs(userpics + 'web/', exist_ok=True)
                                    os.makedirs(userpics + 'thumb/', exist_ok=True)
                                except:
                                    print('Folders is')
                                ##---------- RESIZE IMAGE -----------
                                image.thumbnail((900,900), Image.Resampling.LANCZOS)
                                image.save(userpics + 'web/' + soundfile)
                                image.thumbnail((300,300), Image.Resampling.LANCZOS)
                                image.save(userpics + 'thumb/' + soundfile)
                                print('images resized images')
                        elif filetype == 'wav' or filetype == 'flac' or filetype == 'mp3' or filetype == 'ogg':
                            usersound = staticdir + 'users/' + session.user + '/sounds/'
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

#Load from settings
standalone = settings.standaloneserver
if standalone == 'yes' or standalone == 'True' or standalone == 'y' or standalone == 'Y':
    app.run()
else:
    application = app.wsgifunc()
