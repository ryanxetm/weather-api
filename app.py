import requests
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

weather_data = {
    "data": None,
    "timestamp": None
}

CACHE_TTL = 3  # Cache time-to-live in seconds

def primary_weather_api_url(city):
    """Constructs the URL for the primary weather API."""
    weather_api_access_key = "17d394962af18f49783b8a89846c7ece"
    return f"http://api.weatherstack.com/current?access_key={weather_api_access_key}&query={city}"

def failover_weather_api_url(city):
    """Constructs the URL for the failover weather API."""
    # Note: THE qUERY PARAMETER MUST BE IN THE FORMAT 'CITY,COUNTRY_CODE' (e.g., 'Sydney,AU'
    # but given the exam requirements, we will assume the country code is always 'AU'.
    return f"http://api.openweathermap.org/data/2.5/weather?q={city},AU&appid=2326504fb9b100bee21400190e4dbe6d&units=metric"

def save_to_cache(wind_speed, temperature_degrees):
    """Saves weather data to the cache."""
    weather_data['data'] = {
        "wind_speed": wind_speed,
        "temperature_degrees": temperature_degrees
    }
    weather_data['timestamp'] = time.time()

def get_cached_weather_data():
    """Returns cached weather data if it's still valid, otherwise returns None."""
    if weather_data['data'] is not None and weather_data['timestamp'] is not None:
        if time.time() - weather_data['timestamp'] < CACHE_TTL:
            return weather_data
    return None

def get_stale_cached_weather_data():
    """Returns stale cached weather data if available, otherwise returns None."""
    if weather_data['data'] is not None and weather_data['timestamp'] is not None:
        return weather_data
    return None

def call_weather_api(url):
    """Helper function to call a weather API and return the response."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"Error calling weather API: {e}")
        return None

def get_weather_data(city):
    """Fetches weather data from the primary API, and if it fails, tries the failover API."""

    # First, check if we have valid cached data
    cached_data = get_cached_weather_data()
    if cached_data:
        print("Returning cached weather data")
        return cached_data['data']

    response = call_weather_api(primary_weather_api_url(city))
    if response:
        try:
            print("Successfully fetched data from primary API")
            wind_speed = response['current']['wind_speed']
            temperature_degrees = response['current']['temperature']
            save_to_cache(wind_speed, temperature_degrees)
            return weather_data['data']
        except KeyError as e:
            print(f"Error parsing primary API response: {e}")


    # If primary API fails, try the failover API
    response = call_weather_api(failover_weather_api_url(city))
    if response:
        try:
            print("Successfully fetched data from failover API")
            wind_speed = response['wind']['speed']
            temperature_degrees = response['main']['temp']
            save_to_cache(wind_speed, temperature_degrees)
            return weather_data['data']
        except KeyError as e:
            print(f"Error parsing failover API response: {e}")

    # If both APIs fail, return stale cached data if available
    stale_data = get_stale_cached_weather_data()
    if stale_data:
        print("Returning stale cached weather data")
        return stale_data['data']
    
    # If all attempts fail, return None
    return None

@app.route("/")
def home():
    """Home route to confirm the server is running."""
    return "Weather API is running. Use /weather?city=CityName to get weather data."

@app.route("/weather", methods=["GET"])
def get_weather():
    """Handle GET requests to return current weather data."""
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    data = get_weather_data(city)
    if data:
        return jsonify({
            "wind_speed": data['wind_speed'],
            "temperature_degrees": data['temperature_degrees']
        })
    else:
        return jsonify({
            "error": "Unable to fetch weather data at this time."
        }), 503
        
if __name__ == "__main__":
    app.run(debug=True)