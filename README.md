# Weather API

A lightweight Flask service that returns current wind speed and temperature for a requested city.

## Overview

This project exposes a simple REST endpoint with primary and failover weather API support.

- Primary weather provider: Weatherstack
- Failover provider: OpenWeatherMap
- In-memory cache with a 3-second TTL
- Stale cached data is returned if both providers fail and a prior result exists

## Requirements

- Python 3.8+ (or newer)
- `Flask`
- `requests`
- `gunicorn` (optional Render)

## Installation

1. Create a virtual environment:

```powershell and terminal
python -m venv .venv
```

2. Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

```terminal
.venv\Scripts\activate
```

3. Install dependencies:

```powershell and terminal
pip install -r requirements.txt
```

## Running the App

Run the application with:

```powershell
python app.py
```

The API will start locally at `http://127.0.0.1:5000`.

## (Optional) Deploy in Render

- In `Render` Dashboard > New > Web Service
- Connect GitHub Repo `https://github.com/ryanxetm/weather-api.git`
- Config Build Settings, use:

```terminal:
  pip install -r requirements.txt
```

- Start Command

```terminal:
  gunicorn app:app
```

- Deploy Service

## API Endpoints

### `GET /`

Returns a basic status message indicating the API is running.

### `GET /weather?city=CityName`

Fetches weather data for the requested city.

Example request:

```powershell
curl "http://127.0.0.1:5000/weather?city=Sydney"
```

The API is deployed in Render, you can access the API using:

```
https://weather-api-p0af.onrender.com/weather?city=Melbourne
```

Successful response:

```json
{
  "wind_speed": 5.1,
  "temperature_degrees": 20
}
```

Error responses:

- `400` if the `city` query parameter is missing
- `503` if weather data cannot be fetched from either provider

## Notes

- API keys are currently embedded in `app.py`.
- The failover API call assumes Australian cities by appending `,AU`.
- Cached data is stored in memory and resets when the service restarts.

## Future Improvements

- Move API keys to environment variables
- Add country support for the failover endpoint
- Add automated tests and better error handling
- Replace in-memory cache with a persistent cache for multi-instance use
- Add error response message if the city does not exist
- Add other countries instead of just AU
