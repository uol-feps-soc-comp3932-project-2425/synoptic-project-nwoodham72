from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_admin import Admin
from flask_babel import Babel
import os

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # Redirects unauthorised users to login page
login_manager.login_message_category = "info"
admin = Admin(template_mode='bootstrap4')
babel = Babel()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)  
    admin.init_app(app)
    babel.init_app(app)

    from .models import FlikUser

    @login_manager.user_loader
    def load_user(user_id):
        return FlikUser.query.get(int(user_id)) 

    from .routes import main
    from .auth import auth
    from .runbook import runbook
    from .config import config
    from . import admin_views

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(runbook)
    app.register_blueprint(config)

    __all__ = ["app", "db"]

    return app
