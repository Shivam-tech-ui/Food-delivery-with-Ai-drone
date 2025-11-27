let map = L.map('map').setView([21.1702, 72.8311], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

let droneMarkers = {};
let orderMarkers = {};

const socket = io();

// Receive initial data on connect
socket.on("initial_state", (data) => {
    data.drones.forEach(updateDroneMarker);
    data.orders.forEach(updateOrderMarker);
});

// Real-time updates
socket.on("drone_update", updateDroneMarker);
socket.on("order_update", updateOrderMarker);

function updateDroneMarker(d) {
    if (!d.lat || !d.lon) return;
    if (droneMarkers[d.drone_id || d.id]) {
        droneMarkers[d.id].setLatLng([d.lat, d.lon]);
    } else {
        droneMarkers[d.id] = L.marker([d.lat, d.lon], {
            title: "Drone " + d.id
        }).addTo(map);
    }
}

function updateOrderMarker(o) {
    if (!o.lat || !o.lon) return;
    if (orderMarkers[o.order_id || o.id]) {
        orderMarkers[o.id].setLatLng([o.lat, o.lon]);
    } else {
        orderMarkers[o.id] = L.circleMarker([o.lat, o.lon], {
            radius: 6,
            color: "red"
        }).addTo(map);
    }
}

// Button handler → Place customer order
async function placeOrder() {
    let lat = map.getCenter().lat;
    let lon = map.getCenter().lng;

    let response = await fetch("/api/place_order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            restaurant_id: 1,
            lat: lat,
            lon: lon,
            items: []
        })
    });

    let data = await response.json();
    alert("Order Placed: " + JSON.stringify(data));
}
