import json  # Import the JSON module to handle JSON data
import requests  # Import the requests module to make HTTP requests
from flask import Flask, render_template, request, redirect, url_for  # Import Flask and related functions
from geopy.geocoders import Nominatim  # Import Nominatim from geopy for geocoding

app = Flask(__name__)  # Create a Flask application instance

# Function to fetch data from a given URI
def fetch(uri):
    if uri is None:  # Check if the URI is None
        return None  # Return None if the URI is None
    elif uri == '':  # Check if the URI is an empty string
        return None  # Return None if the URI is an empty string
    return requests.get(uri)  # Make a GET request to the URI and return the response

# Load configuration from config.json
with open('config.json') as config_file:  # Open the config.json file
    config = json.load(config_file)  # Load the JSON data from the file
    app.config.update(config)  # Update the Flask app configuration with the loaded data

# Load questions from questions.json
with open('questions.json') as questions_file:  # Open the questions.json file
    QUESTIONS = json.load(questions_file)  # Load the JSON data from the file

@app.context_processor
def utility_processor():
    return dict(enumerate=enumerate)  # Make the enumerate function available in Jinja2 templates

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')  # Render and return the index.html template

# Route for the map page
@app.route('/map')
def map():
    return render_template('map.html')  # Render and return the map.html template

# Route for the info page
@app.route('/info')
def info():
    return render_template('info.html')  # Render and return the info.html template

# Route for the quiz page
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":  # Check if the request method is POST
        score = 0  # Initialize the score to 0
        responses = request.form  # Get the form responses
        for i, question in enumerate(QUESTIONS):  # Iterate over the questions with their index
            user_answer = responses.get(f"question{i}")  # Get the user's answer for the current question
            if user_answer == question["correctAnswer"]:  # Check if the user's answer is correct
                score += 1  # Increment the score if the answer is correct
        return render_template("quiz.html", questions=QUESTIONS, score=score)  # Render and return the quiz.html template with the score
    return render_template("quiz.html", questions=QUESTIONS, score=None)  # Render and return the quiz.html template without the score

# Route to handle geocoding of an address
@app.route('/geocode', methods=['POST'])
def geocode():
    address = request.form['address']  # Get the address input from the form
    if not address or address == '':  # Check if the address is not provided or is an empty string
        return "Address not provided", 400  # Return a 400 error with a message

    geolocator = Nominatim(user_agent="land-acknowledger")  # Create a geolocator instance with a user agent
    location = geolocator.geocode(address)  # Geocode the address to get the location
    if location:  # Check if the location is found
        if not location.latitude or not location.longitude:  # Check if the location has latitude and longitude
            return "Location not found", 404  # Return a 404 error with a message
        return redirect(url_for('result', latitude=location.latitude, longitude=location.longitude))  # Redirect to the result route with latitude and longitude
    else:
        return "Address not found", 404  # Return a 404 error with a message if the address is not found

# Route to display the result based on latitude and longitude
@app.route('/result')
def result():
    latitude = request.args.get('latitude')  # Get the latitude from the query parameters
    longitude = request.args.get('longitude')  # Get the longitude from the query parameters
    api_key = app.config['API_KEY']  # Get the API key from the app configuration
    url = f'https://native-land.ca/api/index.php?maps=languages,territories&position={latitude},{longitude}&key={api_key}'  # Construct the API URL with latitude, longitude, and API key
    response = fetch(url)  # Fetch the data from the API URL
    data = response.json()  # Parse the JSON response data
    
    land_names = [item['properties']['Name'] for item in data]  # Extract the land names from the response data
    return render_template('result.html', names=', '.join(land_names))  # Render and return the result.html template with the land names

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])  # Run the Flask app with debug mode based on the configuration