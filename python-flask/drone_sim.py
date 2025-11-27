import time
import random
from models import db, Drone, Order
from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 6371 * c

def move_towards(lat1, lon1, lat2, lon2, step_km=0.1):
    dist = haversine(lat1, lon1, lat2, lon2)
    if dist < step_km:
        return lat2, lon2
    ratio = step_km / dist
    return (
        lat1 + (lat2 - lat1) * ratio,
        lon1 + (lon2 - lon1) * ratio
    )

def start_simulator(socketio):
    while True:
        drones = Drone.query.filter_by(status='delivering').all()
        for d in drones:
            order = Order.query.filter_by(assigned_drone_id=d.id).first()
            if not order:
                continue

            new_lat, new_lon = move_towards(
                d.lat, d.lon,
                order.lat, order.lon
            )

            d.lat = new_lat
            d.lon = new_lon
            d.battery_percent -= 0.2

            db.session.commit()

            socketio.emit('drone_update', {
                'drone_id': d.id,
                'lat': d.lat,
                'lon': d.lon,
                'battery': d.battery_percent,
            })

            if haversine(d.lat, d.lon, order.lat, order.lon) < 0.05:
                d.status = 'idle'
                order.status = 'delivered
