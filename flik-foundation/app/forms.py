from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RaiseBugForm(FlaskForm):
    title = StringField("Bug Title", validators=[DataRequired(), Length(max=150)], render_kw={"id": "title"})
    role = SelectField(
        "User Role",
        choices=[
            ("", "Select a user role..."),
            ("developer", "Developer"),
            ("client", "Client"),
        ],
        validators=[DataRequired(message="Please select a user role")],
        render_kw={"id": "role"},
    )
    page = SelectField(
        "Page",
        choices=[
            ("", "What page are you on..."),
            ("login", "Login"),
            ("modules", "Modules"),
            ("registration", "Student Registration"),
        ],
        validators=[DataRequired(message="Please select a page")],
        render_kw={"id": "page"},
    )
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=10)], render_kw={"id": "description"})
    expected = TextAreaField(
        "Expected Behaviour", validators=[DataRequired(), Length(min=10)], render_kw={"id": "expected"}
    )
    submit = SubmitField("Report Bug")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    role = SelectField(
        "Role",
        choices=[
            ("Manager", "Manager"),
            ("Developer", "Developer"),
            ("Client", "Client"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Register")
