from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint
from flask_uploads import UploadSet, IMAGES, configure_uploads
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

# upload manager for pictures and files
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

blueprint = make_google_blueprint(
	client_id=os.environ.get('GOOGLE_CLIENT_ID') or '',
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET') or '',
	scope=['profile', 'email'],
	offline=True
	)

app.register_blueprint(blueprint, url_prefix='/login')

stripe_keys = {
	'secret_key': os.environ.get('STRIPE_SECRET_KEY') or '',
	'publishable_key': os.environ.get('STRIPE_PUBLISHABLE_KEY') or '',
	'oauth_client_id': os.environ.get('STRIPE_OAUTH_CLIENT_ID') or '',
}

params = {'response_type': 'code', 'scope': 'admin'}

stripe_connect_service = OAuth2Service(
        name='stripe',
        client_id=stripe_keys['oauth_client_id'],
        client_secret=stripe_keys['secret_key'],
        authorize_url='https://connect.stripe.com/oauth/authorize',
        access_token_url='https://connect.stripe.com/oauth/token',
        base_url='https://api.stripe.com/',
    )

plaid_keys = {
	'client_key':os.getenv('PLAID_CLIENT_ID') or '',
	'secret_key':os.getenv('PLAID_SECRET') or '',
	'public_key':os.getenv('PLAID_PUBLIC_KEY') or '',
	'plaid_env':os.getenv('PLAID_ENV', 'sandbox'),
}

client = plaid.Client(client_id = plaid_keys['client_key'], secret=plaid_keys['secret_key'],
                  public_key=plaid_keys['public_key'], environment=plaid_keys['plaid_env'])



from app import routes, models, errors

