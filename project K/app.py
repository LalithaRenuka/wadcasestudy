from flask import Flask, render_template, request, jsonify, url_for
import os
import datetime
import requests

app = Flask(__name__)

# Configuration
USER_DATA_FILE = "users.txt"
LOG_FILE_DIR = "ride_logs"
SERPAPI_KEY = os.getenv('SERPAPI_KEY', "05532de29082adcb6aee4ce9f32cf0f17196740a71387643ba7001893ceb22da")

# Ensure ride logs directory exists
if not os.path.exists(LOG_FILE_DIR):
    os.makedirs(LOG_FILE_DIR)

# Ensure user data file exists
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "w") as f:
        pass  # Create empty user file

def get_user_log_file(email):
    """Returns the path for a user's log file."""
    return os.path.join(LOG_FILE_DIR, f"{email}.txt")

def log_ride(email, start, destination, vehicle, cost_details):
    """Logs ride details into a user's specific text file."""
    log_file = get_user_log_file(email)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"[{timestamp}] Start: {start}, Destination: {destination}, Vehicle: {vehicle}, Costs: {cost_details}\n"
    with open(log_file, "a") as file:
        file.write(log_entry)

@app.route("/log_ride", methods=["POST"])
def log_ride_endpoint():
    """API to log ride details."""
    data = request.json
    if not all(key in data for key in ["email", "start", "destination", "vehicle", "costs"]):
        return jsonify({"error": "Missing data"}), 400
    
    log_ride(data["email"], data["start"], data["destination"], data["vehicle"], data["costs"])
    return jsonify({"message": "Ride logged successfully"})

@app.route("/get_history", methods=["GET"])
def get_history():
    """API to fetch ride history."""
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    log_file = get_user_log_file(email)
    if not os.path.exists(log_file):
        return jsonify({"history": []})

    with open(log_file, "r") as file:
        history = file.readlines()
    
    return jsonify({"history": history})

@app.route("/")
def home():
    """Render Sign In / Sign Up Page."""
    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    """User Sign Up."""
    data = request.json
    if not all(k in data for k in ["fullname", "email", "phone", "password"]):
        return jsonify({"error": "Missing fields"}), 400

    email, password, fullname, phone = data["email"], data["password"], data["fullname"], data["phone"]

    # Check if user already exists
    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            stored_email, _ = line.strip().split(",", 1)
            if stored_email == email:
                return jsonify({"message": "User already exists! Try signing in."})

    # Store user data
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{email},{password},{fullname},{phone}\n")

    return jsonify({"message": "Sign Up Successful! Please Sign In."})

@app.route("/signin", methods=["POST"])
def signin():
    """User Sign In."""
    data = request.json
    if not all(k in data for k in ["email", "password"]):
        return jsonify({"error": "Missing fields"}), 400

    email, password = data["email"], data["password"]

    with open(USER_DATA_FILE, "r") as f:
        for line in f:
            stored_email, stored_password, _, _ = line.strip().split(",", 3)
            if stored_email == email and stored_password == password:
                return jsonify({"redirect": url_for("dashboard")})

    return jsonify({"message": "Invalid Email or Password"})

@app.route("/dashboard")
def dashboard():
    """Render Dashboard Page."""
    return render_template("index.html")

@app.route("/check")
def vehicle_cost():
    """Render Vehicle Cost Page."""
    return render_template("vehicle_cost.html")

@app.route("/act")
def history_page():
    """Render Ride History Page."""
    return render_template("history.html")

@app.route("/flights", methods=["GET", "POST"])
def flights():
    """Flight Search Page."""
    if request.method == "POST":
        departure = request.form.get("departure")
        arrival = request.form.get("arrival")
        outbound_date = request.form.get("outbound_date")
        return_date = request.form.get("return_date")

        params = {
            "api_key": SERPAPI_KEY,
            "engine": "google_flights",
            "departure_id": departure,
            "arrival_id": arrival,
            "outbound_date": outbound_date,
            "return_date": return_date,
        }

        search = requests.get("https://serpapi.com/search", params=params)

        if search.status_code == 200:
            response = search.json()
            flights = []

            for key in ["best_flights", "other_flights"]:
                for item in response.get(key, []):
                    for flight in item.get("flights", []):
                        flights.append({
                            "airline": flight.get("airline", "Unknown"),
                            "airplane": flight.get("airplane", "Unknown"),
                            "departure_airport": flight.get("departure_airport", {"name": "Unknown", "time": "Unknown"}),
                            "arrival_airport": flight.get("arrival_airport", {"name": "Unknown", "time": "Unknown"}),
                            "price": item.get("price", "N/A"),
                        })
            return render_template("flights.html", flights=flights)

    return render_template("flights.html", flights=None)

if __name__ == "__main__":
    app.run(debug=True)
