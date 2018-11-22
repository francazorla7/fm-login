#! /usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, Response
from flask import request, make_response, current_app
from flask_cors import CORS
import json
import pymongo
from pymongo import MongoClient
import random
from werkzeug.security import generate_password_hash, check_password_hash

class ConfigFMLogin(object):

	def __init__(self, config_file, using=False):

		super(ConfigFMLogin, self).__init__()

		self.session_key_active = True
		self.session_key_length = 16

		self.db_name = "test"
		self.collection_users_name = "fm-users"
		self.collection_sessions_name = "fm-sessions"
		self.user_key = "email"
		self.user_template = ["username", "name", "email"]

		if using:
			with open(config_file, "r") as f:

				f_json = json.load(f)
				print("Using {} as config file: \n{}".format(config_file, f_json))

	def generate_blank_user(self):

		user = {}
		for k in self.user_template:
			user[k] = ""
		return user

	def generate_custom_user(self, js):

		user = {}
		for k in self.user_template:
			user[k] = js[k]
		return user


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Create Flask's app
app = Flask(__name__)

# Use CORS
CORS(app)

# Load configuration
configuration = ConfigFMLogin("config.conf")

# Starts MongoDB
client = MongoClient()
db = client[configuration.db_name]

# Create a new session
def generate_session(user_key):

	session_key = "".join(random.choice(ALPHABET) for i in range(configuration.session_key_length))

	row = {

		configuration.user_key: user_key,
		"session_key": session_key
	}

	db[config_file.collection_sessions_name].insert_one(row)

	del row["_id"]
	return row

# Chek if exists a session
def check_session_key(session_key, user_key):

	exists = db["sessions"].find_one({"session_key": session_key, configuration.user_key: user_key})
	if exists is None:
		return False

	return True

# Register an user
@app.route("/register", methods=["POST"])
def register():

	js = request.get_json()
	user_template = configuration.generate_custom_user(js)

	user_exists = db[configuration.collection_users_name].find_one({configuration.user_key: user_template[configuration.user_key]})

	if not user_exists is None:

		r = {

			"error": "true",
			"text": "El usuario ya está registrado."
		}
		resp = Response(json.dumps(r))
		resp.headers['Content-Type'] = 'application/json'
		resp.headers['Access-Control-Allow-Origin'] = '*'

		return resp

	password = js["password"]

	_salt = "".join(random.choice(ALPHABET) for i in range(16))
	_hash = generate_password_hash(_salt + password)

	user_template["_hash"] = _hash
	user_template["_salt"] =_salt

	db[configuration.collection_users_name].insert_one(user_template)

	r = {

		"error": "false",
		"text": "El usuario se ha registrado correctamente."
	}

	print(r)

	resp = Response(json.dumps(r))
	resp.headers['Content-Type'] = 'application/json'
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

@app.route("/login", methods=["POST"])
def login():

	js = request.get_json()
	user_template = configuration.generate_custom_user(js)

	user_exists = db[configuration.collection_users_name].find_one({configuration.user_key: user_template[configuration.user_key]})

	if user_exists is None:

		r = {

			"error": "true",
			"text": "El usuario no está registrado."
		}
		resp = Response(json.dumps(r))
		resp.headers['Content-Type'] = 'application/json'
		resp.headers['Access-Control-Allow-Origin'] = '*'

		return resp

	password = js["password"]
	_salt = user_exists["_salt"]

	if not check_password_hash(user_exists["_hash"], _salt + password):

		r = {

			"error": "true",
			"text": "La contraseña es incorrecta."
		}
		resp = Response(json.dumps(r))
		resp.headers['Content-Type'] = 'application/json'
		resp.headers['Access-Control-Allow-Origin'] = '*'

		return resp

	if configuration.session_key_active:
		r = generate_session(user_exists["username"])

	else:
		r = {configuration.user_key: user_exists[configuration.user_key]}
	
	print(r)

	resp = Response(json.dumps(r))
	resp.headers['Content-Type'] = 'application/json'
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

@app.route("/logout", methods=["POST"])
def logout():

	js = request.get_json()

	user_exists = db[configuration.collection_users_name].find_one({configuration.user_key: js[configuration.user_key]})

	if user_exists is None:

		r = {

			"error": "true",
			"text": "El usuario no está registrado."
		}

		resp = Response(json.dumps(r))
		resp.headers['Content-Type'] = 'application/json'
		resp.headers['Access-Control-Allow-Origin'] = '*'

		return resp

	session_key = js["session_key"]

	if not check_session_key(session_key, user_template[configuration.user_key]):

		r = {

			"error": "true",
			"text": "La clave de sesión no es válida."
		}

		resp = Response(json.dumps(r))
		resp.headers['Content-Type'] = 'application/json'
		resp.headers['Access-Control-Allow-Origin'] = '*'

		return resp

	db[configuration.collection_sessions_name].delete_one({configuration.user_key: js[configuration.user_key], "session_key": session_key})

	r = {

		"error": "false",
		"text": "Se ha desconectado correctamente."
	}

	print(r)

	resp = Response(json.dumps(r))
	resp.headers['Content-Type'] = 'application/json'
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

app.run("localhost", port=9999)