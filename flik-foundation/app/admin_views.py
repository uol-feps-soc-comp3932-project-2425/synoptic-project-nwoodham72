# admin.py
from flask_admin.contrib.sqla import ModelView
from .models import FlikUser, FlikRole
from . import db, admin 

# Register models with Flask-Admin
admin.add_view(ModelView(FlikUser, db.session))
admin.add_view(ModelView(FlikRole, db.session))

