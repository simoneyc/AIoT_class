from flask import Flask, render_template, request, jsonify
from weather import save

app = Flask(__name__)

data = save
@app.route('/')
def index():
    regions = list(data.keys())
    return render_template('index.html', regions=regions)

@app.route('/get_chart_data', methods=['POST'])
def get_chart_data():
    region = request.json['region']
    region_data = data.get(region, [])

    dates = [item['date'] for item in region_data]
    max_temps = [int(item['maxTemp']) for item in region_data]
    min_temps = [int(item['minTemp']) for item in region_data]

    return jsonify({'dates': dates, 'maxTemps': max_temps, 'minTemps': min_temps})

if __name__ == '__main__':
    app.run(debug=True)
