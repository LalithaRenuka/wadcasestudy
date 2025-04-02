import os
import json
import requests

# Set API key securely
api_key = os.getenv('SERPAPI_KEY')
if not api_key:
    api_key = "05532de29082adcb6aee4ce9f32cf0f17196740a71387643ba7001893ceb22da"  # Use carefully

# Define request parameters
params = {
    "api_key": api_key,
    "engine": "google_flights",
    "departure_id": "JFK",  # Fixed typo (should be "JFK", not "JKF")
    "arrival_id": "AUS",
    "outbound_date": "2025-04-02",
    "return_date": "2025-04-03",
}

# Make the API request
search = requests.get("https://serpapi.com/search", params=params)

# Check response status
if search.status_code == 200:
    response = search.json()
    
    # Print response in a readable format
    print(json.dumps(response, indent=4))

    # Extract flight details
    keys = ["best_flights", "other_flights"]
    for key in keys:
        print("\nKey: " + key)
        
        for item in response.get(key, []):  # Use .get() to avoid KeyError
            for flight in item.get("flights", []):
                print(flight.get("departure_airport", {}).get("name", "Unknown"), 
                      flight.get("departure_airport", {}).get("time", "Unknown"))

                print(flight.get("arrival_airport", {}).get("name", "Unknown"), 
                      flight.get("arrival_airport", {}).get("time", "Unknown"))

                print("Airplane: " + flight.get("airplane", "Unknown") + 
                      " | Airline: " + flight.get("airline", "Unknown"))

            print("Price: " + str(item.get("price", "N/A")))  # Use .get() for safety
            print("Departure token: " + str(item.get("departure_token", "N/A")))
            print("")

else:
    print(f"Error: {search.status_code} - {search.text}")  # Print error message
