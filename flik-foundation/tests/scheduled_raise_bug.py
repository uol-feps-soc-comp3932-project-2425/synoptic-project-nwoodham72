
import time
import json
import random
from app import create_app
from app.routes import create_ticket_scheduled
from app.models import FlikUser

def main():
    app = create_app()
    with app.app_context():
        # Ensure there are developers to assign the ticket
        developers = FlikUser.query.filter_by(role="Developer").all()
        if not developers:
            print("❌ No developers found in DB — exiting.")
            return

        # Load tickets from file
        with open("tests/bug_tickets.json", "r") as f:
            bug_tickets = json.load(f)

        x_seconds = 2  
        limit = 20      # Max number of tickets to send
        sent = 0

        print(f"🔁 Starting scheduled ticket sender (every {x_seconds} seconds, max {limit} tickets)...")

        while sent < limit:
            bug = random.choice(bug_tickets)
            print(f"📨 [{sent + 1}/{limit}] Sending ticket: {bug['title']}")
            try:
                result = create_ticket_scheduled(bug)
                print(f"✅ Sent ticket to Azure DevOps — ID: {result['azure_id']}")
            except Exception as e:
                print(f"❌ Failed to send ticket: {e}")
            sent += 1
            if sent < limit:
                time.sleep(x_seconds)

        print("✅ All tickets sent. Script finished.")

if __name__ == "__main__":
    main()
