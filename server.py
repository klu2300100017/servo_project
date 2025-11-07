from flask import Flask, render_template, request, jsonify, send_from_directory
import math
import pandas as pd
import os

app = Flask(__name__)

stations = pd.read_csv("stations.csv")

def calc_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/nearest', methods=['POST'])
def nearest_station():
    data = request.get_json()
    user_lat = float(data['lat'])
    user_lon = float(data['lon'])

    min_dist = float('inf')
    nearest = None

    for _, row in stations.iterrows():
        dist = calc_distance(user_lat, user_lon, row['lat'], row['lon'])
        if dist < min_dist:
            min_dist = dist
            nearest = row

    if nearest is not None:
        return jsonify({
            'name': nearest['name'],
            'lat': nearest['lat'],
            'lon': nearest['lon'],
            'distance': round(min_dist, 2)
        })
    else:
        return jsonify({'error': 'No stations found'})

@app.route('/manifest.json')
def manifest():
    return send_from_directory('templates', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('templates', 'service-worker.js')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
