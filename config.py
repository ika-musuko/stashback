import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'thisissecret'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or \
    os.path.join(basedir, 'app\static\logos')

    #WTF_CSRF_ENABLED = True

    # image upload urls
    # Uploads
    UPLOADS_DEFAULT_DEST = basedir + '/project/static/img/'
    UPLOADS_DEFAULT_URL = 'http://127.0.0.1:5000/static/img/'

    UPLOADED_IMAGES_DEST = basedir + '/project/static/img/'
    UPLOADED_IMAGES_URL = 'http://127.0.0.1:5000/static/img/'
