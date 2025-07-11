from backend.app.db import SessionLocal
from backend.app.models.location import Location

def seed_locations():
    db = SessionLocal()
    locations = [
        Location(name="Downtown", address="123 Main St, City", hours="10am-10pm"),
        Location(name="Uptown", address="456 Elm St, City", hours="11am-9pm"),
        Location(name="Suburb", address="789 Oak Ave, City", hours="9am-8pm"),
    ]
    for loc in locations:
        if not db.query(Location).filter_by(name=loc.name).first():
            db.add(loc)
    db.commit()
    db.close()
    print("Seeded locations!")

if __name__ == "__main__":
    seed_locations()