from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class RaiseBugForm(FlaskForm):
    title = StringField('Bug Title', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Bug Description', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Report Bug')
