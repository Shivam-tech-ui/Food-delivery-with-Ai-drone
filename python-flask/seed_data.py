from app import app, db
from models import Restaurant, Drone, User

with app.app_context():
    db.drop_all()
    db.create_all()

    # Demo User
    user = User(name="Demo User", lat=21.1702, lon=72.8311)
    db.session.add(user)

    # Restaurants in Surat (example)
    rest1 = Restaurant(name="Surat Food House",
                       lat=21.1702, lon=72.8311, service_radius_km=5)
    rest2 = Restaurant(name="Gourmet Hub",
                       lat=21.2000, lon=72.8400, service_radius_km=5)

    db.session.add_all([rest1, rest2])
    db.session.commit()

    # Drones positioned near first restaurant
    drones = [
        Drone(identifier="DRONE-01", lat=rest1.lat, lon=rest1.lon,
              battery_percent=100, status="idle"),
        Drone(identifier="DRONE-02", lat=rest1.lat + 0.01,
              lon=rest1.lon + 0.01, battery_percent=95, status="idle"),
        Drone(identifier="DRONE-03", lat=rest2.lat,
              lon=rest2.lon, battery_percent=90, status="idle"),
    ]

    db.session.add_all(drones)
    db.session.commit()

    print("Database initialized with restaurants, drones, and user.")
