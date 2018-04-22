from app import app
from app import db
from app import login
from app import blueprint
from app import stripe_keys, stripe_connect_service, params
from app import plaid_keys, client
from app.models import User, Charity, Donator
from app.forms import CharityInputForm
from flask import render_template, redirect, url_for, redirect, flash, request, session
from flask_login import current_user, login_user, logout_user, login_required
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.google import google
from werkzeug.utils import secure_filename
import os
import stripe
import plaid
import json

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
	resp = google.get("/oauth2/v2/userinfo")
	username = resp.json()['name']
	email = resp.json()['email']
	if resp.ok:
		user = User.query.filter_by(email=email).first()
		if user is None:
			user = User(username=username,email=email)
			db.session.add(user)
			db.session.commit()
			login_user(user)
			return redirect(url_for('type_selector'))
		login_user(user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/options')
@login_required
def options():
	'''
	Users (donators) can change how to calculate their stash
	'''
	return render_template('options.html', title='Change Option')

@app.route('/change_charity')
@login_required
def change_charity():
	'''
	Users can chanege the charity they are going to donate
	The list of charities is shown here
	'''
	charities = Charity.query.all()
	return render_template('change_charity.html', title='Change Charity', charities=charities)

@app.route('/charity_description', methods=['GET'])
@login_required
def charity_description():
	'''
	Users apply to the charity here
	Stripe Button here
	'''
	return render_template('charity_description.html', title='Charity Description')


@app.route('/apply_charity', methods=['POST'])
def apply_charity():
	'''
	Create the subscription for the charity
	'''
	customer = stripe.Customer.create(
		email=current_user.email,
		source=request.form['stripeToken'],
		)

	donater = Donator(customer_id=customer.id)#
	db.session.add(donater)
	db.session.commit()

	#Create the subscription for the charity
	subscription = stripe.Subscription.create(
		customer=customer.id,
		plan='monthly-donation',
		stripe_account=''#connect_user_id here
		)

	flash('You applied to the charity successfully.')
	return redirect(url_for('index'))

@app.route('/refresh_stash')
def refresh_stash():
	'''
	Link to Plaid Form
	Get transaction and calculate the stash when they input the Plaid Link.
	'''
	return render_template('refresh_stash.html', title='Refresh Stash', 
							plaid_public_key=plaid_keys['public_key'], plaid_environment=plaid_keys['plaid_env'])

@app.route("/get_access_token", methods=['POST'])
def get_access_token():
	access_token = None
	public_token = request.form['public_token']
	exchange_response = client.Item.public_token.exchange(public_token)
	print('public token: ' + public_token)
	print('access token: ' + exchange_response['access_token'])
	print('item ID: ' + exchange_response['item_id'])
	access_token = exchange_response['access_token']
	#Redirect here
	#Retrieve transactions here

	return jsonify(exchange_response)
	return redirect(url_for('index'))
	#return render_template('get_access_token.html')

@app.route('/calculate_stash', methods=['GET', 'POST'])
def calculate_stash():
	'''
	Calculate the total stash since the day the user refresh the stash
	'''
	return redirect(url_for('index'))#Pass the stash here

@app.route('/type_selector')
@login_required
def type_selector():
	'''
	Users choose whther they are donator or charity when they log in first time
	When the user register as a charity, is_donator is swicthed to False
	'''
	return render_template('type_selector.html', title='Select Type')

@app.route('/select_donator')
def select_donator():
	'''
	When the user select donotor, the user is registered as donotor
	Save the user info into Donators datatable and Redirect to Home page
	'''
	flash('You registered as donator successfully. Please choose a charity.')
	return redirect(url_for('change_charity.html'))

@app.route('/select_charity')
def select_charity():
	'''
	When the user select charity, the user is registered as charity
	It redirects to  Stripe Connect
	'''
	current_user.is_donator = False
	db.session.commit()
	return redirect("https://connect.stripe.com/oauth/authorize?response_type=code&client_id=ca_CfkdcqiWKWCORwQXaoxOjuvzkDO30YeY&scope=read_write")

@app.route('/input_charity_info', methods=['GET', 'POST'])
@login_required
def input_charity_info():
	'''
	Redirect to this page after Stripe Connect
	'''
	code = request.args.get('code')
	url = stripe_connect_service.get_authorize_url(**params)
	print(url)

	data = {
		'grant_type': 'authorization_code',
		'code': code
	}

	resp = stripe_connect_service.get_raw_access_token(method='POST', data=data)
	connect_account_info = json.loads(resp.text)
	print(connect_account_info)

	connect_public_key = connect_account_info['stripe_publishable_key']
	connect_access_token = connect_account_info['access_token']
	connect_user_id = connect_account_info['stripe_user_id']
	connect_refresh_token = connect_account_info['refresh_token']

	print(connect_public_key)
	print(connect_access_token)
	print(connect_user_id)
	print(connect_refresh_token)
	form = CharityInputForm()
	if form.validate_on_submit():
		'''
		Save the charity's info into Charity data table
		'''
		filename = secure_filename(form.charity_logo.data.filename)
		form.charity_logo.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))#Maybe it's better to trim the logo using js


		charity = Charity(charity_name=form.charity_name.data, charity_logo=filename,
							description=form.description.data, link=form.link.data,
							connect_public_key=connect_account_info['stripe_publishable_key'], 
							connect_access_token=connect_account_info['access_token'],
							connect_user_id=connect_account_info['stripe_user_id'], 
							connect_refresh_token=connect_account_info['refresh_token'])
		db.session.add(charity)
		db.session.commit()

		flash('Your Charity is registered successfully!')
		return redirect(url_for('index'))
	return render_template('input_charity_info.html', title='Input Charity Info', form=form)

###To do
'''
Oauth Connected account(Done?)
Create db for charities(Done?)
Show the list of charities on change_charity.html

Create db for donators(Done?)
Donator choose one charity and connect the user to the charity (Stripe Subscription) (Just write code)

Create Plaid Link and calcurate the stash based on the retrieved transactions (Just write code)
Create other pages
'''

###Problems
'''
Cannot save the connect account keys in db
How to pass the charity's id to @app.route('/apply_charity')
'''