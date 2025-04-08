# admin.py
from flask_admin.contrib.sqla import ModelView
from .models import FlikUser, FlikRole, ApplicationRole, ApplicationRule, Skill, ApplicationPage
from . import db, admin 

# Register models with Flask-Admin
admin.add_view(ModelView(FlikUser, db.session))
admin.add_view(ModelView(FlikRole, db.session))
admin.add_view(ModelView(ApplicationRole, db.session))
admin.add_view(ModelView(ApplicationPage, db.session))
admin.add_view(ModelView(ApplicationRule, db.session))
admin.add_view(ModelView(Skill, db.session))

