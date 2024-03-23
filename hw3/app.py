from flask import Flask, render_template, jsonify
import sqlite3
import random
import time

app = Flask(__name__)

# Function to generate random data and store it in the database
def generate_and_store_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('sensors.db')
    cursor = conn.cursor()
    while True:
        # Generate random humidity between 40% and 60%
        humidity = random.uniform(40, 60)
        # Generate random temperature between 20°C and 30°C
        temperature = random.uniform(20, 30)
        # Insert the generated data into the 'sensor_data' table
        cursor.execute("INSERT INTO sensor_data (humidity, temperature) VALUES (?, ?)", (humidity, temperature))
        conn.commit()
        # Wait for 2 seconds before next iteration
        time.sleep(2)

# Route to display the web page
@app.route('/')
def index():
    return render_template('index.html')

# Route to fetch data from the database
@app.route('/data')
def get_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('sensors.db')
    cursor = conn.cursor()
    # Select the latest 30 entries of humidity and temperature from 'sensor_data' table
    cursor.execute("SELECT humidity, temperature FROM sensor_data ORDER BY id DESC LIMIT 30")
    # Fetch the selected data
    data = cursor.fetchall()
    return jsonify(data)

if __name__ == '__main__':
    # Create the database schema if it doesn't exist
    conn = sqlite3.connect('sensors.db')
    cursor = conn.cursor()
    # Create the 'sensor_data' table with columns id, humidity, and temperature
    cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      humidity REAL,
                      temperature REAL)''')
    conn.commit()
    conn.close()

    # Start a new thread to generate and store data
    import threading
    threading.Thread(target=generate_and_store_data).start()

    # Run the Flask app
    app.run(debug=True)
