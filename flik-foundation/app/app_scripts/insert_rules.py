import random
from app import db, create_app
from app.models import ApplicationRule, ApplicationPage

app = create_app()

# Predefined realistic rule components
titles = [
    "Username must be unique",
    "Password requires special characters",
    "Login is restricted to verified users",
    "Display loading animation on submit",
    "Dropdown values must be predefined",
    "Admin users can override limits",
    "Hide inactive features from clients",
    "Email field must be in valid format",
    "Restrict page access to permitted roles",
    "Duplicate entries should trigger warnings",
]

descriptions = [
    "Ensure that the username entered by the user does not already exist in the system before proceeding with registration.",
    "Passwords must contain at least one uppercase letter, one lowercase letter, one number, and one special character.",
    "Only users who have verified their email addresses through the provided verification link should be allowed to log in.",
    "When a user submits a form, a loading spinner must appear until a response is received from the server.",
    "The dropdown for selecting user type should be populated from the config file and not be manually editable.",
    "Admins should be able to bypass character limits when editing system-generated content.",
    "If a feature has been marked as deprecated in the backend, it should not appear in the UI for client users.",
    "The email field must pass a regex validation to ensure a proper email format is entered before form submission.",
    "Only users with 'Manager' or 'Admin' roles should be able to access this page. All others must be redirected.",
    "If a user attempts to create an entry that already exists based on the title and page combination, warn them appropriately.",
]

def generate_rule(i):
    title = random.choice(titles)
    detail = random.choice(descriptions)
    return f"{title} (Test {i})", f"[Rule {i}] {detail}"

def insert_rules():
    with app.app_context():
        # Get or create a default page
        default_page = ApplicationPage.query.first()
        if not default_page:
            default_page = ApplicationPage(name="Default Page")
            db.session.add(default_page)
            db.session.commit()

        # Insert 100 varied rules
        for i in range(1, 101):
            title, description = generate_rule(i)
            rule = ApplicationRule(
                title=title,
                description=description,
                page_id=default_page.id
            )
            db.session.add(rule)

        db.session.commit()
        print("✅ Inserted 100 diverse rules into the ApplicationRule table.")

if __name__ == "__main__":
    insert_rules()
