from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	username = db.Column(db.String(15), primary_key=True)
	hashed_passwd = db.Column(db.Text, nullable=False)
	email = db.Column(db.String(320))
	phone = db.Column(db.String(15))
	isAdmin = db.Column(db.Boolean, nullable=False)

	def to_dict(self):
		vals = vars(self)
		return {attr: vals[attr] for attr in vals if 'instance_state' not in attr}
