
import sys
import os
import time
import json
import random
import statistics
from app import create_app
from app.utils import create_ticket_scheduled
from app.models import FlikUser

# Fix module resolution when running from tests/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def main():
    app = create_app()
    with app.app_context():
        developers = FlikUser.query.filter_by(role="Developer").all()
        if not developers:
            print("❌ No developers found in DB — exiting.")
            return

        with open("tests/bug_tickets.json", "r") as f:
            bug_tickets = json.load(f)

        x_seconds = 2
        limit = 20
        sent = 0
        times = []

        print(f"🔁 Starting timed ticket sender (every {x_seconds} seconds, max {limit} tickets)...")

        while sent < limit:
            bug = random.choice(bug_tickets)
            print(f"📨 [{sent + 1}/{limit}] Sending ticket: {bug['title']}")
            try:
                start_time = time.time()
                result = create_ticket_scheduled(bug)
                end_time = time.time()
                duration = end_time - start_time
                times.append(duration)
                print(f"✅ Sent ticket in {duration:.2f}s — Azure ID: {result['azure_id']}")
            except Exception as e:
                print(f"❌ Failed to send ticket: {e}")
                times.append(0)
            sent += 1
            if sent < limit:
                time.sleep(x_seconds)

        if times:
            avg = sum(times) / len(times)
            stdev = statistics.stdev(times) if len(times) > 1 else 0
            print(f"📊 Average Time: {avg:.2f}s | Std Deviation: {stdev:.2f}s")

        print("✅ All tickets sent. Script finished.")

if __name__ == "__main__":
    main()
