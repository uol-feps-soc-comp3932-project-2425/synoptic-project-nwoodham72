from . import db, bcrypt
from flask_login import UserMixin

""" models.py: Define database and relationships """

""" Association tables for many-to-many relationships """
flik_user_roles = db.Table(
    "flik_user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("flik_user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("flik_role.id")),
)

flik_user_skill = db.Table(
    "flik_user_skill",
    db.Column("user_id", db.Integer, db.ForeignKey("flik_user.id")),
    db.Column("skill_id", db.Integer, db.ForeignKey("skill.id")),
)


""" Models """
class FlikRole(db.Model):
    __tablename__ = "flik_role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<FlikRole {self.name}>"

class FlikUser(db.Model, UserMixin):
    __tablename__ = "flik_user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'Developer' or 'Client'

    roles = db.relationship("FlikRole", secondary="flik_user_roles", backref="users")

    skills = db.relationship(
        "Skill", secondary=flik_user_skill, back_populates="flik_users"
    )

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def __repr__(self):
        return f"<FlikUser {self.email}>"

class Skill(db.Model):
    __tablename__ = "skill"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    flik_users = db.relationship(
        "FlikUser", secondary=flik_user_skill, back_populates="skills"
    )

    def __repr__(self):
        return f"<Skill {self.name}>"

class ApplicationRole(db.Model):
    __tablename__ = "application_role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<ApplicationRole {self.name}>"
    
class ApplicationPage(db.Model):
    __tablename__ = "application_page"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<ApplicationPage {self.name}>"