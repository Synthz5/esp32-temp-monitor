from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

current_temp = 0.0
current_humidity = 0.0
threshold_temp = 35.0 

@app.route('/')
def index():
    """Serves the main GUI page."""
    return render_template('index.html')

@app.route('/api/update_temp', methods=['POST'])
def update_temp():
    """
    Receives temperature/humidity from the ESP32.
    Determines the buzzer state based on the threshold.
    """
    global current_temp, current_humidity, threshold_temp
    
    try:
        data = request.get_json()
        if 'temperature' not in data or 'humidity' not in data:
            return jsonify({"error": "Missing temperature or humidity data"}), 400

        current_temp = float(data['temperature'])
        current_humidity = float(data['humidity'])
        buzzer_state = "ON" if current_temp >= threshold_temp else "OFF"
        print(f"Received Temp: {current_temp}°C, Buzzer State: {buzzer_state}")
        return jsonify({"buzzer_state": buzzer_state})

    except Exception as e:
        print(f"Error processing update: {e}")
        return jsonify({"error": str(e)}), 500

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
        
        threshold_temp = new_threshold
        
        print(f"Threshold updated to: {threshold_temp}°C")
        
        return jsonify({"message": "Threshold updated successfully", "new_threshold": threshold_temp})
        
    except Exception as e:
        print(f"Error setting threshold: {e}")
        return jsonify({"error": "Invalid threshold value"}), 400


if __name__ == '__main__':
    app.run(debug=True, port=8080)
