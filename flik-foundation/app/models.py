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

application_role_application_rule = db.Table(
    "application_role_application_rule",
    db.Column("application_role_id", db.Integer, db.ForeignKey("application_role.id", ondelete="CASCADE", name="fk_role_rule")),
    db.Column("application_rule_id", db.Integer, db.ForeignKey("application_rule.id", ondelete="CASCADE", name="fk_rule_role"))
)

bug_skills = db.Table(
    "bug_skills",
    db.Column("bug_id", db.Integer, db.ForeignKey("bug.id")),
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
    role = db.Column(db.String(20), nullable=False)

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
    
class ApplicationRule(db.Model):
    __tablename__ = "application_rule"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey("application_page.id", ondelete="SET NULL"), nullable=True)

    page = db.relationship("ApplicationPage", backref=db.backref("application_rules", passive_deletes=True))
    
    roles = db.relationship(
        "ApplicationRole",
        secondary=application_role_application_rule,
        backref="application_rules"
    )

    def __repr__(self):
        return f"<ApplicationRule {self.title}>"
    
class Bug(db.Model):
    __tablename__ = "bug"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False) 

    application_role = db.Column(db.Integer, db.ForeignKey("application_role.id"), nullable=True)
    application_page = db.Column(db.Integer, db.ForeignKey("application_page.id"), nullable=True)

    assignee = db.Column(db.Integer, db.ForeignKey("flik_user.id"), nullable=True)
    author = db.Column(db.Integer, db.ForeignKey("flik_user.id"), nullable=True)

    skills = db.relationship("Skill", secondary=bug_skills, backref="bugs")

    def __repr__(self):
        return f"<Bug {self.title}>"
    
class Configuration(db.Model):
    __tablename__ = "configuration"
    id = db.Column(db.Integer, primary_key=True)
    columns_to_track = db.Column(db.Text, nullable=True)
    database_retention_period = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Configuration Columns: {self.columns_to_track}, Retention: {self.database_retention_period} days>"