# admin.py
from flask_admin.contrib.sqla import ModelView
from .models import User
from . import db, admin 

# Register models with Flask-Admin
admin.add_view(ModelView(User, db.session))
