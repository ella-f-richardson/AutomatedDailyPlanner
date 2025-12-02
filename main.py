import os                                       # to access environment variables
from datetime import datetime, timezone         # to handle date and time
from dateutil import parser                     # to parse date strings
import requests                                 # to make HTTP requests
from dotenv import load_dotenv                  # to load environment variables from .env file

# Load environment variables from .env file
load_dotenv()

BASE = os.getenv("CANVAS_BASE_URL")             # Base URL for Canvas API
TOKEN = os.getenv("CANVAS_TOKEN")               # API token for authentication

# Ensure that the necessary environment variables are set
if not BASE or not TOKEN:
    raise Exception("Missing CANVAS_BASE_URL or CANVAS_TOKEN in .env")

HEADERS = {"Authorization" : f"Bearer {TOKEN}"} # Headers for API requests

## ----- Helper Functions ----- ##

# Return days until due date -> float
def days_until_due(due_at):
    if due_at is None:
        return None
    
    due = parser.isoparse(due_at).astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    return(due-now).total_seconds()/86400 # convert seconds to days

# Return score of urgency based on dates (1-100)
# Lower score -> lower priority and vice-versa
def urgency_score(days):
    if days <= 0:   return 100
    if days <= 1:   return 90
    if days <= 3:   return 70
    if days <= 5:   return 50
    if days is None:return 5
    return 20

## ----- API Calls ----- #

# Get courses from page - restrict later to only courses I want
def get_courses():
    url = f"{BASE}/courses?enrollment_state=active"
    return requests.get(url, headers=HEADERS).json()

# Get assignments from each course - figure out how to cross of 
# assignments once completed for later
def get_assigments(course_id):
    url = f"{BASE}/courses/{course_id}/assignments"
    return requests.get(url, headers=HEADERS).json()

## ----- Main Logic ----- ##

# Get and categorize all assigments
def fetch_all_assigments():
    all_assigments = []
    courses = get_courses()

    for course in courses:
        c_id = course.get("id")
        c_name = course.get("name")

        try: assignments = get_assigments(c_id)
        except: continue

        for a in assignments:
            due = a.get("due_at")
            d = days_until_due(due)
            all_assigments.append({
                "course":            c_name,
                "name":             a.get("name"),
                "due_at":           due, 
                "days_until_due":   d, 
                "urgency":          urgency_score(d)
            })
    
    return all_assigments

# Main Function
def main():
    assignments = fetch_all_assigments()
    assignments.sort(key=lambda x: x["urgency"], reverse=True)
    print("\n========== ASSIGMENTS BY URGENCY ==========\n")

    for a in assignments:
        print(f"{a['course']} - {a['name']}")
        if a["days_until"] is None:
            print("     Due: No due date")
        else:
            print(f"    Due in: {a['days_until']:.1f} days")
        print(f"    Urgency: {a['urgency']}\n")


if __name__ == "__main__":
    main()