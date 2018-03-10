from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, DateTimeField
from wtforms.validators import DataRequired


class SampleForm(FlaskForm):
    txt_field = StringField('txt_field', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class TaskForm(FlaskForm):
    title = StringField("title", validators=[DataRequired()])
    start_time = DateTimeField("start", format='%Y-%m-%d %H:%M:%S')
    end_time = DateTimeField("end", format='%Y-%m-%d %H:%M:%S')
    release = DecimalField("release", places=4)

    submit = SubmitField("Insert New")