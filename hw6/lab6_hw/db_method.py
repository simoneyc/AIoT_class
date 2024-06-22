import sqlite3
from datetime import datetime

DB_NAME = "temperature_data.sqlite"


# Initialize SQLite database
def initdb(db_name=DB_NAME):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS sensor_data (
                            id INTEGER PRIMARY KEY,
                            temperature REAL NOT NULL,
                            humidity REAL NOT NULL,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )"""
        )
        conn.commit()
        conn.close()
        print("(initdb) Database initialized successfully.")
    except sqlite3.Error as e:
        print("(initdb) Error occurred:", e)


# Insert sensor data into the SQLite database
def insert_sensor_data(temperature, humidity, timestamp=None, db_name=DB_NAME):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        if timestamp is None:
            timestamp = datetime.now().replace(microsecond=0)

        cursor.execute(
            """INSERT INTO sensor_data (temperature, humidity, timestamp) VALUES (?, ?, ?)""",
            (temperature, humidity, timestamp),
        )

        conn.commit()
        conn.close()
        print("(insert_sensor_data) Sensor data inserted successfully.")

    except sqlite3.Error as e:
        print("(insert_sensor_data) Error occurred:", e)


# Fetch sensor data from the SQLite database within a specified time period
def get_single_data(start_time_str, end_time_str, db_name=DB_NAME):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Construct the SQL query to retrieve sensor data within the specified time period
        query = """SELECT temperature, humidity, timestamp FROM sensor_data 
                   WHERE timestamp BETWEEN ? AND ?"""
        cursor.execute(query, (start_time_str, end_time_str))

        # Fetch all rows
        data = cursor.fetchall()

        # Close the connection
        conn.close()

        return data

    except sqlite3.Error as e:
        print("(get_single_data) Error occurred:", e)
        return None


# Fetch all the sensor data from the SQLite database
def get_all_data(db_name=DB_NAME):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Construct the SQL query to retrieve all sensor data
        query = """SELECT temperature, humidity, timestamp FROM sensor_data"""

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        data = cursor.fetchall()

        # Close the connection
        conn.close()

        return data

    except sqlite3.Error as e:
        print("Error occurred:", e)
        return None


# if __name__ == "__main__":
#     # 一開始就建立
#     initdb(DB_NAME)
