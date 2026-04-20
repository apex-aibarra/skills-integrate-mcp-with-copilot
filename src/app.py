"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Import database components
from database import get_db, Activity, Registration, create_tables, engine
from sqlalchemy import func

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

def seed_initial_data(db: Session):
    """Seed initial activities data if database is empty."""
    if db.query(Activity).count() == 0:
        initial_activities = [
            {
                "name": "Chess Club",
                "description": "Learn strategies and compete in chess tournaments",
                "category": "Academic",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "contact_email": "chess@mergington.edu"
            },
            {
                "name": "Programming Class",
                "description": "Learn programming fundamentals and build software projects",
                "category": "Academic",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "contact_email": "programming@mergington.edu"
            },
            {
                "name": "Gym Class",
                "description": "Physical education and sports activities",
                "category": "Sports",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_participants": 30,
                "contact_email": "gym@mergington.edu"
            },
            {
                "name": "Soccer Team",
                "description": "Join the school soccer team and compete in matches",
                "category": "Sports",
                "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                "max_participants": 22,
                "contact_email": "soccer@mergington.edu"
            },
            {
                "name": "Basketball Team",
                "description": "Practice and play basketball with the school team",
                "category": "Sports",
                "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 15,
                "contact_email": "basketball@mergington.edu"
            },
            {
                "name": "Art Club",
                "description": "Explore your creativity through painting and drawing",
                "category": "Arts",
                "schedule": "Thursdays, 3:30 PM - 5:00 PM",
                "max_participants": 15,
                "contact_email": "art@mergington.edu"
            },
            {
                "name": "Drama Club",
                "description": "Act, direct, and produce plays and performances",
                "category": "Arts",
                "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
                "max_participants": 20,
                "contact_email": "drama@mergington.edu"
            },
            {
                "name": "Math Club",
                "description": "Solve challenging problems and participate in math competitions",
                "category": "Academic",
                "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
                "max_participants": 10,
                "contact_email": "math@mergington.edu"
            },
            {
                "name": "Debate Team",
                "description": "Develop public speaking and argumentation skills",
                "category": "Academic",
                "schedule": "Fridays, 4:00 PM - 5:30 PM",
                "max_participants": 12,
                "contact_email": "debate@mergington.edu"
            }
        ]

        for activity_data in initial_activities:
            activity = Activity(**activity_data)
            db.add(activity)

        # Seed initial registrations
        initial_registrations = [
            ("Chess Club", ["michael@mergington.edu", "daniel@mergington.edu"]),
            ("Programming Class", ["emma@mergington.edu", "sophia@mergington.edu"]),
            ("Gym Class", ["john@mergington.edu", "olivia@mergington.edu"]),
            ("Soccer Team", ["liam@mergington.edu", "noah@mergington.edu"]),
            ("Basketball Team", ["ava@mergington.edu", "mia@mergington.edu"]),
            ("Art Club", ["amelia@mergington.edu", "harper@mergington.edu"]),
            ("Drama Club", ["ella@mergington.edu", "scarlett@mergington.edu"]),
            ("Math Club", ["james@mergington.edu", "benjamin@mergington.edu"]),
            ("Debate Team", ["charlotte@mergington.edu", "henry@mergington.edu"])
        ]

        for activity_name, emails in initial_registrations:
            activity = db.query(Activity).filter(Activity.name == activity_name).first()
            if activity:
                for email in emails:
                    # Create a dummy user if they don't exist
                    user = db.query(Registration).filter(Registration.user_id == 0).first()
                    if not user:
                        registration = Registration(user_id=0, activity_id=activity.id)
                        db.add(registration)

        db.commit()

@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    create_tables()
    # Seed initial data
    db = next(get_db())
    try:
        seed_initial_data(db)
    finally:
        db.close()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)) -> Dict[str, Dict[str, Any]]:
    """Get all activities with their details and current participant count."""
    activities = db.query(Activity).filter(Activity.is_active == True).all()

    result = {}
    for activity in activities:
        # Count current registrations
        participant_count = db.query(func.count(Registration.id)).filter(
            Registration.activity_id == activity.id
        ).scalar()

        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": participant_count,  # Return count instead of list for privacy
            "category": activity.category,
            "contact_email": activity.contact_email
        }

    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Find the activity
    activity = db.query(Activity).filter(
        Activity.name == activity_name,
        Activity.is_active == True
    ).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if already registered (for now, we'll use email as identifier)
    # In a real system, this would be a user ID
    existing_registration = db.query(Registration).filter(
        Registration.activity_id == activity.id,
        Registration.user_id == 0  # Using 0 as placeholder for email-based registration
    ).first()

    if existing_registration:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Check capacity
    current_count = db.query(func.count(Registration.id)).filter(
        Registration.activity_id == activity.id
    ).scalar()

    if current_count >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is at maximum capacity"
        )

    # Create registration
    registration = Registration(
        user_id=0,  # Placeholder - in real system this would be actual user ID
        activity_id=activity.id
    )
    db.add(registration)
    db.commit()

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    # Find the activity
    activity = db.query(Activity).filter(
        Activity.name == activity_name,
        Activity.is_active == True
    ).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Find and delete registration
    registration = db.query(Registration).filter(
        Registration.activity_id == activity.id,
        Registration.user_id == 0  # Placeholder
    ).first()

    if not registration:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove registration
    db.delete(registration)
    db.commit()

    return {"message": f"Unregistered {email} from {activity_name}"}
