import json
import requests
from flask import Flask, render_template, request, redirect, url_for
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Function to fetch data from a given URI
def fetch(uri):
    if uri is None:
        return None
    elif uri == '':
        return None
    return requests.get(uri)

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)
    app.config.update(config)

# Route for the home page
@app.route('/')
def index():
    # Render the home page template
    return render_template('index.html')

# Route to handle geocoding of an address
@app.route('/geocode', methods=['POST'])
def geocode():
    # Get the address from the form
    address = request.form['address']
    if not address or address == '':
        return "Address not provided", 400

    # Use geopy to geocode the address
    geolocator = Nominatim(user_agent="land-acknowledger")
    location = geolocator.geocode(address)
    if location:
        if not location.latitude or not location.longitude:
            return "Location not found", 404
        # Redirect to the result page with latitude and longitude as query parameters
        return redirect(url_for('result', latitude=location.latitude, longitude=location.longitude))
    else:
        return "Address not found", 404

# Route to display the result based on latitude and longitude
@app.route('/result')
def result():
    # Get latitude and longitude from query parameters
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    api_key = app.config['API_KEY']
    # Construct the API URL
    url = f'https://native-land.ca/api/index.php?maps=languages,territories&position={latitude},{longitude}&key={api_key}'
    response = fetch(url)
    data = response.json()
    
    # Extract land names from the API response
    land_names = [item['properties']['Name'] for item in data]
    # Render the result template with the land names
    return render_template('result.html', names=', '.join(land_names))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])