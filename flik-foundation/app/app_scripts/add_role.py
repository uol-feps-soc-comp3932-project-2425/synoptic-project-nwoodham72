from app import db, create_app
from app.models import FlikRole

app = create_app()
app.app_context().push()

new_role = FlikRole(name='Deleted')

db.session.add(new_role)
db.session.commit()
print('Added new role: Deleted')