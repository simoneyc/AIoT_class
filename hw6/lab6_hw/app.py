import json
import time

from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    stream_with_context,
)

from db_method import DB_NAME, get_all_data, get_single_data, initdb, insert_sensor_data

app = Flask(__name__, template_folder="templates")

data = {"temperature": [], "humidity": []}

# -----------------前端頁面-----------
# 主頁


@app.route("/") 
def index():
    return render_template("index.html")


@app.get("/visualize-realtime")
def visualize():
    return render_template("realtime-data.html")


@app.get("/visualize-specifiedtime")
def visualize2():
    return render_template("specifiedtime-data.html")


@app.get("/visualize-camera_view")
def visualize3():
    return render_template("camera_view.html")


# -----------------後端頁面-----------
# post 給esp32用


@app.post("/post_data")
def receive_data():
    try:
        content = request.get_json()

        temperature = content["temperature"]
        humidity = content["humidity"]

        data["temperature"].append(temperature)
        data["humidity"].append(humidity)

        # Call function to initialize database if not already initialized
        # initdb()

        # Call function to insert sensor data into the database
        insert_sensor_data(temperature, humidity)

        print(f"Received data: temperature={temperature}, humidity={humidity}")
        return jsonify({"success": True})

    except Exception as e:
        print(f"Error receiving data: {str(e)}")
        return jsonify({"success": False, "error": str(e)})


@app.get("/get_data")
def get_data():
    try:
        # Extract start_time and end_time parameters from the request URL
        start_time_str = request.args.get("start_time")
        end_time_str = request.args.get("end_time")

        if not start_time_str or not end_time_str:
            return (
                jsonify({"error": "start_time and end_time parameters are required"}),
                400,
            )

        # Call the function to retrieve temperature data between start_time and end_time
        data_result = get_single_data(start_time_str, end_time_str, DB_NAME)

        if data_result is None:
            return jsonify({"error": "Failed to retrieve temperature data"}), 500

        # Convert data to a list of dictionaries for JSON response
        formatted_data = [
            {"temperature": row[0], "humidity": row[1], "timestamp": row[2]}
            for row in data_result
        ]

        return jsonify(formatted_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/get_all_data")
def get_all_data_route():
    try:
        # Call the function to retrieve all temperature data
        all_data = get_all_data(DB_NAME)

        if all_data is None:
            return jsonify({"error": "Failed to retrieve all the data"}), 500

        # Convert data to a list of dictionaries for JSON response
        formatted_data = [
            {"temperature": row[0], "humidity": row[1], "timestamp": row[2]}
            for row in all_data
        ]

        return jsonify(formatted_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


class camera_view:

    def __init__(self):
        self.a_camera_frame = {"image": "NC", "timestamp": ""}

    def update_camera_frame(self, frame):
        self.a_camera_frame = frame

    def get_camera_frame(self):
        return self.a_camera_frame


a_camera_view = camera_view()


@app.post("/post_camera_frame")
def receive_camera_frame():
    try:
        content = request.get_json()
        a_camera_view.update_camera_frame(content)
        return "camera_frame updated successfully"
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/get_camera_stream")
def make_stream():
    # 與相機網頁前端建立event-stream
    @stream_with_context
    def generate():
        try:
            while True:
                yield "data:" + json.dumps(a_camera_view.get_camera_frame()) + "\n\n"
                time.sleep(0.1)
        except GeneratorExit:
            print("closed")

    # 用stream發給前端
    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    initdb(DB_NAME)
    app.run(host="0.0.0.0", port=5000, debug=True)
