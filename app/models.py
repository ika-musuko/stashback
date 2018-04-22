from app import app
from app import db
from app import login
from app import blueprint
from flask_login import UserMixin, current_user
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend

class User(UserMixin, db.Model):
	'''
	User account datatable
	'''
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True)
	email = db.Column(db.String(120), index=True, unique=True)#email should be unique
	is_donator = db.Column(db.Boolean, default=True)#type_selector:If the user register as a charity, it switched to False
	charity = db.relationship('Charity', backref='user')
	donator = db.relationship('Donator', backref='user')

class OAuth(OAuthConsumerMixin, db.Model):
	'''
	Define the datatable with a token and its provider
	These columns are hidden but we can see on migration file
	'''
	user_id = db.Column(db.Integer, db.ForeignKey(User.id))
	user = db.relationship(User)

blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user, user_required=False)

@login.user_loader
def load_user(user_id):
	'''
	Keep track of the logged in user
	'''
	return User.query.get(int(user_id))

class Charity(db.Model):
	'''
	Data tables for charities
	'''
	id = db.Column(db.Integer, primary_key=True)
	charity_name = db.Column(db.String(64), index=True)
	charity_logo = db.Column(db.String(200), index=True)
	description = db.Column(db.Text(400))#just decided the length randomly
	link = db.Column(db.String(200), index=True)
	connect_public_key = db.Column(db.String(200), index=True)#not sure if it's unique for the prototype
	connect_access_token = db.Column(db.String(200), index=True, unique=True)
	connect_user_id = db.Column(db.String(200), index=True, unique=True)
	connect_refresh_token = db.Column(db.String(200), index=True, unique=True)
	is_form_done = db.Column(db.Boolean, default=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))#Connected to the user's id


class Donator(db.Model):
	'''
	Data tables for donators
	'''
	id = db.Column(db.Integer, primary_key=True)
	customer_id = db.Column(db.String(64))
	current_charity_id = db.Column(db.Integer)#Current charity id that the donator is going to donete
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))#Connected to the user's id
	#option: How to calculate the stash