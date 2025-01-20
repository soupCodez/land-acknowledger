import json
import requests
from flask import Flask, render_template, request, redirect, url_for
from geopy.geocoders import Nominatim

app = Flask(__name__)

def fetch(uri):
    requests.get(uri)

with open('config.json') as config_file:
    config = json.load(config_file)
    app.config.update(config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/geocode', methods=['POST'])
def geocode():
    address = request.form['address']
    if not address:
        return "Address not provided", 400

    geolocator = Nominatim(user_agent="land-acknowledger")
    location = geolocator.geocode(address)
    if location:
        if not location.latitude or not location.longitude:
            return "Location not found", 404
        return redirect(url_for('result', latitude=location.latitude, longitude=location.longitude))
    else:
        return "Address not found", 404

@app.route('/result')
def result():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    api_key = app.config['API_KEY']
    url = f'https://native-land.ca/api/index.php?maps=languages,territories&position={latitude},{longitude}&key={api_key}'
    response = fetch(url)
    data = response.json()
    
    land_names = [item['properties']['Name'] for item in data]
    return render_template('result.html', names=', '.join(land_names))

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
elif __name__ == 'app':
    application = app