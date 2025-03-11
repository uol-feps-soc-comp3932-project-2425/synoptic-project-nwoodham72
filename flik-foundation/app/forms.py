from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class RaiseBugForm(FlaskForm):
    title = StringField('Bug Title', validators=[DataRequired(), Length(max=150)])
    given = TextAreaField('Given', validators=[DataRequired(), Length(min=10)])
    when = TextAreaField('When', validators=[DataRequired(), Length(min=10)])
    then = TextAreaField('Then', validators=[DataRequired(), Length(min=10)])
    expected = TextAreaField('Expected Behaviour', validators=[DataRequired(), Length(min=10)])
    actual = TextAreaField('Actual Behaviour', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Report Bug')
