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
import time
import shutil
import settings
import binascii
import base64
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
    '/config', 'config',

#Load from settings

webmaster = settings.webmaster
baseurl = settings.baseurl
siteurl = baseurl
allowed = settings.allowed
postadmin = settings.postadmin
postadmin_signature = settings.postadmin_signature

basedir = os.path.dirname(os.path.realpath(__file__))+'/'
templatedir = basedir + 'html/'
staticdir = basedir + 'public_html/'
web.config.debug = False
app = web.application(urls, globals())
store = web.session.DiskStore(basedir + 'sessions')
render = web.template.render(templatedir, base="base")
renderop = web.template.render(templatedir, base="op")
rendersplash = web.template.render(templatedir, base="splash")
session = web.session.Session(app,store,initializer={'login':0, 'privilege':0, 'bag':[], 'sessionkey':'empty','soundlink':'','backurl':'','user':'','search':'', 'bildsida':'', 'feedbase':'', 'timebase':''})

allowedchar = '_','-','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','1','2','3','4','5','6','7','8','9','0'

def logged():
    if session.login > 0:
        return True
    else:
        return False

class creatpost:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        return self

def load(thename):
    with open(basedir+thename, 'r') as f:
        settings = json.load(f)
        for key, i in settings.items():
            postmeta=creatpost(key,i)
    return postmeta

def save(thename, thedict):
    #full path to filename
    #save to next line make an ID automatically, you have to check the save to know how to load it.
    #loadfile check if record exist, first in line is the record hash and update if it exists
    #make users in a folder as files first is username username will always be user record
    #hearts will be files as usernames with timestamp in a hearts folder in post folder. be stored and checked in u/hearts and post/hearts
    # be sure to add home domain setting to username
    #make save list a dict use same names
    #postmeta=load(thename)
    for key, i in thedict.items():
        postmeta=createpost(key,i)
        
    with open(basedir+thename, "w") as f:
        #f.write(str(i) + ',')
        json.dumps(thedict,f)

def deletepost(thefile):
    os.system('rm '+thefile)

def adduser(name, password, mail):
    originalname=name
    name=safe_filename(name[:12])
    password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    password_hashed = bcrypt.hashpw(password, salt)
    tot = len(os.listdir(basedir+'users/'))
    print('users alltsomallt: ' + str(tot))
    if tot > 1:
        adminlevel=3
    else:
        adminlevel=5
    savedict={'name':name, 'originalname':originalname, 'password':password, 'hashed':hashed,'mail':mail,'adminlevel':adminlevel}
    save('users/'+name, savedict)
    print("new user added")
    return

def adminlevel(user):
    #level = db.query("SELECT adminlevel FROM rymdadmin WHERE name='"+user+"';")[0]
    level=load('users', user)
    #1 session logout, web.py bug
    #2 rights to see pics and comment
    #3 rights to upoload
    #5 superadmin
    session.login = int(level.adminlevel)
    return

def stopresetpass(mail):
    t = None
    if os.path.exists(basedir+'stopresetpass/'+mail) == True:
        t=load('stopresetpass/'+mail)
    else:
        savedict={'timeadded':time.time()}
        save('stopresetpass/'+mail, savedict)
        return
    savedict={'timeadded':time.time()}
    save('stopresetpass/'+mail, savedict)
    latest = time.time() - t
    print(latest)
    if latest < 600:
        print('mail is in password reset spam filter')
        return True
    else:
        return False

def stopflood(ip,referer):
    t = None
    if os.path.exists(basedir+'stopflood/'+ip) == True:
        t=load('stopflood/'+ip)
    else:
        savedict={'timeadded':time.time()}
        save('stopflood/'+ip, savedict)
        return
    savedict={'timeadded':time.time()}
    save('stopflood/'+ip, savedict)
    latest = time.time() - t
    print(latest)
    if latest < 1:
        print('flooding recognized!')
        return True
    else:
        return False

def getinvitation(secretinvitation):
    invite=load('invites/'+secretinvitation)
    if invitation == secretinvitation:
        if invite == '':
            return True
    return False

class login():
    form = web.form.Form(
    web.form.Textbox('user', web.form.notnull, description="your registered mail account:"),
    web.form.Password('password', web.form.notnull, description="and your passcode please:"),
    web.form.Button('Login'))
    def GET(self):
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
            return web.seeother('/heartranked')
        if session.login == 5:
            raise web.seeother('/heartranked')
    def POST(self):
        referer = web.ctx.env.get('HTTP_REFERER',baseurl)
        ip = web.ctx['ip']
        stopflood(ip, referer)
        loginform = self.form()
        i = web.input()
        if i.user == '' or i.password == '':
            raise web.seeother('/login?error=tom')
        rymdadmins = []
        rymdadmins = bildhistoriker()
        #if not rymdadmins:
        #    raise web.seeother('/register')
        for p in rymdadmins:
            if p.name.lower() == i.user.lower() or p.mail.lower() == i.user.lower():
                try:
                    encodepass = p.password.encode("utf-8")
                    print('noooo')
                except:
                    encodepass = p.password
                if bcrypt.checkpw(i.password.encode('utf-8'), encodepass) == True:
                    session.user = p.name
                    adminlevel(p.name)
                    print('BACKURL: '+session.backurl)
                    if session.login == 5:
                        raise web.seeother('/heartranked')
                    if session.backurl != '':
                        backurl = session.backurl
                        session.backurl = ''
                        raise web.seeother(backurl)
                    else:
                        raise web.seeother('/heartranked')
        return web.seeother('/login?error=fejl')

class register():
    form = web.form.Form(
    web.form.Textbox('invite', description="invitation code (do not edit):"),
    web.form.Textbox('user', description="name:"),
    web.form.Password('password', description="passcode:"),
    web.form.Textbox('mail', description="mail:"),
    web.form.Button('JOIN'))
    def GET(self):
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
            totusers = len(os.listdir(basedir+'users/'))
            registerform.fill(user=urllib.parse.unquote_plus(n), mail=urllib.parse.unquote_plus(m), invite=w.invite)
            return render.register(registerform, formfail, totusers)
        else:
            return web.seeother('/oopsie')
    def POST(self):
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
            rymdadmins = os.listdir(basedir+'users/')
            for p in rymdadmins:
                if p.name.lower() == i.user.lower():
                    raise web.seeother('/register?invite='+i.invite+'&fail=nametaken' +r)
                if p.mail.lower() == i.mail.lower():
                    raise web.seeother('/register?invite='+i.invite+'&fail=mailtaken' +r)
            adduser(i.user, i.password, i.mail.lower())
            #Send mail to Madbaker
            msg = "Wowowowoweeewaaa! Lets Ride The INTERNET Wave Together, Bee as home, HEART RANKED ftw! " + i.user + ' ' + i.mail
            sendmail(postadmin, 'Wowowoweewaaa!', msg)
            #Send mail to new user
            msg = "Wowowowoweeewaaa! "+i.user+" Lets Ride INTERNET Wave Together, Bee as home, HEART RANKED ftw! https://robinbackman.com/heartranked"
            sendmail(i.mail, 'HEART RANKED VISIONARY Fleet', msg)
            #session.login = 3
            #session.user = safe_filename(i.user)
            #add user to matrix
            #os.system("register_new_matrix_user -u "+i.user+" -p "+i.password+" --no-admin -c /etc/matrix-synapse/homeserver.yaml") 
            #db.update('invites', where='secretinvitation="'+i.invite+'"', accepted=datetime.datetime.now())
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
            i = web.input(unlike=None, like=None, hate=None, unhate=None, user=None, postid=None)
            user = i.user
            postid = i.postid
            #l = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+session.user+"';")
            l = load('posts/'+postid+'/likes/'+session.user)
            print(session.user)
            if l:
                user_likes = True
            else:
                user_likes = False
            if user_likes == False:
                #db.insert('likes', user=session.user, bild=postid, datum=datetime.datetime.now())
                savedict={'timeadded':datetime.datetime.now()}
                save('posts/'+postid+'/hearts/'+session.user, savedict)
                save('u/'+session.user+'/hearts/'+session.user, savedict)
                user_likes = True
            elif user_likes == True:
                #db.query("DELETE FROM likes WHERE bild='"+postid+"' AND user='"+session.user+"';")
                deletepost(basedir+'posts/'+postid+'/hearts/'+session.user)
                deletepost(basedir+'u/'+session.user+'/hearts/'+session.user)
                user_likes = False
            #likes = db.query("SELECT Count(*) AS likes FROM likes WHERE bild='"+postid+"';")[0]
            likes = len(os.listdir(basedir+'posts/'+postid+'/hearts/'))
            # Example: Update like count in your database
            # This is a placeholder; replace with your database logic
            # Return JSON response
            web.header('Content-Type', 'application/json')
            return json.dumps({'likes': likes, 'user_likes': user_likes })

class user():
    def GET(self, user):
        data = web.input(soundname=None, onair=None, public=None, showuploads=None)
        if user == session.user:
            if data.public and data.soundname:
                #db.update('published', where="soundlink='" + data.soundname +"'", public=data.public)
                public=data.public
                savedict={'timeadded':datetime.datetime.now()}
                save('posts/'+postid+'/meta')
            elif data.showuploads=='yes':
                uploads = []
                uploads = get_files_by_modtime('public_html/u/' + user + '/images/web/',newest_first=True)
                return render.showuploads(uploads,user,allowedchar, random)
            elif data.onair and data.soundname:
                #db.update('published', where="soundlink='" + data.soundname +"'", playing=data.onair)
                onair={"onair":data.onair}
                save('posts/'+postid+'/meta')
            #soundname='aurora_ruderalis-greatful_bread'
            #filetype='flac'
            #soundlink = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
            #db.insert('sound', soundlink=soundlink, filename=soundname, sort=filetype, title=soundname, uploaddate=datetime.datetime.now(), uppladdare=user, lastmod=datetime.datetime.now(), moddedby=user)
            #usersounds = db.query("SELECT * FROM published WHERE creator='"+user+"' ORDER BY timeadded DESC;")
            usersound=load('posts/')
            #sounds = db.select('published')
            sounds=os.listdir(basedir+'posts/')
            creditsounds = []
            for i in sounds:
                try:
                    credits=i.musicians.split(',')
                except:
                    credits=''
                for u in credits:
                    if u.strip().lower() == user.strip().lower():
                        creditsounds.append(i.title)
            return render.user(usersounds,creditsounds,user,datetime,str,int)
        return web.seeother('/login')

class invites():
    form = web.form.Form(
    web.form.Textbox('mail', description="epost:"), 
    web.form.Button('Skicka'))
    def GET(self):
        if session.login > 2:
            #user = db.select('rymdadmin', where='name="'+session.user+'"')[0]
            user = load('users/'+session.user)
            #invites = db.select('invites', where='createdby="'+session.user+'"')
            invites = load('invites/'+session.user)
            tuningform = self.form()
            w = web.input(epost=None, render=None)
            formfail = ''
            if w.epost == '':
                formfail = formfail + 'you have to put your email in'
            if w.render == 'yes':
                secretinvitekey = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
                #db.insert('invites', secretinvitation=secretinvitekey, created=datetime.datetime.now(), createdby=session.user)
                thedict={"secretinvitekey":secretinvitekey,"timeadded":datetime.datetime.now(),"creator":session.user)
                save('invites/'+session.user, thedict)
            return render.invites(tuningform, formfail, user.name, invites)
    def POST(self):
        if session.login > 2:
            #user = db.select('rymdadmin', where='name="'+session.user+'"')[0]
            user = load('users/'+session.user)
            tuningform = self.form()
            i = web.input()
            if i.mail == '':
                raise web.seeother('/invites?fail=nomail')
            if '@' not in i.mail:
                raise web.seeother('/tuning?fail=notmail') 
            secretinvitekey = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
            #db.insert('invites', secretinvitation=secretinvitekey, created=datetime.datetime.now(), createdby=session.user)
            thedict={"secretinvitekey":secretinvitekey,"timeadded":datetime.datetime.now(),"creator":session.user)
            save('invites/'+session.user, thedict)
            msg = "YO! You are the One! " + user.name + " is your Morpheous. Follow this rabbit https://robinbackman.com/register?invite="+secretinvitekey 
            sendmail(i.mail, 'Invitation to HEART RANKED!', msg)
        return web.seeother('/heartranked')

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
            print('asdfasdfasdf')
            #user = db.select('rymdadmin', where='name="'+session.user+'"')[0]
            user = load('users/'+session.user)
            tuningform = self.form()
            w = web.input(namn=None,epost=None,fail=None,upd=None)
            print('asdfasdfasdfkdakkakka')
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
            tuningform.fill(user=user.displayname, mail=user.mail, subscribe=user.subscribe)
            return render.tuning(tuningform, formfail, user.name)
        else:
            return web.seeother('/register')
    def POST(self):
        if session.login > 2:
            tuningform = self.form()
            i = web.input()
            if i.password == '':
                raise web.seeother('/tuning?fail=nopass')
            rymdadmins = bildhistoriker()
            for p in rymdadmins:
                print(p)
                if p.name == session.user:
                    if bcrypt.checkpw(i.password.encode('utf-8'), p.password):
                        #check if display name taken
                        b_displayname = bildhistoriker()
                        for a in b_displayname:
                            if i.user in a.displayname and a.name != session.user:
                                raise web.seeother('/tuning?fail=nametaken')
                            if i.mail in a.mail and i.mail != p.mail:
                                raise web.seeother('/tuning?fail=mailtaken')
                        if i.newpassword != '':
                            if i.newpassword != i.newpassword2:
                                raise web.seeother('/tuning?fail=newpass')
                            if len(i.newpassword) < 5:
                                raise web.seeother('/tuning?fail=kortlosen')
                            else:
                                #update with password change
                                password = i.newpassword.encode("utf-8")
                                salt = bcrypt.gensalt()
                                password_hashed = bcrypt.hashpw(password, salt)
                                #db.update('rymdadmin', where='name="'+session.user+'"', displayname=i.user, password=password_hashed, mail=i.mail.lower())
                                thedict={'displayname':i.user,'password':password_hashed,'mail':i.mail.lower()}
                                save('users/'+session.user, thedict)
                                return web.seeother('/tuning?upd=yes')
                        if '@' not in i.mail:
                            raise web.seeother('/tuning?fail=notmail')
                        #update without passwordchange
                        #db.update('rymdadmin', where='name="'+session.user+'"', displayname=i.user, mail=i.mail.lower())
                        thedict={'displayname':i.user,'mail':i.mail.lower()}
                        save('users/'+session.user, thedict)
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
            rymdadmin = []
            rymdadmins = bildhistoriker()
            for p in rymdadmins:
                if p.mail.lower() == i.mail.lower():
                    passfilter = stopresetpass(i.mail.lower())
                    if passfilter == True:
                        raise web.seeother('/forgotpass?error=stopresetpass')
                    unencrypted_password = ('%06x' % random.randrange(16**6))
                    password = unencrypted_password.encode("utf-8")
                    salt = bcrypt.gensalt()
                    password_hashed = bcrypt.hashpw(password, salt)
                    #db.update('rymdadmin', where='name="'+p.name+'"', password=password_hashed)
                    thedict={'password':password_hashed}
                    save('users/'+p.name, thedict)
                    print("lösenordet uppdaterat!")
                    msg = "Your new passcode is: " + unencrypted_password + ' , once you logg in with this enter a new passcode by pressin your name, it a um link. Take care now bye bye then.'
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
        #displayname = db.query("SELECT displayname FROM rymdadmin WHERE name='"+user+"';")[0]
        displayname = load('users/'+session.user)
        displayname = displayname.displayname
    except:
        displayname = user
    return displayname

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

#-------------Get files and sort em by date modified---------------

def get_files_by_modtime(directory: str = ".", newest_first: bool = True):
    """
    Returns a list of file names in the directory sorted by last modified time.
    
    - newest_first=True  → Newest files first (most recent modification)
    - newest_first=False → Oldest files first
    """
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
    print(filmfolder+'FUUUUUUUUUUUUUUUUUUUUUU')
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

def visitorlog(ip, referer, environ):
    #last = db.query('SELECT ip AS ip FROM visitors WHERE id=(SELECT MAX(id) FROM visitors)')
    last = get_files_by_modtime('visitors/'+ip,newest_first=True)
    lastip=load('visitors/'+last[0])
    if lastip != ip:
        country = ''
        country = os.popen('geoiplookup '+ip).read()
        #print(soundtype)
        countrycode = country.split(':')[1].split(',')[0].lower().strip()
        country = country.split(':')[1].split(',')[1].strip()
        #print('fuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu: '+ country)
        try:
            #db.insert('visitors', ip=ip, referer=referer, environ=environ, country=country,  countrycode=countrycode, time=datetime.datetime.now())
            thedict={'ip':ip,'referer':referer,'environ':environ,'country':country,'countrycode':countrycode,'time':datetime.datetime.now()}
            save('visitors/'+ip,thedict)
        except:
            pass
        print("added to visitor log")
    return

def getvisitors():
    #visitors = db.select('visitors')
    #visitors = db.query('SELECT * FROM visitors ORDER BY time DESC LIMIT 10000')
    visitors = get_files_by_modtime('visitors/'+ip,newest_first=True) 
    #total = db.query('SELECT COUNT(*) AS total_visits FROM visitors')
    total=len(os.listdir('visitors/'))
    #unique = db.query('SELECT COUNT(DISTINCT ip) AS unique_visits FROM visitors')
    unique=[]
    for i in visitors:
        for p in visitors:
            if i == p:
                unique.append(i)
    uniquevisits=len(unique)
    return visitors, total, uniquevisits

def getvisits():
    #limit=100
    #visits = db.query("SELECT * FROM visitors ORDER BY time DESC LIMIT " + str(limit))
    visits=load('visitors/')
    #visitors = db.select('visitors')
    visitors=load('visitors/')
    #total = db.query('SELECT COUNT(*) AS total_visits FROM visitors')
    total=len(os.listdir('visitors/'))
    #unique = db.query('SELECT COUNT(DISTINCT ip) AS unique_visits FROM visitors')
    unique=[]
    for i in visitors:
        for p in visitors:
            if i == p:
                unique.append(i)
    uniquevisits=len(unique)
    countrylist=[]
    for i in visits:
        if i.countrycode not in countrylist:
            countrylist.append(i.countrycode)
            #print('fuuuuuuuuuuuuuuu: '+i.countrycode)
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
        raise web.seeother('/heartranked')

def getlikes(postid, user):
    user_likes = False
    #l = db.query("SELECT Count(*) AS likes FROM likes WHERE bild='"+postid+"';")[0]
    l=len(os.listdir('posts/'+postid+'/hearts/')
    #db.update('published', where='soundlink="'+postid+'"', hearts=l.likes)
    thedict={'hearts:'l}
    save('posts/'+postid+'/meta',thedict)
    thedict={'postid:'postid}
    save('heartranked/'+str(l),thedict)
    if user:
        #m = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+user+"';")
        m=load('posts/'+postid+'/hearts/'+user)
        if m:
            user_likes = True
        else:
            user_likes = False
    if l.likes >= 0:
        if user_likes: 
            likes = "❤️ " + str(l.likes)
        else: 
            if l.likes > 0:
                likes = "🤍 " + str(l.likes)
            else:
                likes = "🤍 "
        return likes

def postexist(postid):
    return False
    try:
        #l = db.select('published', where="soundlink='"+postid+"'")[0]
        l=load('posts/'+postid+'/meta')
    except:
        return False
    try:
        if l.soundname != None:
            return True
        else:
            return False
    except:
        return False
    return False

def getcombines(postid):
    #l = db.query("SELECT Count(*) AS combines FROM published WHERE combine='"+postid+"';")[0]
    l=len(os.listdir('post/'+postid+'/combines/'))
    #m = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+user+"';")
    #db.update('published', where='soundlink="'+postid+'"', combines=0)
    if l.combines > 0:
            return "⚭ " + str(l)
    else:
        return ''

def pushcombines(postid):
    #l = db.query("SELECT Count(*) AS combines FROM published WHERE soundlink='"+postid+"';")[0]
    l=len(os.listdir('post/'+postid+'/combines/'))
    #m = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+user+"';")
    #db.update('published', where='soundlink="'+postid+'"', combines=l.combines)
    thedict={'combines':l}
    save('posts/'+postid+'/meta',thedict)
    if l.combines >= 0:
            return "⚭ " + str(l)
    else:
        return ''

def formattime(timeadded):
    return timeadded.strftime("%Y-%m-%d %H:%M:%S")

def getfeed():
    timebase=session.timebase
    feedbase=session.feedbase
    if feedbase == '':
        feedbase = 'time'
    now = datetime.datetime.now()
    #HEARTS
    #SAVE HEARTRANKING EVERY MINUTE CHECK BOTH USER LIKES AND POST LIKES IF IT CHECKS OUT GOOD IT NOT WRITE ERROR AT LEAST (A BACKEND PROGRAM, RUNS EVERY MINUTE AND COUNTS LIKES AND WRITES THE HEARTRANKING FOR TODAY. HEARTRANKING STAYES SAVED FOREVER IN FOLDERS BY DAYS. IT IS A FOLDER WITH NUMBERS. starting with 0000000000000001 pointing to postid. simple. effective.
    #backend program will also sync posts and likes to trustees
    if feedbase == "heart" and timebase == "today":
        now = datetime.datetime.now()
        one_day_before = now - datetime.timedelta(days=1)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        #goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY hearts DESC LIMIT 1000;")
        #posts=os.listdir('posts/')
        #make function get_files_by_modtime newest_first and by today week month year
        posts = get_files_by_modtime_today('posts/',newest_first=True)
        #posts=os.listdir('heartranked/')
        goodies=[]
        goodies2=[]
        for p in posts:
            l=load('posts/'+g)
            goodies.append(l)
        for g in goodies:
            goodies2.append(g.postid)
        print(goodies2)
    elif feedbase == "heart" and timebase == "week":
        now = datetime.datetime.now()
        one_day_before = now - datetime.timedelta(weeks=1)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY hearts DESC LIMIT 1000;")
    elif feedbase == "heart" and timebase == "month":
        now = datetime.datetime.now()
        one_day_before = now - datetime.timedelta(weeks=4)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY hearts DESC LIMIT 1000;")
    elif feedbase == "heart" and timebase == "year":
        now = datetime.datetime.now()
        one_day_before = now - datetime.timedelta(weeks=54)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY hearts DESC LIMIT 1000;")
    elif feedbase == "heart" and timebase == "" or feedbase == "heart" and timebase == "all":
        goodies = db.query("SELECT * FROM published ORDER BY hearts DESC LIMIT 1000;")
    #TIME
    elif feedbase == "time" and timebase == "today":
        one_day_before = now - datetime.timedelta(days=1)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY ID DESC LIMIT 1000;")
    elif feedbase == "time" and timebase == "week":
        now = datetime.datetime.now()
        one_day_before = now - datetime.timedelta(weeks=1)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY ID DESC LIMIT 1000;")
    elif feedbase == "time" and timebase == "month":
        now = datetime.datetime.now()
        one_day_before = now - datetime.timedelta(weeks=4)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY ID DESC LIMIT 1000;")
    elif feedbase == "time" and timebase == "year":
        now = datetime.datetime.now()
        one_day_before = now - datetime.timedelta(weeks=54)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY ID DESC LIMIT 1000;")
    elif feedbase == "time" and timebase == "" or  feedbase == "time" and timebase == "all":
        goodies = db.query("SELECT * FROM published ORDER BY ID DESC LIMIT 1000;")
    #COMBO
    elif feedbase == "combo" and timebase == "today":
        one_day_before = now - datetime.timedelta(days=1)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY combines DESC LIMIT 1000;")
    elif feedbase == "combo" and timebase == "week":
        now = datetime.datetime.now()
        one_day_before = now - datetime.timedelta(weeks=1)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY combines DESC LIMIT 1000;")
    elif feedbase == "combo" and timebase == "month":
        now = datetime.datetime.now()
        one_day_before = now - datetime.timedelta(weeks=4)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY combines DESC LIMIT 1000;")
    elif feedbase == "combo" and timebase == "year":
        now = datetime.datetime.now()
        one_day_before = now - datetime.timedelta(weeks=54)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY combines DESC LIMIT 1000;")
    elif feedbase == "combo" and timebase == "" or  feedbase == "combo" and timebase == "all":
        goodies = db.query("SELECT * FROM published ORDER BY combines DESC LIMIT 1000;")
    elif feedbase == "Idontevenknow":
        goodies = db.query("SELECT * FROM published ORDER BY combines DESC LIMIT 1000;")
    else:
        goodies = db.query("SELECT * FROM published ORDER BY ID DESC LIMIT 1000;")
    return goodies

def getcombofeed(show):
    timebase=session.timebase
    feedbase=session.feedbase
    if feedbase == "heart":
        comboposts = db.query("SELECT * FROM published WHERE combine='"+show+"' ORDER BY hearts DESC LIMIT 1000;")
    elif feedbase == "combo":
        comboposts = db.query("SELECT * FROM published WHERE combine='"+show+"' ORDER BY combines DESC LIMIT 1000;")
    elif feedbase == "idontknow":
        comboposts = db.query("SELECT * FROM published WHERE combine='"+show+"' ORDER BY hearts DESC LIMIT 1000;")
    else:
        comboposts = db.query("SELECT * FROM published WHERE combine='"+show+"' ORDER BY ID DESC LIMIT 1000;")
    return comboposts

def userimage(user):
    usrimg = ''
    i = staticdir+'users/'+user+'/images/thumb/'+user
    print(i)
    if os.path.isfile(i+'.jpeg'):
        usrimg='/static/users/'+user+'/images/thumb/'+user+'.jpeg'
    elif os.path.isfile(i+'.jpg'):
        usrimg='/static/users/'+user+'/images/thumb/'+user+'.jpg'
    elif os.path.isfile(i+'.png'):
        usrimg='/static/users/'+user+'/images/thumb/'+user+'.png'
    elif os.path.isfile(i+'.gif'):
        usrimg='/static/users/'+user+'/images/thumb/'+user+'.gif'
    if usrimg != '':
        imghtml='<img class="usrimg" src="'+usrimg+'">'
        return imghtml
    else:
        print('FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU')
        return 

class heartranked:
    form = web.form.Form(web.form.Textbox('search', web.form.notnull, description="or search"))
    def GET(self):
        searchform = self.form()
        bildpersida = 1000
        session.search = ''
        session.bildsida = 0
        i = web.input(publised=None, public=None, show=None, remove=None, edit=None, feedbase=None, timebase=None)
        #search
        try:
            bilder_totalt = db.query("SELECT COUNT(*) AS sound FROM published")[0]
            tot = int(bilder_totalt.sound)
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
            b1, b2, b3 = 0,0,0
            try:
                search_result.append(db.query("SELECT * FROM published WHERE creator LIKE '%"+session.search+"%' ORDER BY ID DESC LIMIT 1000;"))
                tot = db.query("SELECT Count(*) AS sound FROM published WHERE creator LIKE '%"+session.search+"%';")[0]
                b1 = tot.sound
            except:
                pass
            try:
                search_result.append(db.query("SELECT * FROM published WHERE description LIKE '%"+session.search+"%' ORDER BY ID DESC LIMIT 1000;"))
                tot = db.query("SELECT Count(*) AS sound FROM published WHERE description LIKE '%"+session.search+"%';")[0]
                b2 = tot.sound
            except:
                pass
            try:
                search_result.append(db.query("SELECT * FROM published WHERE description2 LIKE '%"+session.search+"%' ORDER BY ID DESC LIMIT 1000;"))
                tot = db.query("SELECT Count(*) AS sound FROM published WHERE description2 LIKE '%"+session.search+"%';")[0]
                b3 = tot.sound
            except:
                pass
            tot = b1 + b2 + b3
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
        if session.search == '':
            bilder = db.query("SELECT * FROM published ORDER BY id DESC LIMIT " + str(limit) + " OFFSET " + str(offset))
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
            #session.user = 'rocker_'+free_hash_for_user
            session.user = None
        ip = web.ctx['ip']
        referer = web.ctx.env.get('HTTP_REFERER', 'none')
        environ = web.ctx.env.get('HTTP_USER_AGENT', 'dunno')
        visitorlog(ip,referer,environ)
        visitors, total, unique = getvisits()
        if i.edit != None:
            session.soundlink=i.edit
            raise web.seeother('/editor?public=yes') 
        if i.remove != None:
            try:
                user = db.select('published', where="soundlink='"+i.remove+"'")[0]
            except:
                pass
            try:
                user = user.creator
            except:
                user = ''
            if user == session.user:
                db.query("INSERT INTO deleted SELECT * FROM published WHERE soundlink = '"+i.remove+"'")
                db.delete('published', where='soundlink="' + i.remove + '"')
                #db.query("DELETE * FROM published WHERE soundlink ="+i.remove)
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
        return rendersplash.heartranked(db,markdown, visitors, total, unique, i.show, logged(), rights, session.user, getlikes, formattime, feedbase, tot, limit, offset, bildpersida, session.search, bilder, searchform, getcombines, timebase, getfeed, getcombofeed, userimage, postexist)
    def POST(self):
        searchform = self.form()
        i = web.input()
        if i.search != '':
            raise web.seeother('/heartranked?search='+i.search)

storage = {"content": ""}
class editor:
    def GET(self):
        if logged():
            i = web.input(publish=None, public=None, new=None, combine=None, remix=None)
            if i.combine != None:
                if session.user:
                    session.soundlink = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
                    db.insert('unpublished', soundlink=session.soundlink, description='', description2='', timeadded=datetime.datetime.now(), creator=session.user, combine=i.combine)
            if i.remix != None:
                if session.user:
                    text=''
                    text2=''
                    try:
                        olduser = db.select('unpublished', where="soundlink='"+i.remix+"'")[0]
                        text = db.select('unpublished', where="soundlink='"+i.remix+"'")[0]
                        text2 = db.select('unpublished', where="soundlink='"+i.remix+"'")[0]
                    except:
                        pass
                    try:
                        olduser = olduser.creator
                        text = text.description
                        text2 = text2.description2
                    except:
                        olduser = ''
                    if olduser != '':
                        allcreators = olduser+','+session.user
                    else:
                        allcreators = session.user
                    session.soundlink = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
                    db.insert('unpublished', soundlink=session.soundlink, description=text, description2=text2, timeadded=datetime.datetime.now(), creator=allcreators, remix=i.remix)
            if session.soundlink != '':
                if i.public=='yes':
                    try:
                        text = db.select('published', where="soundlink='"+session.soundlink+"'")[0]
                    except:
                        session.soundlink = ''
                else:
                    try:
                        text = db.select('unpublished', where="soundlink='"+session.soundlink+"'")[0]
                    except:
                        pass
                try:
                    text = text.description
                except:
                    text = ''
                if i.public=='yes':
                    try:
                        text2 = db.select('published', where="soundlink='"+session.soundlink+"'")[0]
                    except:
                        session.soundlink = ''
                else:
                    try:
                        text2 = db.select('unpublished', where="soundlink='"+session.soundlink+"'")[0]
                    except:
                        pass
                try:
                    text2 = text2.description2
                except:
                    text2 = ''
            else:
                text = ''
                text2 = ''
            if i.new == 'yes':
                session.soundlink = ''
                raise web.seeother('/editor')
            if i.publish == 'yes' and text != '' and i.public == None and logged() and len(text) < 256:
                description1 = text
                description2 = text2
                soundname = safe_filename(description1[0:27])
                #session.soundlink = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
                createpost=True
                try:
                    iftext = db.select('published', where="soundlink='"+session.soundlink+"'")[0]
                    iftext = iftext.description
                    createpost=False
                except:
                    iftext = ''
                if createpost == False:
                    db.update('published', where='soundlink="'+session.soundlink+'"', soundlink=session.soundlink, soundname=soundname, description=description1, description2=description2, timeadded=datetime.datetime.now(), creator=session.user)
                    raise web.seeother('/editor?public=yes')
                else:
                    print('make a new post')
                try:
                    db.update('unpublished', where='soundlink="'+session.soundlink+'"', soundlink=session.soundlink, soundname=soundname, description=description1, description2=description2, timeadded=datetime.datetime.now(), creator=session.user)
                except:
                    print('update unpublished')
                if createpost == True:
                    try:
                        combine = db.select('unpublished', where="soundlink='"+session.soundlink+"'")[0]
                    except:
                        pass
                    try:
                        combine = combine.combine
                    except:
                        combine = ''
                    try:
                        remix = db.select('unpublished', where="soundlink='"+session.soundlink+"'")[0]
                    except:
                        pass
                    try:
                        remix = remix.remix
                    except:
                        remix = ''
                    db.insert('published', soundlink=session.soundlink, soundname=soundname, description=description1, description2=description2, timeadded=datetime.datetime.now(), creator=session.user, combine=combine, remix=remix)
                    try:
                        l = db.query("SELECT Count(*) AS combines FROM published WHERE combine='"+combine+"';")[0]
                        #m = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+user+"';")
                        db.update('published', where='soundlink="'+combine+'"', combines=l.combines)
                    except:
                        print('fuuuuuuuuuuuuuuuuuuuuuuu COMBINES NOT UPDATING! WARNING WARNING!')
                        pass
                    raise web.seeother('/editor?public=yes')
                raise web.seeother('/editor?public=yes')
                #db.insert('pawning', pawning=i.remix, name=session.user, timeadded=datetime.datetime.now())
            return rendersplash.editor(storage, text, text2, markdown, safe_filename, session.soundlink, i.public, logged(), session.user, i.combine, i.remix)

class savepost:
    def POST(self):
        data = json.loads(web.data())
        text = data.get("text", "")
        text2 = data.get("text2", "")
        print(text)
        print(text2 +'fuuuuuuuuuuuuu')
        if session.soundlink == '':
            session.soundlink = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
            db.insert('unpublished', soundlink=session.soundlink, description=text, description2=text2, timeadded=datetime.datetime.now(), creator=session.user)
        else:
            iftext = ''
            try:
                iftext = db.select('unpublished', where="soundlink='"+session.soundlink+"'")[0]
                iftext = iftext.soundlink
            except:
                iftext = ''
            if iftext != '':
                db.update('unpublished', where='soundlink="'+session.soundlink+'"', description=text, description2=text2, timeadded=datetime.datetime.now(), creator=session.user)
            else:
                db.insert('unpublished', soundlink=session.soundlink, description=text, description2=text2, timeadded=datetime.datetime.now(), creator=session.user)
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
        i = web.input(public=None)
        if session.soundlink != '':
            if i.public == None:
                try:
                    unpublished = db.select('unpublished', where='soundlink="'+session.soundlink+'"')[0]
                    if unpublished.description == None:
                        return ''
                except:
                    print('can not find any post')
                else:
                    return markdown.markdown(unpublished.description+'\n\n---\n\n'+unpublished.description2)
            elif i.public == 'yes':
                published = db.select('published', where='soundlink="'+session.soundlink+'"')[0]
                if published.description1 == None:
                    return ''
                else:
                    return markdown.markdown(published.description1+'\n\n---\n\n'+published.description2)
            else:
                return ''

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
            saved_files = []
            try:
                # Best way for multiple files in web.py
                input_data = web.webapi.rawinput()
                uploaded = input_data.get('files')
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
                        if filetype == 'pdf' or filetype == 'txt' or filetype == 'md':
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

class uploads:
    def GET(self):
        if logged():
            uploaded = getfiles(staticdir+'upload/')
            return render.uploads(uploaded)

application = app.wsgifunc()
