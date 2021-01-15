# -*- coding: utf-8 -*-

import bcrypt
import hashlib
from quart import Blueprint, render_template, request
from cmyui import log, Ansi

__all__ = ()

frontend = Blueprint('frontend', __name__)

@frontend.route('/home')
@frontend.route('/')
async def home():
    return await render_template('home.html')

@frontend.route('/login') # GET
async def login():
    return await render_template('login.html')

@frontend.route('/login', methods=['POST']) # POST
async def login_post():
    # get form data (username, password)
    form = await request.form
    username = form.get('username')
    pw_md5 = hashlib.md5(form.get('username').encode()).hexdigest().encode()

    # check if account exists
    user_info = await glob.db.fetch(
        'SELECT id, name, priv, pw_bcrypt, silence_end '
        'FROM users WHERE safe_name = %s',
        [username.replace(' ', '_').lower()]
    )

    # the second part of this if statement exists because if we try to login with Aika
    # and compare our password inputed against the database it will fail because the 
    # hash saved in the database is invalid.
    if not user_info or user_info['id'] == 1:
        return b'login failed. account does not exist.'

    bcrypt_cache = glob.cache['bcrypt']
    pw_bcrypt = user_info['pw_bcrypt'].encode()
    user_info['pw_bcrypt'] = pw_bcrypt

    # check credentials against db
    # intentionally slow, will cache to speed up
    # TODO: sessions and redirect
    if pw_bcrypt in bcrypt_cache:
        if pw_md5 != bcrypt_cache[pw_bcrypt]: # ~0.1ms
            return 'login failed. password is incorrect.'
    else: # ~200ms
        if not bcrypt.checkpw(pw_md5, pw_bcrypt):
            return 'login failed. password is incorrect.'
            
        # login success. cache password for next login
        bcrypt_cache[pw_bcrypt] = pw_md5

    # login successful
    return 'login successful.'

@frontend.route("/register")
async def register():
    return await render_template("register.html")