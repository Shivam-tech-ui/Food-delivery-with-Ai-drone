from flask import Flask, request, jsonify, render_template
from models import db, User, Restaurant, MenuItem, Drone, Order
from math import radians, cos, sin, asin, sqrt
import json, threading
from flask_socketio import SocketIO
from drone_sim import start_simulator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drone_delivery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app, async_mode='eventlet')


# ---------------- Utility: distance ----------------
def haversine(lat1, lon1, lat2, lon2):
    """Return distance in km between two (lat, lon) points."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km


with app.app_context():
    db.create_all()


# ---------------- Routes ----------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/api/drones')
def list_drones():
    drones = Drone.query.all()
    return jsonify([
        {
            'id': d.id,
            'identifier': d.identifier,
            'lat': d.lat,
            'lon': d.lon,
            'battery': d.battery_percent,
            'status': d.status,
        }
        for d in drones
    ])


@app.route('/api/restaurants')
def list_restaurants():
    rests = Restaurant.query.all()
    return jsonify([
        {
            'id': r.id,
            'name': r.name,
            'lat': r.lat,
            'lon': r.lon,
            'service_radius_km': r.service_radius_km,
        }
        for r in rests
    ])


@app.route('/api/place_order', methods=['POST'])
def place_order():
    data = request.json
    user_id = data.get('user_id', 1)  # demo user
    rest_id = int(data['restaurant_id'])
    lat = float(data['lat'])
    lon = float(data['lon'])

    order = Order(
        user_id=user_id,
        restaurant_id=rest_id,
        menu_json=json.dumps(data.get('items', [])),
        lat=lat,
        lon=lon,
    )
    db.session.add(order)
    db.session.commit()

    assigned = assign_drone(order)
    if assigned:
        socketio.emit('order_update', {
            'order_id': order.id,
            'status': order.status,
            'drone_id': order.assigned_drone_id,
            'eta': order.eta_minutes,
            'lat': order.lat,
            'lon': order.lon,
        })
        return jsonify({
            'status': 'assigned',
            'order_id': order.id,
            'drone_id': assigned.id,
            'eta_minutes': order.eta_minutes,
        })
    else:
        return jsonify({'status': 'no_drone_available'}), 400


def assign_drone(order: Order):
    """Pick the best drone for this order (simple greedy AI)."""
    rest = Restaurant.query.get(order.restaurant_id)
    drones = Drone.query.filter_by(status='idle').all()
    candidates = []

    for d in drones:
        d_to_rest = haversine(d.lat, d.lon, rest.lat, rest.lon)
        rest_to_cust = haversine(rest.lat, rest.lon, order.lat, order.lon)
