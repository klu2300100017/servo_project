from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import math
import os

# Use templates folder for HTML, manifest, and service worker
app = Flask(__name__, template_folder='templates', static_folder='templates')

# Load EV stations
stations = pd.read_csv("stations.csv")

# Haversine formula to calculate distance
def calc_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Homepage
@app.route('/')
def home():
    return render_template('index.html')

# API: nearest station
@app.route('/nearest', methods=['GET'])
def nearest_station():
    try:
        user_lat = float(request.args.get('lat', 0))
        user_lon = float(request.args.get('lon', 0))
        battery_type = request.args.get('battery_type', '').strip()
        if not battery_type:
            return jsonify({'error': 'battery_type parameter missing'})

        # Filter stations by battery type (case-insensitive)
        filtered = stations[stations['battery_type'].str.lower() == battery_type.lower()]
        if filtered.empty:
            return jsonify({'error': f'No stations found for battery type: {battery_type}'})

        # Compute distance for all filtered stations
        filtered['distance'] = filtered.apply(
            lambda row: calc_distance(user_lat, user_lon, row['lat'], row['lon']),
            axis=1
        )

        # Get the nearest station
        nearest = filtered.sort_values('distance').iloc[0]

        return jsonify({
            'name': nearest['name'],
            'lat': nearest['lat'],
            'lon': nearest['lon'],
            'distance': round(nearest['distance'], 2),
            'battery_type': nearest['battery_type']
        })
    except Exception as e:
        return jsonify({'error': str(e)})

# Serve manifest and service worker
@app.route('/manifest.json')
def manifest():
    return send_from_directory('templates', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('templates', 'service-worker.js')

# Run app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
