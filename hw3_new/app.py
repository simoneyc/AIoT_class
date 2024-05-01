# app.py

from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Connect to SQLite database
conn = sqlite3.connect('sensor_data.db', check_same_thread=False)
c = conn.cursor()

# Create a table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
             (id INTEGER PRIMARY KEY,
             temperature REAL,
             humidity REAL,
             timestamp TEXT)''')

# Route to receive data from ESP32 and insert into the database
@app.post('/update_data')
def update_data():
    data = request.json
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Received data: temperature={temperature},humidity={humidity}")
    c.execute("INSERT INTO sensor_data (temperature, humidity, timestamp) VALUES (?, ?, ?)", (temperature, humidity, timestamp))
    conn.commit()
    return 'Data received and stored successfully'

# Route to fetch real-time sensor data
@app.route('/api/data')
def get_sensor_data():
    c.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
    rows = c.fetchall()
    data = [{'timestamp': row[3], 'temperature': row[1], 'humidity': row[2]} for row in reversed(rows)]
    return jsonify(data)

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host = "0.0.0.0",port = 5000, debug = True)
