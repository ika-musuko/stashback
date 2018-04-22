from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint
from rauth import OAuth2Service
import os
import stripe
import plaid

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

blueprint = make_google_blueprint(
	client_id="887094665146-dr3gtcjss9dquehr579iorba4qe030fp.apps.googleusercontent.com",
	client_secret="aGzRtH3xMRzACLnXCjrLC1gr",
	scope=['profile', 'email'],
	offline=True
	)

app.register_blueprint(blueprint, url_prefix='/login')

stripe_keys = {
	'secret_key': os.environ.get('STRIPE_SECRET_KEY') or 'sk_test_SPxRtNhAGFTuIoS4adJbvtNS',
	'publishable_key': os.environ.get('STRIPE_PUBLISHABLE_KEY') or 'pk_test_pIQmqoDGHlxFVEAMvslLHr2U',
	'oauth_client_id': os.environ.get('STRIPE_OAUTH_CLIENT_ID') or 'ca_CfkdcqiWKWCORwQXaoxOjuvzkDO30YeY',
}

params = {'response_type': 'code', 'scope': 'admin'}

stripe_connect_service = OAuth2Service(
        name='stripe',
        client_id='ca_CfkdcqiWKWCORwQXaoxOjuvzkDO30YeY',
        client_secret='sk_test_SPxRtNhAGFTuIoS4adJbvtNS',
        authorize_url='https://connect.stripe.com/oauth/authorize',
        access_token_url='https://connect.stripe.com/oauth/token',
        base_url='https://api.stripe.com/',
    )

plaid_keys = {
	'client_key':os.getenv('PLAID_CLIENT_ID') or '5ad3deefbdc6a40eb40cb837',
	'secret_key':os.getenv('PLAID_SECRET') or '2477ce93d86dda1ea323f1c8378fe7',
	'public_key':os.getenv('PLAID_PUBLIC_KEY') or '2b8b50cccbb000a6980afd5e46b2cf',
	'plaid_env':os.getenv('PLAID_ENV', 'sandbox'),
}

client = plaid.Client(client_id = plaid_keys['client_key'], secret=plaid_keys['secret_key'],
                  public_key=plaid_keys['public_key'], environment=plaid_keys['plaid_env'])

from app import routes, models, errors