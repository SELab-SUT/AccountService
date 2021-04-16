import sqlite3
import os
from flask import Flask, request, g
from werkzeug.security import generate_password_hash

app = Flask(__name__)
DATABASE = 'db.sqlite3'


def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE)
	return db


@app.before_first_request
def setup_db():
	if not os.path.exists('db.sqlite'):
		open('db.sqlite', 'a').close()

	cur = get_db().cursor()

	cur.execute('''CREATE TABLE IF NOT EXISTS users 
									(username VARCHAR(15) NOT NULL PRIMARY KEY,
									hashed_passwd TEXT NOT NULL,
									email VARCHAR(320),
									phone VARCHAR(15),
									isAdmin BOOLEAN NOT NULL)''')
	passwd_hashed = generate_password_hash('1234', method='sha256')
	cur.execute("""INSERT OR IGNORE INTO users VALUES 
						('superadmin', ?, NULL, NULL, TRUE)""", 
						(passwd_hashed,))
	get_db().commit()


@app.route('/create_user', methods=['POST'])
def create_user():
	data = request.json
	data['email'] = data['email'] if 'email' in data else None
	data['phone'] = data['phone'] if 'phone' in data else None
	cur = get_db().cursor()

	try:
		cur.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)', (data['username'],
															data['hashed_passwd'],
															data['email'],
															data['phone'],
															data['isAdmin']))
		get_db().commit()
		return {'message': 'Success'}
	
	except sqlite3.IntegrityError:
		return {'message': 'Error: UNIQUE constrained failed'}


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__=='__main__':
	app.run()
