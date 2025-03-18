from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RaiseBugForm(FlaskForm):
    title = StringField('Bug Title', validators=[DataRequired(), Length(max=150)])
    given = TextAreaField('Given', validators=[DataRequired(), Length(min=10)])
    when = TextAreaField('When', validators=[DataRequired(), Length(min=10)])
    then = TextAreaField('Then', validators=[DataRequired(), Length(min=10)])
    expected = TextAreaField('Expected Behaviour', validators=[DataRequired(), Length(min=10)])
    actual = TextAreaField('Actual Behaviour', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Report Bug')

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    role = SelectField("Role", choices=[("Manager", "Manager"), ("Developer", "Developer"), ("Client", "Client")], validators=[DataRequired()])
    submit = SubmitField("Register")