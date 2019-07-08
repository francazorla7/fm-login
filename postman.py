# -*- coding: utf-8 -*-

import requests
import json

def post_register():

	headers = {'content-type': 'application/json'}

	params = {

		"email": "francazorla7@hotmail.es",
		"name": "Fran",
		"username": "francazorla7",
		"password": "test1234"
	}

	r = requests.post("http://localhost:9999/register", headers=headers, json=json.dumps(params))
	response = json.loads(r.content)

	return response

def post_login(email, password):

	headers = {'content-type': 'application/json'}

	params = {

		"email": email,
		"username": "",
		"name": "",
		"password": password
	}

	r = requests.post("http://localhost:9999/login", headers=headers, json=json.dumps(params))
	response = json.loads(r.content)

	return response

def post_profile(email, session_key):

	headers = {'content-type': 'application/json'}

	params = {

		"email": email,
		"session_key": session_key
	}

	r = requests.post("http://localhost:9999/profile", headers=headers, json=json.dumps(params))
	response = json.loads(r.content)

	return response

def post_logout(email, session_key):

	headers = {'content-type': 'application/json'}

	params = {

		"email": email,
		"session_key": session_key
	}

	r = requests.post("http://localhost:9999/logout", headers=headers, json=json.dumps(params))
	response = json.loads(r.content)

	return response

if __name__ == '__main__':
	
	print(post_register())
	login = post_login("francazorla7@hotmail.es", "test1234")
	print(login)
	print(post_profile(**login))
	print(post_logout(**login))