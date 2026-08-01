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
    '/shop?', 'index',
    '/?', 'almost',
    '/putinbag/(.*)', 'putinbag',
    '/dropitem/(.*)?', 'dropitem',
    '/paymobile/(.*)', 'paymobile',
    '/goodies/(.*)', 'goodies',
    "/stats?", "stats",
    '/payment/(.*)', 'payment',
    '/orders?', 'orders',
    '/checkout?', 'checkout',
    '/pending', 'pending',
    '/thankyou', 'thankyou',
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
    '/products/(.*)?', 'products',
    '/bigpic/(.*)?', 'bigpic',
    '/categories?', 'categories',
    '/op', 'op',
    '/shipping/(.*)', 'shipping',
    '/propaganda?', 'propaganda',
    '/editor?', 'editor',
    '/heartranked?','heartranked',
    '/save', 'save',
    '/upload', 'upload',
    '/rendered', 'rendered',
    '/uploads?', 'uploads',
    '/config', 'config',
    '/payments?', 'payments',

bag = ''

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

def loadpost(thename):
    with open(thename, 'r') as f:
        settings = json.load(f)
        for key, i in settings.items():
            postmeta=creatpost(key,i)
    return postmeta

def savepost(thename, thelist):
    #full path to filename
    #save to next line make an ID automatically, you have to check the save to know how to load it.
    #loadfile check if record exist, first in line is the record hash and update if it exists
    #make users in a folder as files first is username username will always be user record
    #hearts will be files as usernames with timestamp in a hearts folder in post folder. be stored and checked in u/hearts and post/hearts
    # be sure to add home domain setting to username
    #make save list a dict use same names
    postmeta=loadpost(thename)
    for i in thelist:
        createpost
        
    with open(thename, "w") as f:
        #f.write(str(i) + ',')
        json.dumps(thedict,f)

def deleterecord(thefile):
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
    savepost(basedir+'users/'+name, savedict)
    print("new user added")
    return

def adminlevel(user):
    #level = db.query("SELECT adminlevel FROM rymdadmin WHERE name='"+user+"';")[0]
    level=loadpost(basedir+'users', user)
    #1 session logout, web.py bug
    #2 rights to see pics and comment
    #3 rights to upoload
    #5 superadmin
    session.login = int(level.adminlevel)
    return

def stopresetpass(mail):
    t = None
    if os.path.exists(basedir+'stopresetpass/'+mail) == True:
        t=loadpost(basedir+'stopresetpass/'+mail)
    else:
        savedict={'timeadded':time.time()}
        savepost(basedir+'stopresetpass/'+mail, savedict)
        return
    savedict={'timeadded':time.time()}
    savepost(basedir+'stopresetpass/'+mail, savedict)
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
        t=loadpost(basedir+'stopflood/'+ip)
    else:
        savedict={'timeadded':time.time()}
        savepost(basedir+'stopflood/'+ip, savedict)
        return
    savedict={'timeadded':time.time()}
    savepost(basedir+'stopflood/'+ip, savedict)
    latest = time.time() - t
    print(latest)
    if latest < 1:
        print('flooding recognized!')
        return True
    else:
        return False

def getinvitation(secretinvitation):
    invite=loadpost(basedir+'invites/'+secretinvitation)
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
            i = web.input(unlike=None, like=None, hate=None, unhate=None, user=None, uniqueunicorn=None)
            user = i.user
            uniqueunicorn = i.uniqueunicorn
            #l = db.query("SELECT * FROM likes WHERE bild='"+uniqueunicorn+"' AND user='"+session.user+"';")
            l = loadpost(basedir+'posts/'+uniqueunicorn+'/likes/'+session.user)
            print(session.user)
            print(session.user)
            print('fuuuuuuuuuuuuuuuuu')
            if l:
                user_likes = True
            else:
                user_likes = False
            if user_likes == False:
                #db.insert('likes', user=session.user, bild=uniqueunicorn, datum=datetime.datetime.now())
                savedict={'timeadded':datetime.datetime.now()}
                savepost(basedir+'posts/'+uniqueunicorn+'/likes/'+session.user, savedict)
                user_likes = True
            elif user_likes == True:
                #db.query("DELETE FROM likes WHERE bild='"+uniqueunicorn+"' AND user='"+session.user+"';")
                deleterecord(basedir+'posts/'+uniqueunicorn+'/likes/'+session.user)
                user_likes = False
            #likes = db.query("SELECT Count(*) AS likes FROM likes WHERE bild='"+uniqueunicorn+"';")[0]
            likes = len(os.listdir(basedir+'posts/'+uniqueunicorn+'/likes/'))
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
                savepost([public])
            elif data.showuploads=='yes':
                uploads = []
                uploads = get_files_by_modtime(basedir+'public_html/u/' + user + '/images/web/',newest_first=True)
                return render.showuploads(uploads,user,allowedchar, random)
            elif data.onair and data.soundname:
                #db.update('published', where="soundlink='" + data.soundname +"'", playing=data.onair)
                onair=data.onair
                savepost([onair])
            #soundname='aurora_ruderalis-greatful_bread'
            #filetype='flac'
            #soundlink = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
            #db.insert('sound', soundlink=soundlink, filename=soundname, sort=filetype, title=soundname, uploaddate=datetime.datetime.now(), uppladdare=user, lastmod=datetime.datetime.now(), moddedby=user)
            #usersounds = db.query("SELECT * FROM published WHERE creator='"+user+"' ORDER BY timeadded DESC;")
            usersound=loadpost(basedir+'posts/')
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
            user = db.select('rymdadmin', where='name="'+session.user+'"')[0]
            invites = db.select('invites', where='createdby="'+session.user+'"')
            tuningform = self.form()
            w = web.input(epost=None, render=None)
            formfail = ''
            if w.epost == '':
                formfail = formfail + 'you have to put your email in'
            if w.render == 'yes':
                secret_invite = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
                db.insert('invites', secretinvitation=secret_invite, created=datetime.datetime.now(), createdby=session.user)
            return render.invites(tuningform, formfail, user.name, invites)
    def POST(self):
        if session.login > 2:
            user = db.select('rymdadmin', where='name="'+session.user+'"')[0]
            tuningform = self.form()
            i = web.input()
            if i.mail == '':
                raise web.seeother('/invites?fail=nomail')
            if '@' not in i.mail:
                raise web.seeother('/tuning?fail=notmail') 
            secret_invite = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
            db.insert('invites', secretinvitation=secret_invite, created=datetime.datetime.now(), createdby=session.user)
            msg = "YO! You are the One! " + user.name + " is your Morpheous. Follow this rabbit https://robinbackman.com/register?invite="+secret_invite 
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
            user = db.select('rymdadmin', where='name="'+session.user+'"')[0]
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
                                db.update('rymdadmin', where='name="'+session.user+'"', displayname=i.user, password=password_hashed, mail=i.mail.lower())
                                return web.seeother('/tuning?upd=yes')
                        if '@' not in i.mail:
                            raise web.seeother('/tuning?fail=notmail')
                        #update without passwordchange
                        db.update('rymdadmin', where='name="'+session.user+'"', displayname=i.user, mail=i.mail.lower())
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
                    db.update('rymdadmin', where='name="'+p.name+'"', password=password_hashed)
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
        displayname = db.query("SELECT displayname FROM rymdadmin WHERE name='"+user+"';")[0]
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

    # Normalize unicode (é → e, etc.)
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')

    # Replace spaces and common separators with the replacement char
    name = re.sub(r'[\s_]+', replacement, name)

    # Remove any character that is not alphanumeric, hyphen, underscore, or dot
    name = re.sub(r'[^a-zA-Z0-9.\-_]', '', name)

    # Replace multiple replacement chars with single one
    name = re.sub(re.escape(replacement) + r'+', replacement, name)

    # Remove leading/trailing replacement chars and dots
    name = name.strip(replacement + '.')

    # Prevent empty or hidden files
    if not name or name.startswith('.'):
        name = "file" + name

    # Enforce max length (leave room for extension)
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
    path = Path(directory)
    
    # Get all files (exclude directories and hidden files if you want)
    files = [f for f in path.iterdir() if f.is_file()]
    
    # Sort by modification time
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
                lastupdate = os.path.getmtime(filmfolder + i + '/' + f)
                films_sorted.append((i,f,lastupdate))
        else:
            films_sorted.append((i,f,0))
    films_sorted = sorted(films_sorted, key=lambda tup: tup[2], reverse=True)
    return films_sorted

def getmacaroon():
    with open(basedir+'access.macaroon', 'rb') as f:
        m = f.read()
    #m = binascii.hexlify(m).decode()
    m = base64.b64encode(m).decode()
    return m

def createinvoice(amount, description, label):
    #Cents to EUR
    amount = str(amount*1000)
    invoice_details = {"amount":amount, "description": description, "label": label}
    print(invoice_details)
    macaroon = getmacaroon()
    headers = {'macaroon': macaroon} 
    resp = requests.post(rtl+'invoice/genInvoice', json=invoice_details, headers=headers,verify=False)
    print(resp.json())
    return resp.json()

def getinvoice(label):
    macaroon = getmacaroon()
    headers = {'macaroon': macaroon}
    resp = requests.get(rtl+'invoice/listInvoices?label='+label, headers=headers, verify=False)
    return resp.json()['invoices'][0]

def getnewaddr():
    macaroon = getmacaroon()
    headers = {'macaroon': macaroon}
    resp = requests.get(rtl+'invoice/newaddr', headers=headers, verify=False)
    return resp.json()['address'][0]

def callsubprocess(cmd):
    subprocess.call(cmd.split())

def dropitems(d):
    i = getproduct(d)
    try:
        product = db.query("SELECT * FROM customerbag WHERE sessionkey='" + session.sessionkey +"' AND product='"+str(i.id)+"';")[0]
    except:
        return 'empty'
    if product.quantity > 1:
        db.update('customerbag', where="sessionkey='" + session.sessionkey +"' and product='"+str(i.id)+"'", quantity=product.quantity-1)
        db.update('products', where="id='"+str(i.id)+"'", available=i.available+1)
    else:
        db.query("DELETE FROM customerbag WHERE sessionkey='" + session.sessionkey +"' AND product='"+str(i.id)+"';")
        db.update('products', where="id='"+str(i.id)+"'", available=i.available+1)
        return 'empty'

def addtobag(p):
    i = getproduct(p)
    if i.available > 0:
        #session.bag += (i.name, i.price, i.id),
        db.update('products', where="id='"+str(i.id)+"'", available=i.available-1)
        product = db.query("SELECT * FROM customerbag WHERE sessionkey='" + session.sessionkey +"' AND product='"+str(i.id)+"';")
        if product:
            product = product[0]
            print(product)
            db.update('customerbag', where="sessionkey='" + session.sessionkey +"' and product='"+str(i.id)+"'", quantity=product.quantity+1)
            print('gwtdafaakouttahere')
        else:
            db.insert('customerbag', sessionkey=session.sessionkey, product=i.id, type=i.type, currency=i.currency, price=i.price, quantity=1, timeadded=datetime.datetime.now())

def productname(productid):
    try:
        name = db.query("SELECT name FROM products WHERE id='"+str(productid)+"';")[0]
    except:
        return ''
    return name.name

def getproduct(productid):
    try:
        product = db.query("SELECT * FROM products WHERE id='"+str(productid)+"';")[0]
    except:
        return ''
    return product

def getcategories():
    try:
        categories = db.query("SELECT * FROM categories;")[0]
    except:
        return ''
    return categories

def ordertype():
    physical=False
    bag = db.query("SELECT * FROM customerbag WHERE sessionkey='" + session.sessionkey +"';")
    for b in bag:
        if b.type=='physical':
            return 'physical'
    return 'digital'

def getavailable(productid):
    try:
        name = db.query("SELECT available FROM products WHERE id='"+str(productid)+"';")[0]
    except:
        return ''
    return name.available

def getbtcrate():
    btc_to_euro = db.select("btcrate", where="currency='EUR'")
    #shippinginfo = db.select('shipping', where="country='" + pendinginfo.country + "'", what='price, days')[0]
    btcrate = 65619         
    return btcrate
    try:
        if time.time() - btc_to_euro[0].timeadded > 6000:
            btcrate = 64485
            b = BtcConverter()
            btcrate = int(b.get_latest_price('EUR'))
            db.update('btcrate', where='currency="EUR"', rate=btcrate, timeadded=time.time())
        else:
            btc_to_euro = db.select("btcrate", where="currency='EUR'")
            btcrate = btc_to_euro[0].rate
    except:
        db.insert('btcrate', currency='EUR', rate=64485, timeadded=time.time())

def getbtcratetime():
    btc_to_euro = db.select("btcrate", where="currency='EUR'")
    btctime = btc_to_euro[0].timeadded
    return datetime.datetime.fromtimestamp(btctime).strftime('%c')

def getprice(productid):
    p = db.query("SELECT * FROM products WHERE id='"+str(productid)+"';")[0]
    #b = BtcConverter()
    btcrate=getbtcrate()
    if p.currency=='euro':
        sat = 1/btcrate*(p.price/100) * 100000000
        #sat = b.convert_to_btc(p.price/100, 'EUR') * 100000000
        euro = p.price/100
    if p.currency=='bitcoin':
        euro = btcrate*p.price/100000000
        #euro = b.convert_btc_to_cur(p.price/100000000,'EUR')
        sat = p.price
    return int(sat), round(euro,2)

def btc_to_eur(amount):
    #b = BtcConverter()
    btcrate=getbtcrate()
    #euro = round(b.convert_btc_to_cur(amount/100000000,'EUR'),2)
    euro = round(btcrate*amount/100000000)
    return euro

def eur_to_sat(amount):
    btcrate=getbtcrate()
    #b = BtcConverter()
    #btc = b.convert_to_btc(amount/100, 'EUR')
    btc = 1/btcrate*(amount/100)
    sat=btc*100000000
    return int(sat)

def getrate():
    #b = BtcConverter()
    btcrate=getbtcrate()
    #return int(b.get_latest_price('EUR'))
    return int(btcrate)

def checkforoldbags():
    print('checking for old bags')
    bags = db.select('customerbag')
    for bag in bags:
        if datetime.datetime.now() - bag.timeadded > datetime.timedelta(minutes=6000):
            print(datetime.datetime.now() - bag.timeadded)
            print(datetime.timedelta(hours=1))
            print("Fuck")
            product = getproduct(bag.product)
            try:
                print('found a bag at door! goddamit, got to put ' + str(bag.quantity) + ' x '  + product.name + ' back on the shelf')
                if product.available > 1:
                    q = product.available + bag.quantity
                else:
                    q = bag.quantity
                db.update('products', where="id='"+str(bag.product)+"'", available=str(q))
                db.query("DELETE FROM customerbag WHERE sessionkey='" + bag.sessionkey + "'")
            except:
                pass

def checkavailable():
    print('check items from availability')
    bag = db.query("SELECT * FROM customerbag WHERE sessionkey='" + session.sessionkey + "'")
    for i in bag:
        q = getavailable(i.product)
        soldout = q - i.quantity
        if soldout < 0:
            web.seeother('/?error=soldout&prod='+str(i.product))
        else:
            return

def sold():
    print('remove items from availability')
    bag = db.query("SELECT * FROM customerbag WHERE sessionkey='" + session.sessionkey + "'")
    for i in bag:
        q = getavailable(i.product)
        soldout = q - i.quantity
        if soldout < 0:
            web.seeother('/?error=soldout')
        else:
            db.update('products', where="id='"+str(i.product)+"'", available=str(q - i.quantity))


def organizepics(product):
    imgdir = basedir+'public_html/static/img/' + str(product) + '/'
    imgdirlist = [imgdir, imgdir + 'web/', imgdir + 'thumb/']
    for d in imgdirlist:
        pics = next(os.walk(d))[2]
        organized_nr = 0
        for s in sorted(pics):
            if '.jpeg' in s:
                #print(s)
                unorganized_nr = int(s[0:3])
                if organized_nr == unorganized_nr:
                    print('correcto pic numbering')
                    pass
                if organized_nr != unorganized_nr:
                    print('false, correcting pic from ' + str(unorganized_nr) + ' to ' + str(organized_nr))
                    mv = 'mv ' + d + str(unorganized_nr).zfill(3) + '.jpeg'
                    mv2 = ' ' + d + str(organized_nr).zfill(3) + '.jpeg'
                    os.system(mv + mv2)
                organized_nr += 1

def getpendinginfo():
    try:
        pendinginfo = db.select('pending', where="invoice_key='" + session.sessionkey + "'", what='country, firstname, lastname, address, town, postalcode, email')[0]
    except:
        pendinginfo = ''
    return pendinginfo

class index():
    def GET(self):
        ip = web.ctx['ip']
        referer = web.ctx.env.get('HTTP_REFERER', 'none')
        environ = web.ctx.env.get('HTTP_USER_AGENT', 'dunno')
        visitorlog(ip,referer,environ)
        checkforoldbags()
        i = web.input(dropitem=None, putinbag=None,error=None,prod=None,category=None)
        if session.sessionkey == 'empty':
            session.sessionkey = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[15:35]
        if i.dropitem != None:
            session.bag = dropitems(i.dropitem)
            print(session.bag)
        if i.putinbag != None:
            addtobag(i.putinbag)
            return web.seeother('/shop#' + i.putinbag)
        print('Cyberpunk cafe')
        #print(session.bag)
        products = db.query("SELECT * FROM products ORDER BY priority DESC")
        try:
            bag = db.query("SELECT * FROM customerbag WHERE sessionkey='" + session.sessionkey +"';")
        except:
            bag = None
        try:
            inbag = db.query("SELECT COUNT(*) AS inbag FROM customerbag where sessionkey='" + session.sessionkey +"';")[0]
            inbag = int(inbag.inbag)
        except:
            inbag = None
        if inbag < 1:
            session.sessionkey = 'empty'
        return render.index(products,bag,session.sessionkey,productname,inbag,db,getprice,getrate,i.category, markdown)

class almost():
    def GET(self):
        ip = web.ctx['ip']
        referer = web.ctx.env.get('HTTP_REFERER', 'none')
        environ = web.ctx.env.get('HTTP_USER_AGENT', 'dunno')
        visitorlog(ip,referer,environ)
        visitors, total, unique = getvisits()
        checkforoldbags()
        i = web.input(dropitem=None, putinbag=None,error=None,prod=None,category=None,show=None)
        if session.sessionkey == 'empty':
            session.sessionkey = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[15:35]
        if i.dropitem != None:
            session.bag = dropitems(i.dropitem)
            print(session.bag)
        if i.putinbag != None:
            addtobag(i.putinbag)
            return web.seeother('/#' + i.putinbag)
        print('Cyberpunk cafe')
        #print(session.bag)
        products = db.query("SELECT * FROM products ORDER BY priority DESC")
        try:
            bag = db.query("SELECT * FROM customerbag WHERE sessionkey='" + session.sessionkey +"';")
        except:
            bag = None
        try:
            inbag = db.query("SELECT COUNT(*) AS inbag FROM customerbag where sessionkey='" + session.sessionkey +"';")[0]
            inbag = int(inbag.inbag)
        except:
            inbag = None
        if inbag < 1:
            session.sessionkey = 'empty'
        return rendersplash.almost(products,bag,session.sessionkey,productname,inbag,db,getprice,getrate,i.category, markdown, visitors, total, unique, i.show)

def visitorlog(ip, referer, environ):
    last = db.query('SELECT ip AS ip FROM visitors WHERE id=(SELECT MAX(id) FROM visitors)')
    try:
        lastip = last[0].ip
    except:
        lastip = 'none'
    if lastip != ip:
        country = ''
        country = os.popen('geoiplookup '+ip).read()
        #print(soundtype)
        countrycode = country.split(':')[1].split(',')[0].lower().strip()
        country = country.split(':')[1].split(',')[1].strip()
        #print('fuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu: '+ country)
        try:
            db.insert('visitors', ip=ip, referer=referer, environ=environ, country=country,  countrycode=countrycode, time=datetime.datetime.now())
        except:
            pass
        print("added to visitor log")
    return

def getvisitors():
    #visitors = db.select('visitors')
    visitors = db.query('SELECT * FROM visitors ORDER BY time DESC LIMIT 10000')
    total = db.query('SELECT COUNT(*) AS total_visits FROM visitors')
    unique = db.query('SELECT COUNT(DISTINCT ip) AS unique_visits FROM visitors')
    return visitors, total[0].total_visits, unique[0].unique_visits

def getvisits():
    limit=100
    visits = db.query("SELECT * FROM visitors ORDER BY time DESC LIMIT " + str(limit))
    visitors = db.select('visitors')
    total = db.query('SELECT COUNT(*) AS total_visits FROM visitors')
    unique = db.query('SELECT COUNT(DISTINCT ip) AS unique_visits FROM visitors')
    countrylist=[]
    for i in visits:
        if i.countrycode not in countrylist:
            countrylist.append(i.countrycode)
            #print('fuuuuuuuuuuuuuuu: '+i.countrycode)
    return countrylist, total[0].total_visits, unique[0].unique_visits

class stats:
    def GET(self):
        p = web.input(logfilter=None)
        visitors, total, unique = getvisitors()
        return rendersplash.stats(visitors, total, unique, p.logfilter)

class putinbag:
    def GET(self, p):
        addtobag(p)
        raise web.seeother('/')

class dropitem():
    def GET(self, d):
        referer = web.ctx.env.get('HTTP_REFERER', 'none')
        p = web.input()
        i = 0
        empty=dropitems(d)
        if empty=='empty':
            return web.seeother('/shop?#'+d)
        return web.seeother(referer)

class bigpic():
    def GET(self, i):
        print('faaaakyeee ' + i)
        p = web.input(pic=None)
        name=productname(i)
        goodies = db.query("SELECT * FROM soundlink WHERE id='"+i+"';")
        #if p.pic != None:
        return render.bigpic(i,name,goodies)

class checkout():
    t = []
    shippingcountries = db.select('shipping', what='country', order='country ASC')
    shippingcountries = list(shippingcountries)
    #t.append('Finland')
    for i in shippingcountries:
        if i.country != 'NO-SHIPPING':
            t.append(i.country)
    shipping = web.form.Form(
    web.form.Textbox('email', web.form.notnull, description="Email:"),
    web.form.Dropdown('country', t, web.form.notnull, description="Country"),
    web.form.Textbox('firstname', web.form.notnull, description="First Name:"),
    web.form.Textbox('lastname', web.form.notnull, description="Last Name:"),
    web.form.Textbox('address', web.form.notnull, description="Shipping Address:"),
    web.form.Textbox('town', web.form.notnull, description="Town / City:"),
    web.form.Textbox('postalcode', web.form.notnull, description="Postalcode / zip"),
    web.form.Button('Calculate shipping cost'))
    email = web.form.Form(
    web.form.Textbox('email', web.form.notnull, description="Email:"),
    web.form.Button('Okey, lets do it!'))
    def GET(self):
        i = web.input(error=None)
        pendinginfo = getpendinginfo()
        if ordertype()=='digital':
            checkoutform = self.email()
            if pendinginfo:
                checkoutform.fill(email=pendinginfo.email)
        if ordertype()=='physical':
            checkoutform = self.shipping()
            if pendinginfo:
                checkoutform.fill(country=pendinginfo.country, firstname=pendinginfo.firstname, lastname=pendinginfo.lastname, address=pendinginfo.address, town=pendinginfo.town, postalcode=pendinginfo.postalcode, email=pendinginfo.email)
        errormsg=''
        if i.error == 'mail':
            errormsg = 'Check your mail!'
        if i.error == 'shipping':
            errormsg = 'Check your shipping address!'
        bag = db.query("SELECT * FROM customerbag WHERE sessionkey='" + session.sessionkey +"';")
        return render.checkout(checkoutform,bag,productname,errormsg,db,getprice)
    def POST(self):
        physical=False
        bag = db.query("SELECT * FROM customerbag WHERE sessionkey='" + session.sessionkey +"';")
        checkoutform = self.email()
        for b in bag:
            if b.type=='physical':
                checkoutform = self.shipping()
                physical=True
                break
        errormsg=''
        pendinginfo = getpendinginfo()
        i = web.input()
        if pendinginfo:
            if physical==True:
                db.update('pending', where="invoice_key='"+session.sessionkey+"'", invoice_key=session.sessionkey, country=i.country, firstname=i.firstname, lastname=i.lastname, address=i.address, town=i.town, postalcode=str(i.postalcode), email=i.email, dateadded=datetime.datetime.now())
            else:
                db.update('pending', where="invoice_key='"+session.sessionkey+"'", invoice_key=session.sessionkey, email=i.email, dateadded=datetime.datetime.now())
        else:
            if physical==True:
                db.insert('pending', invoice_key=session.sessionkey, country=i.country, firstname=i.firstname, lastname=i.lastname, address=i.address, town=i.town, postalcode=str(i.postalcode), email=i.email, dateadded=datetime.datetime.now())
            else:
                db.insert('pending', invoice_key=session.sessionkey, email=i.email, dateadded=datetime.datetime.now())
        if '@' not in i.email:
            web.seeother('/checkout?error=mail')
        elif not checkoutform.validates():
            return web.seeother('/checkout?error=shipping')
        else:
            return web.seeother('/pending')

class pending:
    #form = web.form.Form(
    #web.form.Dropdown('payment', ['Bitcoin Lightning', 'Bitcoin'], web.form.notnull, description="Select payment method"),
    #web.form.Button('Pay'))
    form = web.form.Form(
    web.form.Button('Pay'))
    def GET(self):
        pendingform = self.form()
        pendinginfo = getpendinginfo()
        bag = db.query("SELECT * FROM customerbag WHERE sessionkey='" + session.sessionkey +"';")
        return render.pending(session.sessionkey,pendingform,pendinginfo,bag,productname,db,getprice,eur_to_sat,ordertype)
    def POST(self):
        pendingform = self.form()
        pendinginfo = getpendinginfo()
        i = web.input()

        #Calculate total amount of bag
        totalamount = 0
        description = ''
        bag = db.query("SELECT * FROM customerbag WHERE sessionkey='" + session.sessionkey +"';")
        comma = ''
        for s in bag:
            totalamount += getprice(s.product)[0] * s.quantity
            description += comma + str(s.quantity) + ' x ' + productname(s.product)
            comma = ', '
        if ordertype()=='physical':
            shippinginfo = db.select('shipping', where="country='" + pendinginfo.country + "'", what='price, days')[0]
            totalamount += eur_to_sat(shippinginfo.price)
        totsats=totalamount
        totbtc=totsats/100000000

        #make lightning invoice
        
        #print(str(totalamount) + ' | ' +  description)
        #print(str(totsats) + ' | ' +  description)
        #label = hashlib.sha256(str(random.getrandbits(64)).encode('utf-8')).hexdigest()[15:35]
        #invoice = createinvoice(totsats, description, label)
        #time.sleep(1)
        
        #print(invoice)
        #callsubprocess('qrencode -s 3 -o '+ staticdir + 'qr/' + session.sessionkey+'.png '+invoice['bolt11'])
        #make bitcoin address
        #bitcoinrpc = AuthServiceProxy(rpcauth)
        #newaddress = bitcoinrpc.getnewaddress('Tarina Shop Butik')
        #bitcoinrpc = None
        #btcuri = 'bitcoin:' + newaddress + '?amount=' + str(totbtc) + '&label=' + description
        #callsubprocess('qrencode -s 5 -o '+ staticdir + 'qr/' + newaddress +'.png ' + btcuri)
        #try:
        #    db.query("DELETE FROM invoices WHERE invoice_key='"+session.sessionkey+"';")
        #except:
        #    print('no old invoices to delete')
        db.insert('invoices', invoice_key=session.sessionkey, products=description, amount=totalamount, totsats=totsats, status='unpaid', timestamp=time.strftime('%Y-%m-%d %H:%M:%S'))
        msg="sup Robin? wowoweewaa! someone made an order."
        sendmail('me@robinbackman.com', 'A message from Robins webshop', msg)
        return web.seeother('/paymobile/' + session.sessionkey)

class paymobile:
    def GET(self, invoice_key):
        digitalkey = None
        invoice = db.select('invoices', where="invoice_key='"+invoice_key+"'")[0]
        lninvoice=''
        #lninvoice = getinvoice(invoice['ln'])
        if invoice.status == 'paid' and session.sessionkey != 'empty':
            bag = db.query("SELECT * FROM customerbag WHERE sessionkey='"+invoice_key+"';")
            customer = db.select('pending', where="invoice_key='"+invoice_key+"'")[0]
            db.query("INSERT INTO paidbags SELECT * FROM customerbag WHERE sessionkey='" + invoice_key + "'")
            db.query("DELETE FROM customerbag WHERE sessionkey='" + invoice_key + "'")
            db.update("invoices",where='invoice_key="'+invoice_key+'"', status='paid')
            digitalkey=hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[15:35]
            db.insert('digitalkey', invoice_key=invoice_key, digitalkey=digitalkey, email=customer.email)
            session.sessionkey = 'empty'
            # send mail to op
            if ordertype()=='physical':
                msg = 'You got a new order, from ' + customer.firstname + ' ' + customer.lastname + ' from ' + customer.country + ' email: ' + customer.email + ' this dude wantz ' + invoice.products
            else:
                msg='sup?'
            sendmail(webmaster, 'Robs Shop', msg)
            # send mail to customer
            if ordertype()=='physical':
                msg = "Thank you for order " + invoice.products + " at Robins webshop, we'll be processing your order as soon as possible and send it to " + customer.firstname + ' ' + customer.lastname + ', ' + customer.address + ', ' + str(customer.postalcode) + ', ' + customer.town + ', ' + customer.country + '. To pay/view status or take a look at the digital goodies of your order please visit ' + baseurl + '/goodies/'+digitalkey
            else:
                msg="sup? thanks! here's a link to the digital goodies "+baseurl+'/goodies/'+digitalkey
            sendmail(customer.email, 'A message from Robins webshop', msg)
            web.seeother('/paymobile/'+invoice_key)
        elif invoice.status == 'paid':
            bag = db.query("SELECT * FROM paidbags WHERE sessionkey='"+invoice_key+"';")
            digitalkey = db.select('digitalkey', where="invoice_key='"+invoice_key+"'")[0]
        elif invoice.status != 'paid':
            bag = db.query("SELECT * FROM customerbag WHERE sessionkey='"+invoice_key+"';")
        pendinginfo = getpendinginfo()
        return render.paymobile(lninvoice,invoice,bag,productname,digitalkey,db,getprice,getrate,ordertype,pendinginfo,eur_to_sat)

class payln:
    def GET(self, invoice_key):
        digitalkey = None
        invoice = db.select('invoices', where="invoice_key='"+invoice_key+"'")[0]
        lninvoice = getinvoice(invoice['ln'])
        if lninvoice['status'] == 'paid' and session.sessionkey != 'empty':
            bag = db.query("SELECT * FROM customerbag WHERE sessionkey='"+invoice_key+"';")
            customer = db.select('pending', where="invoice_key='"+invoice_key+"'")[0]
            db.query("INSERT INTO paidbags SELECT * FROM customerbag WHERE sessionkey='" + invoice_key + "'")
            db.query("DELETE FROM customerbag WHERE sessionkey='" + invoice_key + "'")
            db.update("invoices",where='invoice_key="'+invoice_key+'"', status='paid')
            digitalkey=hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[15:35]
            db.insert('digitalkey', invoice_key=invoice_key, digitalkey=digitalkey, email=customer.email)
            session.sessionkey = 'empty'
            # send mail to op
            if ordertype()=='physical':
                msg = 'You got a new order, from ' + customer.firstname + ' ' + customer.lastname + ' from ' + customer.country + ' email: ' + customer.email + ' this dude wantz ' + lninvoice['description']
            else:
                msg='sup?'
            sendmail(webmaster, 'Robs Shop', msg)
            # send mail to customer
            if ordertype()=='physical':
                msg = "Thank you for order " + lninvoice['description'] + " at Robins webshop, we'll be processing your order as soon as possible and send it to " + customer.firstname + ' ' + customer.lastname + ', ' + customer.address + ', ' + str(customer.postalcode) + ', ' + customer.town + ', ' + customer.country + '. To pay/view status or take a look at the digital goodies of your order please visit ' + baseurl + '/goodies/'+digitalkey
            else:
                msg="sup? thanks! here's a link to the digital goodies "+baseurl+'/goodies/'+digitalkey
            sendmail(customer.email, 'A message from Robins webshop', msg)
            web.seeother('/payln/'+invoice_key)
        if lninvoice['status'] == 'paid':
            bag = db.query("SELECT * FROM paidbags WHERE sessionkey='"+invoice_key+"';")
            digitalkey = db.select('digitalkey', where="invoice_key='"+invoice_key+"'")[0]
        if lninvoice['status'] != 'paid':
            bag = db.query("SELECT * FROM customerbag WHERE sessionkey='"+invoice_key+"';")
        pendinginfo = getpendinginfo()
        return render.payln(lninvoice,invoice,bag,productname,digitalkey,db,getprice,getrate,ordertype,pendinginfo,eur_to_sat)

class goodies():
    def GET(self, digitalkey):
        digitalkey = db.select('digitalkey', where="digitalkey='"+digitalkey+"'")[0]
        #digitalkeys = db.select('digitalkey', where="email='"+digitalkey.email+"'")
        digitalkeys = db.query("SELECT * FROM digitalkey WHERE email='"+digitalkey.email+"' ORDER BY timeadded DESC;")
        return render.goodies(digitalkey,digitalkeys,productname,db,getprice)
        #check all puraches with same email fuck ye

class paybtc:
    def GET(self, invoice_key):
        invoice = db.select('invoices', where="invoice_key='" + invoice_key + "'", what='invoice_key, btc, ln, products, payment, amount, totsats, timestamp, status, datepaid, dateshipped')[0]
        totbtc = float(invoice.totsats * 0.00000001)
        btcaddress = invoice.btc
        btcuri = 'bitcoin:' + btcaddress + '?amount=' + str(totbtc) + '&label=' + invoice.products
        bitcoinrpc = AuthServiceProxy(rpcauth)
        showpayment = bitcoinrpc.listreceivedbyaddress(0, True, True, btcaddress)
        bitcoinrpc = None
        if showpayment:
            for i in showpayment:
                confirmations = int(i['confirmations'])
                print(str(confirmations))
            if invoice.datepaid == None and confirmations > 6:
                msg = 'Robins webshop order update! someone sent you Bitcoin! ' + baseurl + '/paybtc/' + invoice.invoice_key
                print(msg)
                sendmail(webmaster, 'Robs Shop', msg)
                db.update('invoices', where="invoice_key='" + invoice.invoice_key + "'", status='paid', datepaid=time.strftime('%Y-%m-%d %H:%M:%S'))
        pendinginfo = getpendinginfo()
        bag = db.query("SELECT * FROM customerbag WHERE sessionkey='"+invoice_key+"';")
        return render.paybtc(invoice, btcaddress, btcuri, showpayment, bag, productname, db, getprice, getrate, ordertype, pendinginfo, eur_to_sat)

class orders():
    def GET(self):
        if logged():
            referer = web.ctx.env.get('HTTP_REFERER', 'none')
            listpayments=[]
            i=web.input(key=None,status=None)
            if i.key != None and i.status != None:
                db.update('invoices', where="invoice_key='" + i.key + "'", status=i.status)
                #get the right invoice send mail
                customer = db.select('pending', where="invoice_key='" + i.key + "'", what='country, firstname, lastname, address, town, postalcode, email')[0]
                payment = db.select('invoices', where="invoice_key='" + i.key + "'", what='btc, ln, invoice_key, products, payment, amount, totsats, timestamp, status, datepaid, dateshipped')[0]
                if payment.payment == 'Bitcoin':
                    paylink = 'paybtc/'
                elif payment.payment == 'Bitcoin Lightning':
                    paylink = 'payln/'
                elif payment.payment == 'Mobile Pay':
                    paylink = 'paymobile/'
                if i.status == 'thankyou':
                    msg="Hi " + customer.email + ", thank you for your order! You can track the status of your order at "+baseurl+'/'+paylink+i.key
                    sendmail(customer.email, 'Robs Shop, a thank you!', msg)
                elif i.status == 'shipped':
                    digitalkey = db.query("SELECT * FROM digitalkey WHERE email='"+customer.email+"' ORDER BY timeadded ASC;")[0]
                    # send mail to customer
                    try:
                        msg = "Your order at Robins webshop has been shipped to " + customer.firstname + ' ' + customer.lastname + ', ' + customer.address + ', ' + str(customer.postalcode) + ', ' + customer.town + ', ' + customer.country + '. To pay/view status or take a look at the digital goodies of your order please visit ' + baseurl + '/goodies/'+digitalkey.digitalkey
                    except:
                        msg = "Hi " + customer.email + ". To pay/view status or take a look at the digital goodies of your order please visit " + baseurl + '/goodies/'+digitalkey.digitalkey
                    sendmail(customer.email, 'Rob Shop, your order has been shipped!', msg)
                elif i.status == 'paynotice':
                    msg="Hi " + customer.email + ", we noticed you have an unpaid order in our shop, thank you. You can track the status of your order at " + baseurl + paylink + payment.invoice_key
                    sendmail(customer.email, 'Rob Shop, order waiting for payment!', msg)
                elif i.status == 'paid':
                    digitalkey = db.query("SELECT * FROM digitalkey WHERE email='"+customer.email+"' ORDER BY timeadded ASC;")[0]
                    # send mail to customer
                    msg="Hi " + customer.email + ", thank you! payment received. You can track the status of your order and view the status or take a look at the digital goodies of your order at " + baseurl + '/goodies/'+digitalkey.digitalkey
                    sendmail(customer.email, 'Rob Shop, order payment received', msg)
                raise web.seeother(referer)
            payments = db.select('invoices', what='btc, ln, invoice_key, products, payment, amount, totsats, timestamp, status, datepaid, dateshipped', order='timestamp DESC')
            if i.key == None and i.status != None:
                status = i.status
            else:
                status = ''
            totsats = 0
            paid = 0
            unpaid = 0
            shipped = 0
            nonshipped = 0
            pickup = 0
            removed=0
            thankyou=0
            for i in payments:
                if i.status == 'paid':
                    paid=paid+1
                    nonshipped=nonshipped+1
                elif i.status == 'unpaid':
                    unpaid=unpaid+1
                    nonshipped=nonshipped+1
                elif i.status == 'shipped':
                    shipped=shipped+1
                elif i.status == 'paid':
                    nonshipped=nonshipped+1
                elif i.status == 'pickup':
                    pickup=pickup+1
                elif i.status == "removed":
                    removed=removed+1
                elif i.status != "thankyou":
                    thankyou=thankyou+1
            payments = db.select('invoices', order='timestamp DESC')
            return renderop.orders(payments,db,getinvoice,totsats,status,paid,unpaid,shipped,nonshipped,pickup,removed,thankyou,productname,getprice)
        else:
            raise web.seeother('/login')

class ordersbtcold():
    def GET(self):
        referer = web.ctx.env.get('HTTP_REFERER', 'none')
        listpayments=[]
        i=web.input(key=None,status=None)
        if i.key != None and i.status != None:
            db.update('invoices', where="invoice_key='" + i.key + "'", status=i.status)
            #get the right invoice send mail
            customer = db.select('pending', where="invoice_key='" + i.key + "'", what='country, firstname, lastname, address, town, postalcode, email')[0]
            payment = db.select('invoices', where="invoice_key='" + i.key + "'", what='btc, ln, invoice_key, products, payment, amount, totsats, timestamp, status, datepaid, dateshipped')[0]
            if payment.payment == 'Bitcoin':
                paylink = 'paybtc/'
            elif payment.payment == 'Bitcoin Lightning':
                paylink = 'payln/'
            if i.status == 'thankyou':
                msg="Hi " + customer.email + ", thank you for your order! You can track the status of your order at "+baseurl+'/'+paylink+i.key
                sendmail(customer.email, 'Robs Shop, a thank you!', msg)
            elif i.status == 'shipped':
                msg="Hi " + customer.email + ", your order has been shipped!. You can track the status of your order at "+baseurl+'/'+paylink+i.key
                sendmail(customer.email, 'Rob Shop, your order has been shipped!', msg)
            elif i.status == 'paynotice':
                msg="Hi " + customer.email + ", we noticed you have an unpaid order in our shop, thank you. You can track the status of your order at " + baseurl + paylink + payment.invoice_key
                sendmail(customer.email, 'Rob Shop, order waiting for payment!', msg)
            elif i.status == 'paid':
                msg="Hi " + customer.email + ", thank you! payment received. You can track the status of your order at " + baseurl + paylink + payment.invoice_key
                sendmail(customer.email, 'Rob Shop, order payment received', msg)
            raise web.seeother(referer)
        payments = db.select('invoices', what='btc, ln, invoice_key, products, payment, amount, totsats, timestamp, status, datepaid, dateshipped', order='timestamp DESC')
        if i.key == None and i.status != None:
            status = i.status
        else:
            status = ''
        totsats = 0
        paid = 0
        unpaid = 0
        shipped = 0
        nonshipped = 0
        pickup = 0
        removed=0
        for i in payments:
            ln = getinvoice(i.ln)
            print(ln)
            if ln['status'] == 'paid':
                totsats=totsats+ln['amount_msat']
                paid=paid+1
                s = db.select('invoices', where="invoice_key='"+i.invoice_key+"'", what='status')[0]
                if s.status == None:
                    db.update('invoices', where="invoice_key='"+i.invoice_key+"'", status='paid', datepaid=time.strftime('%Y-%m-%d %H:%M:%S'))
                if i.status == 'shipped':
                    shipped=shipped+1
                if i.status == 'paid':
                    nonshipped=nonshipped+1
                if i.status == 'pickup':
                    pickup=pickup+1
                if i.status == "removed":
                    removed=removed+1
            else:
                s = db.select('invoices', where="invoice_key='"+i.invoice_key+"'", what='status')[0]
                if s.status == None:
                    db.update('invoices', where="invoice_key='"+i.invoice_key+"'", status='unpaid', datepaid=time.strftime('%Y-%m-%d %H:%M:%S'))
                if i.status != "removed":
                    unpaid=unpaid+1
                if i.status == "removed":
                    removed=removed+1
        payments = db.select('invoices', order='timestamp DESC')
        return renderop.orders(payments,db,getinvoice,totsats,status,paid,unpaid,shipped,nonshipped,pickup,removed,productname,getprice)

class payment:
    def GET(self, invoice_key):
        id = db.where('invoices', invoice_key=invoice_key)[0]['ln']
        invoice = getinvoice(id)
        return render.payment(invoice)

class thankyou:
    def GET(self, id):
        return render.thankyou(id)

class loginold:
    form = web.form.Form(
    web.form.Textbox('user', web.form.notnull, description="User"),
    web.form.Password('password', web.form.notnull, description="Passcode"),
    web.form.Button('Login'))
    def GET(self):
        if not logged():
            loginform = self.form()
            return render.login(loginform)
        else:
            raise web.seeother('/op')
    def POST(self):
        loginform = self.form()
        if not loginform.validates():
            return render.login(loginform)
        else:
            i = web.input()
            if (i.user,i.password) in allowed:
                session.login = 1
                raise web.seeother('/op')
            else:
                return render.login(loginform)

class logout:
    def GET(self):
        session.login = 0
        session.user = None
        raise web.seeother('/heartranked')

class op:
    def GET(self):
        if logged():
            return renderop.operator()
        else:
            raise web.seeother('/login')

class propaganda:
    form = web.form.Form(
    web.form.Textbox('name', web.form.notnull, description="site name"),
    web.form.Textarea('description', web.form.notnull, description="write here"),
    web.form.Textarea('description2', web.form.notnull, description="write more here"),
    web.form.Button('Save'))
    picform = web.form.Form(
    web.form.Textbox('name', web.form.notnull, description="upload images"),
    web.form.Textarea('description', web.form.notnull, description="write even more here"),
    web.form.Textarea('description2', web.form.notnull, description="write even here more"),
    web.form.Textarea('id', web.form.notnull, description="id:"),
    web.form.Button('Save'))
    def GET(self):
        if logged():
            i = web.input(cmd=None,soundname=None)
            nocache = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[11:15]
            story = None
            if i.cmd == 'remove' and i.soundname != None:
                try:
                    os.remove(staticdir+'/img/thumb/'+i.soundname)
                    os.remove(staticdir+'/img/web/'+i.soundname)
                except:
                    print('notin to delete')
                goodies = db.query("DELETE FROM propagandapics WHERE soundname='"+i.soundname+"';")
                raise web.seeother('/propaganda')
            elif i.cmd == 'flipright' and i.soundname != None:
                original_thumb = Image.open(staticdir+'/img/thumb/'+i.soundname) 
                original_web = Image.open(staticdir+'/img/web/'+i.soundname) 
                o_thumb=original_thumb.rotate(270)
                o_web=original_web.rotate(270)
                o_thumb.save(staticdir+'/img/thumb/'+i.soundname)
                o_web.save(staticdir+'/img/web/'+i.soundname)
                raise web.seeother('/propaganda')
            elif i.cmd == 'flipleft' and i.soundname != None:
                original_thumb = Image.open(staticdir+'/img/thumb/'+i.soundname) 
                original_web = Image.open(staticdir+'/img/web/'+i.soundname) 
                o_thumb=original_thumb.rotate(90)
                o_web=original_web.rotate(90)
                o_thumb.save(staticdir+'/img/thumb/'+i.soundname)
                o_web.save(staticdir+'/img/web/'+i.soundname)
                raise web.seeother('/propaganda')
            elif i.soundname != None:
                story = db.query("SELECT * FROM propagandapics WHERE soundlink='"+i.soundname+"';")
            goodies = db.query("SELECT * FROM propagandapics;")
            configsite = self.form()
            picturetext = self.picform()
            try:
                oldsiteconfig = db.select('propaganda', what='id, name, description, description2')[0]
                configsite.fill(name=oldsiteconfig.name, description=oldsiteconfig.description, description2=oldsiteconfig.description2)
            except:
                print('no non no')
            bilder_totalt = db.query("SELECT COUNT(*) AS stories FROM propagandapics")[0]
            return renderop.propaganda(configsite, picturetext, goodies, nocache, story)
        else:
            raise web.seeother('/login')
    def POST(self):
        addcategory = self.form()
        i = web.input(imgfile={}, name=None, id=None)
        if i.id != None:
            db.update('propagandapics', where='soundlink="'+i.id+'"', name=i.name, description=i.description, description2=i.description2, soundlink=i.id)
            raise web.seeother('/propaganda')
        if i.name != None:
            #db.insert('propaganda', name=i.name, description=i.description, description2=i.description2 )
            db.update('propaganda', where='id=1', name=i.name, description=i.description, description2=i.description2 )
        if i.imgfile != {}:
            if i.imgfile.filename == '':
                print('hmmm... no image to upload')
                raise web.seeother('/config/')
            print('YEAH, Upload image!')
            ##---------- UPLOAD IMAGE ----------
            filepath=i.imgfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
            #split and only take the filename with extension
            #soundpath=filepath.split('/')[-1]
            #if soundpath == '':
            #    return render.nope("strange, no filename found!")
            #get filetype, last three 
            imgname=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            filetype = imgname.split('.')[-1].lower()
            if filetype == 'jpg':
                filetype = 'jpeg'
            soundname = imgname.split('.')[0]
            #lets remove unwanted characters yes please!
            sound = ''
            for p in soundname.lower():
                if p in allowedchar:
                    sound = sound + p
            if sound == '':
                raise web.seeother('/upload?fail=wierdname')
            soundname = sound + '_Gonzo_Pi.' + filetype
            print(soundname)
            print("filename is " + imgname + " filetype is " + filetype + " soundname is " + soundname + " trying to upload file from: " + filepath)
            #if filetype != 'wav' or 'ogg' or 'flac' or 'jpeg' or 'jpg' or 'mp3':
            #    web.seeother('/upload?fail=notsupported')
            #uniqueunicorn = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
            #imgname = uniqueunicorn
            #imgname = str(len(os.listdir(imgdir))).zfill(3) + '.jpeg'
            soundlink = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
            imgdir = staticdir+'upload/'+soundlink+'/'
            os.system('mkdir -p ' + imgdir)
            fout = open(imgdir + soundname,'wb') # creates the file where the uploaded file should be stored
            fout.write(i.imgfile.file.read()) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete. 
            db.insert('propagandapics', soundlink=soundlink, soundname=soundname, name='', description='', description2='',timeadded=datetime.datetime.now())
            if filetype == 'jpeg' or filetype == 'png':
                ##---------- OPEN FILE & CHEKC IF JPEG --------
                image = Image.open(imgdir + soundname)
                #if image.format != 'JPEG':
                #    os.remove(imgdir +'/'+ soundname)
                #    raise web.seeother('/products/' + idvalue)

                ##---------- RESIZE IMAGE SAVE TO PRODUCT-----------
                imgdir=staticdir+'img'
                try:
                    os.makedirs(imgdir + '/web/', exist_ok=True)
                    os.makedirs(imgdir + '/thumb/', exist_ok=True)
                except:
                    print('Folders is')
                image.resize((1500,1500), Image.LANCZOS)
                image.save(imgdir + '/web/'+soundname)
                image.resize((500,500), Image.LANCZOS)
                image.save(imgdir + '/thumb/'+soundname) 
        raise web.seeother('/propaganda')

def word_break(text: str, width: int = 140) -> str:
    """
    Breaks text into lines at word boundaries, with max line length = width.
    Returns a single string with '\n' inserted.
    """
    if not text:
        return ""
    
    words = text.split()
    if not words:
        return ""
    
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        # Length if we add this word (+ space if not first word in line)
        word_len = len(word)
        if current_line:
            added_len = word_len + 1  # +1 for space
        else:
            added_len = word_len
        
        if current_length + added_len > width:
            # Finish current line and start new one
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = word_len
        else:
            current_line.append(word)
            current_length += added_len
    
    # Don't forget the last line
    if current_line:
        lines.append(" ".join(current_line))
    
    return "\n".join(lines)

def getlikes(postid, user):
    user_likes = False
    l = db.query("SELECT Count(*) AS likes FROM likes WHERE bild='"+postid+"';")[0]
    db.update('published', where='soundlink="'+postid+'"', hearts=l.likes)
    if user:
        m = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+user+"';")
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
        l = db.select('published', where="soundlink='"+postid+"'")[0]
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
    l = db.query("SELECT Count(*) AS combines FROM published WHERE combine='"+postid+"';")[0]
    #m = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+user+"';")
    #db.update('published', where='soundlink="'+postid+'"', combines=0)
    if l.combines > 0:
            return "⚭ " + str(l.combines)
    else:
        return ''

def pushcombines(postid):
    l = db.query("SELECT Count(*) AS combines FROM published WHERE soundlink='"+postid+"';")[0]
    #m = db.query("SELECT * FROM likes WHERE bild='"+postid+"' AND user='"+user+"';")
    db.update('published', where='soundlink="'+postid+'"', combines=l.combines)
    if l.combines >= 0:
            return "⚭ " + str(l.combines)
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
    if feedbase == "heart" and timebase == "today":
        now = datetime.datetime.now()
        one_day_before = now - datetime.timedelta(days=1)
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        one_day_before=one_day_before.strftime('%Y-%m-%d %H:%M:%S')
        goodies = db.query("SELECT * FROM published WHERE timeadded BETWEEN '"+one_day_before+"' AND '"+now+"' ORDER BY hearts DESC LIMIT 1000;")
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

class save:
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

class config:
    form = web.form.Form(
    web.form.Textbox('name', web.form.notnull, description="Site name:"),
    web.form.Textarea('description', web.form.notnull, description="Slogan:"),
    web.form.Textarea('description2', web.form.notnull, description="Description:"),
    web.form.Button('Save'))
    def GET(self):
        if logged():
            configsite = self.form()
            try:
                oldsiteconfig = db.select('siteconfig', what='id, name, description, description2')[0]
                configsite.fill(name=oldsiteconfig.name, description=oldsiteconfig.description, description2=oldsiteconfig.description2)
            except:
                print('no non no')
            return renderop.config(configsite)
        else:
            raise web.seeother('/login')
    def POST(self):
        if logged():
            addcategory = self.form()
            i = web.input(imgfile={}, name=None)
            if i.name != None:
                db.update('siteconfig', where='id=1', name=i.name, description=i.description, description2=i.description2 )
            if i.imgfile != {}:
                if i.imgfile.filename == '':
                    print('hmmm... no image to upload')
                    raise web.seeother('/config/')
                print('YEAH, Upload image!')

                ##---------- UPLOAD IMAGE ----------

                filepath=i.imgfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
                #split and only take the filename with extension
                #soundpath=filepath.split('/')[-1]
                #if soundpath == '':
                #    return render.nope("strange, no filename found!")
                #get filetype, last three 
                imgname=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
                filetype = imgname.split('.')[-1].lower()
                if filetype == 'jpg':
                    filetype = 'jpeg'
                soundname = imgname.split('.')[0]
                #lets remove unwanted characters yes please!
                sound = ''
                for p in soundname.lower():
                    if p in allowedchar:
                        sound = sound + p
                if sound == '':
                    raise web.seeother('/upload?fail=wierdname')
                soundname = 'logo.' + filetype
                print(soundname)
                print("filename is " + imgname + " filetype is " + filetype + " soundname is " + soundname + " trying to upload file from: " + filepath)
                #if filetype != 'wav' or 'ogg' or 'flac' or 'jpeg' or 'jpg' or 'mp3':
                #    web.seeother('/upload?fail=notsupported')
                #uniqueunicorn = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
                #imgname = uniqueunicorn
                #imgname = str(len(os.listdir(imgdir))).zfill(3) + '.jpeg'
                soundlink = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
                imgdir = staticdir+'upload/'
                os.system('mkdir -p ' + imgdir)
                fout = open(imgdir + soundname,'wb') # creates the file where the uploaded file should be stored
                fout.write(i.imgfile.file.read()) # writes the uploaded file to the newly created file.
                fout.close() # closes the file, upload complete.
                
                if filetype == 'jpeg' or filetype == 'png':
                    ##---------- OPEN FILE & CHEKC IF JPEG --------

                    image = Image.open(imgdir + soundname)
                    #if image.format != 'JPEG':
                    #    os.remove(imgdir +'/'+ soundname)
                    #    raise web.seeother('/products/' + idvalue)

                    ##---------- RESIZE IMAGE SAVE TO PRODUCT-----------

                    imgdir=staticdir+'img'
                    try:
                        os.makedirs(imgdir + '/web/', exist_ok=True)
                        os.makedirs(imgdir + '/thumb/', exist_ok=True)
                    except:
                        print('Folders is')
                    image.resize((900,900), Image.LANCZOS)
                    image.save(imgdir + '/web/'+soundname)
                    image.resize((300,300), Image.LANCZOS)
                    image.save(imgdir + '/thumb/'+soundname) 
            raise web.seeother('/config')
        else:
            raise web.seeother('/login')

class categories:
    form = web.form.Form(
    web.form.Textbox('category', web.form.notnull, description="Add Category:"),    
    web.form.Button('Add'))
    def GET(self):
        if logged():
            i = web.input(delete=None)
            if i.delete:
                db.delete('categories', where='id='+i.delete)
            listcategories = db.query("SELECT * FROM categories ORDER BY id DESC")
            addcategory = self.form()
            return renderop.categories(listcategories,addcategory)
        else:
            raise web.seeother('/login')
    def POST(self):
        addcategory = self.form()
        i = web.input()
        db.insert('categories', category=i.category)
        raise web.seeother('/categories')


class products:
    listcategories = db.query("SELECT * FROM categories ORDER BY id DESC")
    p = []
    for i in listcategories:
        p.append(i.category)
    #p = listcategories[0]
    form = web.form.Form(
    web.form.Dropdown('category', p, web.form.notnull, description="Category:"),
    web.form.Textbox('name', web.form.notnull, description="Name:"),
    web.form.Textarea('description', web.form.notnull, description="Description:"),
    web.form.Radio('type', ['digital', 'physical'],description="Type:"),
    web.form.Radio('currency', ['euro', 'bitcoin'],description="Currency:"),
    web.form.Textbox('price', web.form.notnull, description="Price:"),
    web.form.Textbox('available', web.form.notnull, web.form.regexp(r'\d+', 'number dumbass!'), description="Available"),
    web.form.Textbox('priority', web.form.notnull, web.form.regexp(r'\d+', 'number dumbass!'), description="Priority (high value more priority)"),
    web.form.Button('Save'))
    def GET(self, idvalue):
        if logged():
            i = web.input(cmd=None,soundname=None)
            nocache = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[11:15]
            if i.cmd == 'del':
                db.delete('products', where='id="'+idvalue+'"')
                imgdir = staticdir + 'img/' + idvalue
                try:
                    shutil.rmtree(imgdir,ignore_errors=True,onerror=None)
                except:
                    print('no picture folder, nothing to remove...')
                    pass
                raise web.seeother('/products/')
            if i.cmd == 'remove' and i.soundname != None:
                try:
                    os.remove(staticdir+'/img/thumb/'+i.soundname)
                    os.remove(staticdir+'/img/web/'+i.soundname)
                except:
                    print('notin to delete')
                goodies = db.query("DELETE FROM soundlink WHERE id='"+idvalue+"' AND soundname='"+i.soundname+"';")
                raise web.seeother('/products/' + idvalue)
            if i.cmd == 'flipright' and i.soundname != None:
                original_thumb = Image.open(staticdir+'/img/thumb/'+i.soundname) 
                original_web = Image.open(staticdir+'/img/web/'+i.soundname) 
                o_thumb=original_thumb.rotate(270)
                o_web=original_web.rotate(270)
                o_thumb.save(staticdir+'/img/thumb/'+i.soundname)
                o_web.save(staticdir+'/img/web/'+i.soundname)
                raise web.seeother('/products/' + idvalue)
            if i.cmd == 'flipleft' and i.soundname != None:
                original_thumb = Image.open(staticdir+'/img/thumb/'+i.soundname) 
                original_web = Image.open(staticdir+'/img/web/'+i.soundname) 
                o_thumb=original_thumb.rotate(90)
                o_web=original_web.rotate(90)
                o_thumb.save(staticdir+'/img/thumb/'+i.soundname)
                o_web.save(staticdir+'/img/web/'+i.soundname)
                raise web.seeother('/products/' + idvalue)
            addproduct = self.form()
            addproduct.fill(available='1', priority='1', type='physical',currency='euro')
            goodies = None
            if idvalue:
                oldinfo = db.query("SELECT * FROM products WHERE id='"+idvalue+"';")[0]
                addproduct.fill(name=oldinfo.name, description=oldinfo.description, type=oldinfo.type, currency=oldinfo.currency, price=oldinfo.price, available=oldinfo.available, priority=oldinfo.priority, category=oldinfo.category)
                goodies = db.query("SELECT * FROM soundlink WHERE id='"+idvalue+"';")
            listproducts = db.query("SELECT * FROM products ORDER BY priority DESC")
            return renderop.products(addproduct, listproducts, goodies, idvalue, nocache)
        else:
            raise web.seeother('/login') 
    def POST(self, idvalue):
        listproducts = db.query("SELECT * FROM products ORDER BY priority DESC")
        addproduct = self.form()
        if logged():
            i = web.input(imgfile={},name=None,description=None,price=1,available=1)
            #for p in i:q
            #    print(p)
            if i.name != None:
                if idvalue:
                    db.update('products', where='id="'+idvalue+'"', category=i.category,name=i.name,description=i.description,type=i.type,currency=i.currency,price=i.price,available=i.available,priority=i.priority,dateadded=datetime.datetime.now())
                else:
                    idvalue = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[11:36]
                    db.insert('products', id=idvalue, category=i.category, name=i.name, description=i.description, type=i.type,currency=i.currency, price=i.price, available=i.available, sold=0, priority=i.priority, dateadded=datetime.datetime.now())
            if i.imgfile != {}:
                if idvalue == '':
                    print('cant upload a picture to a non existing product')
                    raise web.seeother('/products/')
                print(i.imgfile.filename)
                if i.imgfile.filename == '':
                    print('hmmm... no image to upload')
                    raise web.seeother('/products/' + idvalue)
                print('YEAH, Upload image!')

                ##---------- UPLOAD IMAGE ----------

                filepath=i.imgfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
                #split and only take the filename with extension
                #soundpath=filepath.split('/')[-1]
                #if soundpath == '':
                #    return render.nope("strange, no filename found!")
                #get filetype, last three 
                imgname=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
                filetype = imgname.split('.')[-1].lower()
                if filetype == 'jpg':
                    filetype = 'jpeg'
                soundname = imgname.split('.')[0]
                #lets remove unwanted characters yes please!
                sound = ''
                for p in soundname.lower():
                    if p in allowedchar:
                        sound = sound + p
                if sound == '':
                    raise web.seeother('/upload?fail=wierdname')
                soundname = sound + '.' + filetype
                print(soundname)
                print("filename is " + imgname + " filetype is " + filetype + " soundname is " + soundname + " trying to upload file from: " + filepath)
                #if filetype != 'wav' or 'ogg' or 'flac' or 'jpeg' or 'jpg' or 'mp3':
                #    web.seeother('/upload?fail=notsupported')
                #uniqueunicorn = hashlib.md5(str(random.getrandbits(256)).encode('utf-8')).hexdigest()
                #imgname = uniqueunicorn
                #imgname = str(len(os.listdir(imgdir))).zfill(3) + '.jpeg'
                soundlink = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).hexdigest()[9:36]
                imgdir = staticdir+'upload/'+soundlink+'/'
                os.system('mkdir -p ' + imgdir)
                fout = open(imgdir + soundname,'wb') # creates the file where the uploaded file should be stored
                fout.write(i.imgfile.file.read()) # writes the uploaded file to the newly created file.
                fout.close() # closes the file, upload complete.
                
                    ##----------CHECK IF SAME NAME THEN UPDATE-------
                slink = db.query("SELECT * FROM soundlink WHERE id='"+idvalue+"' AND soundname='"+soundname+"';")
                if slink:
                    db.update('soundlink', where='"id='+idvalue+'"', soundlink=soundlink, soundname=soundname, timeadded=datetime.datetime.now())
                else:
                    db.insert('soundlink', id=idvalue, soundlink=soundlink, soundname=soundname, timeadded=datetime.datetime.now())

                if filetype == 'jpeg' or filetype == 'png':
                    ##---------- OPEN FILE & CHEKC IF JPEG --------

                    image = Image.open(imgdir +'/'+ soundname)
                    #if image.format != 'JPEG':
                    #    os.remove(imgdir +'/'+ soundname)
                    #    raise web.seeother('/products/' + idvalue)

                    ##---------- RESIZE IMAGE SAVE TO PRODUCT-----------

                    imgdir=staticdir+'img'
                    try:
                        os.makedirs(imgdir + '/web/', exist_ok=True)
                        os.makedirs(imgdir + '/thumb/', exist_ok=True)
                    except:
                        print('Folders is')
                    image.resize((900,900), Image.LANCZOS)
                    image.save(imgdir + '/web/'+soundname)
                    image.resize((300,300), Image.LANCZOS)
                    image.save(imgdir + '/thumb/'+soundname) 

            return web.seeother('/products/' + idvalue)
        else:
            return web.seeother('/login')

class shipping:
    form = web.form.Form(
    web.form.Textbox('country', web.form.notnull, description="Country:"),
    web.form.Textbox('price', web.form.regexp(r'\d+', 'number thanx!'), web.form.notnull, description="Price in cents"),
    web.form.Textbox('days', web.form.regexp(r'\d+', 'number thanx!'), web.form.notnull, description="Shipping in days"),
    web.form.Button('Add shipping country'))
    def GET(self, idvalue):
        if logged():
            addcountry = self.form()
            if idvalue:
                oldinfo = db.select('shipping', where="id='"+idvalue+"'", what='country, price, days')
                oldinfo = oldinfo[0]
                addcountry.fill(country=oldinfo.country, price=oldinfo.price, days=oldinfo.days)
            listcountries = db.query("SELECT * FROM shipping ORDER BY country DESC")
            return renderop.shipping(addcountry, listcountries)
        else:
            raise web.seeother('/login')
    def POST(self, idvalue):
        if logged():
            addcountry = self.form()
            if not addcountry.validates():
                listcountries = db.query("SELECT * FROM shipping ORDER BY country DESC")
                return renderop.shipping(addcountry, listcountries)
            else:
                i = web.input()
                if idvalue:
                    db.update('shipping', where='id="'+idvalue+'"', country=i.country, price=i.price, days=i.days)
                else:
                    db.insert('shipping', country=i.country, price=i.price, days=i.days)
                raise web.seeother('/shipping/')
        else:
            raise web.seeother('/login')

class cv:
    def GET(self):
        return render.cv()

class bitcoin:
    def GET(self):
        if logged():
            bitcoinrpc = AuthServiceProxy(rpcauth)
            wallet = bitcoinrpc.getwalletinfo()
            bitcoinrpc = None
            return renderop.bitcoin(wallet)


application = app.wsgifunc()
