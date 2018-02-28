from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SampleForm(FlaskForm):
    txt_field = StringField('txt_field', validators=[DataRequired()])
    submit = SubmitField('Sign In')