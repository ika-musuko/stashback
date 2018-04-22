from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired , ValidationError
from app.models import User #Donator, Charity

class CharityInputForm(FlaskForm):
	'''
	Logo, name, description, link
	'''
	charity_name = StringField('Charity Name', validators=[DataRequired()])
	charity_logo = FileField('Charity Logo', validators=[DataRequired()])
	description = TextAreaField('Description', validators=[DataRequired()])
	link = StringField('Link', validators=[DataRequired()])
	submit = SubmitField('Submit')

