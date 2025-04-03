from . import db, bcrypt
from flask_login import UserMixin

""" Association tables for many-to-many relationships """
flik_user_skill = db.Table('flik_user_skill',
    db.Column('user_id', db.Integer, db.ForeignKey('flik_user.id')),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'))
)



""" Models """
class FlikUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'Developer' or 'Client'

    skills = db.relationship('Skill', secondary=flik_user_skill, back_populates='flik_users')

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    flik_users = db.relationship('FlikUser', secondary=flik_user_skill, back_populates='skills')


