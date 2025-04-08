from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from .models import ApplicationRole, ApplicationPage, ApplicationRule, FlikRole

""" forms.py: Define flask forms and field criteria """
class RaiseBugForm(FlaskForm):
    title = StringField("Bug Title", validators=[DataRequired(), Length(max=150)], render_kw={"id": "title"})
    role = QuerySelectField(
        "Role",
        query_factory=lambda: ApplicationRole.query.order_by(ApplicationRole.name).all(),
        get_label="name",
        allow_blank=True,
    )
    page = QuerySelectField(
        "Page",
        query_factory=lambda: ApplicationPage.query.order_by(ApplicationPage.name).all(),
        get_label="name",
        allow_blank=True,
    )
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=10, max=2048)], render_kw={"id": "description"})
    expected = TextAreaField(
        "Expected Behaviour", validators=[DataRequired(), Length(min=10)], render_kw={"id": "expected"}
    )
    submit = SubmitField("Report Bug")

class ApplicationRuleForm(FlaskForm):
    title = StringField("Rule Title", validators=[DataRequired(), Length(max=150)], render_kw={"id": "title"})
    description = TextAreaField("Rule Description", validators=[DataRequired(), Length(min=10, max=1024)], render_kw={"id": "description"})
    page = QuerySelectField(
        "Page",
        query_factory=lambda: ApplicationPage.query.order_by(ApplicationPage.name).all(),
        get_label="name",
        allow_blank=False,
    )

    roles = QuerySelectMultipleField(
        "Permitted Roles",
        query_factory=lambda: ApplicationRole.query.order_by(ApplicationRole.name).all(),
        get_label="name"
    )
     
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
    role = QuerySelectField(
        "Flik Role",
        query_factory=lambda: FlikRole.query.order_by(FlikRole.name).all(),
        get_label="name",
        allow_blank=True,
    )
    submit = SubmitField("Register")
