from flask import Flask, render_template, request, jsonify

# 1. INITIALIZE APP AND GLOBAL STATE
app = Flask(__name__)

# Global variables to hold the current state and threshold
# NOTE: For production, you would use a database (like PostgreSQL) instead of global vars.
current_temp = 0.0
current_humidity = 0.0
threshold_temp = 28.0 # Default threshold in Celsius

@app.route('/')
def index():
    """Serves the main GUI page."""
    # The index.html file will display the current status and controls.
    return render_template('index.html')

# --- API ENDPOINTS FOR THE ESP32 ---

@app.route('/api/update_temp', methods=['POST'])
def update_temp():
    """
    Receives temperature/humidity from the ESP32.
    Determines the buzzer state based on the threshold.
    """
    global current_temp, current_humidity, threshold_temp
    
    try:
        data = request.get_json()
        
        # Ensure we have the necessary data keys
        if 'temperature' not in data or 'humidity' not in data:
            return jsonify({"error": "Missing temperature or humidity data"}), 400

        # Update global variables with new readings
        current_temp = float(data['temperature'])
        current_humidity = float(data['humidity'])
        
        # BUZZER LOGIC: Compare the reading to the current user-set threshold
        buzzer_state = "ON" if current_temp >= threshold_temp else "OFF"
        
        print(f"Received Temp: {current_temp}°C, Buzzer State: {buzzer_state}")
        
        # Send the required buzzer state back to the ESP32
        return jsonify({"buzzer_state": buzzer_state})

    except Exception as e:
        print(f"Error processing update: {e}")
        return jsonify({"error": str(e)}), 500


# --- API ENDPOINTS FOR THE WEB GUI (Frontend) ---

@app.route('/api/get_data', methods=['GET'])
def get_data():
    """Returns all current data for the GUI to display."""
    global current_temp, current_humidity, threshold_temp
    
    return jsonify({
        "temperature": current_temp,
        "humidity": current_humidity,
        "threshold": threshold_temp
    })

@app.route('/api/set_threshold', methods=['POST'])
def set_threshold():
    """Receives a new threshold value from the GUI."""
    global threshold_temp
    
    try:
        data = request.get_json()
        new_threshold = float(data['threshold'])
        
        # Update the global threshold
        threshold_temp = new_threshold
        
        print(f"Threshold updated to: {threshold_temp}°C")
        
        return jsonify({"message": "Threshold updated successfully", "new_threshold": threshold_temp})
        
    except Exception as e:
        print(f"Error setting threshold: {e}")
        return jsonify({"error": "Invalid threshold value"}), 400


if __name__ == '__main__':
    # Use Flask's built-in server for local development only
    # Render will use gunicorn (via Procfile)
    app.run(debug=True, port=8080)