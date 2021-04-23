import sqlite3
import os
from flask import Flask, request, g
from flask.json import jsonify
from sqlalchemy.exc import IntegrityError
from http import HTTPStatus
from werkzeug.security import generate_password_hash
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False	# To silent a warning


@app.before_first_request
def setup_db():
	db.init_app(app)
	db.create_all()


@app.route('/create_user', methods=['POST'])
def create_user():
	data = request.json

	user = User(username=data.get('username'),
				hashed_passwd=data.get('hashed_passwd'),
				email=data.get('email'),
				phone=data.get('phone'),
				isAdmin=data.get('isAdmin'))

	try:
		db.session.add(user)
		db.session.commit()
		return {'message': 'Success'}, HTTPStatus.CREATED	
	
	except IntegrityError as e:
		if 'UNIQUE' in str(e):
			return {'message': 'Error: username already exists'}, HTTPStatus.CONFLICT
		else:
			return {'message': 'Error: missing or bad fields'}, HTTPStatus.BAD_REQUEST


@app.route('/get_user/<username>')
def get_user(username):
	user = User.query.get(username)

	if user is None:
		return {'message': 'Error: No user found'}, HTTPStatus.NOT_FOUND
	else:
		return {'message': 'Success', 'user': user.to_dict()}, HTTPStatus.OK


@app.route('/modify_user/<username>', methods=['PUT'])
def modify_user(username):
	data = request.json
	user = User.query.get(username)

	if user is None:
		return {'message': 'Error: No user found'}, HTTPStatus.NOT_FOUND

	if 'hashed_passwd' in data:
		user.hashed_passwd = data['hashed_passwd']
	if 'email' in data:
		user.email = data['email']
	if 'phone' in data:
		user.phone = data['phone']
	if 'isAdmin' in data:
		user.isAdmin = data['isAdmin']

	try:
		db.session.commit()
		return {'message': 'Success'}, HTTPStatus.OK
	except IntegrityError:
		return {'message': 'Bad fields'}, HTTPStatus.BAD_REQUEST


@app.route('/all_users', methods=['GET'])
def all_users():
	return jsonify([u.to_dict() for u in User.query.all()])


if __name__=='__main__':
	app.run()
