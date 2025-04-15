import os
import sys

# Add flik-foundation/app to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from app import create_app, db  # Make sure your app/__init__.py exposes these
from sqlalchemy import inspect

app = create_app()  # This depends on how you bootstrap Flask — update if needed

def print_foreign_keys():
    inspector = inspect(db.engine)
    fks = inspector.get_foreign_keys("application_rule")

    for fk in fks:
        print(f"Constraint Name: {fk['name']}")
        print(f"Columns: {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
        print()

# ✅ Push the application context so db.engine can be accessed
with app.app_context():
    print_foreign_keys()
