import requests
import json
import sqlite3
# 存成html
# 發送 GET 請求
url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization=CWA-EC120CE1-9656-4492-AA98-7AAFB831FC1F&downloadType=WEB&format=JSON"
response = requests.get(url)

with open("datapage.html", "w", encoding="utf-8") as file:
    file.write(response.text)

save = {
    "北部地區": [],
    "中部地區": [],
    "南部地區": [],
    "東北部地區": [],
    "東部地區": [],
    "東南部地區": [],
}

# 爬蟲
def get_data():

    url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization=CWA-EC120CE1-9656-4492-AA98-7AAFB831FC1F&downloadType=WEB&format=JSON"
    params = {
        "Authorization": "CWA-EC120CE1-9656-4492-AA98-7AAFB831FC1F",
        "locationName": "臺中市",
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = json.loads(response.text)
        for area in range(6):
            location = data["cwaopendata"]["resources"]['resource']["data"]['agrWeatherForecasts']['weatherForecasts']['location'][area]['locationName']
            # print(data["cwaopendata"]["resources"]['resource']["data"]['agrWeatherForecasts']['weatherForecasts']['location'][area]['locationName'])
            
            Max = data["cwaopendata"]["resources"]['resource']["data"]['agrWeatherForecasts']['weatherForecasts']['location'][area]['weatherElements']['MaxT']['daily']
            min = data["cwaopendata"]["resources"]['resource']["data"]['agrWeatherForecasts']['weatherForecasts']['location'][area]['weatherElements']['MinT']['daily']
            
            
            for i in range(len(Max)):
                
                # print(f'Day {i+1}: {Max[i]["dataDate"]} Max Temp: {Max[i]["temperature"]} min Temp: {min[i]["temperature"]}')
                entry = {
                "date": Max[i]["dataDate"],
                "maxTemp": Max[i]["temperature"],
                "minTemp": min[i]["temperature"]
                }
            
                save[location].append(entry)
    # print(save)

    # 存到DB
    # 連接SQLite 
    conn = sqlite3.connect('weather_data.db')
    c = conn.cursor()

    # 建立table
    c.execute('''CREATE TABLE IF NOT EXISTS weather_forecast 
                (id INTEGER PRIMARY KEY,
                locationName TEXT,
                dataDate TEXT,
                maxTemperature REAL,
                minTemperature REAL)''')

    # loop處理
    for area in range(6):
        location_name = data["cwaopendata"]["resources"]['resource']["data"]['agrWeatherForecasts']['weatherForecasts']['location'][area]['locationName']
        Max = data["cwaopendata"]["resources"]['resource']["data"]['agrWeatherForecasts']['weatherForecasts']['location'][area]['weatherElements']['MaxT']['daily']
        min = data["cwaopendata"]["resources"]['resource']["data"]['agrWeatherForecasts']['weatherForecasts']['location'][area]['weatherElements']['MinT']['daily']
        
        # 每個地區各7天(未來一周)
        for i in range(len(Max)):
            data_date = Max[i]["dataDate"]
            max_temp = Max[i]["temperature"]
            min_temp = min[i]["temperature"]
            
            # insert DB
            c.execute('''INSERT INTO weather_forecast (locationName, dataDate, maxTemperature, minTemperature) 
                        VALUES (?, ?, ?, ?)''', (location_name, data_date, max_temp, min_temp))

    # 提交並關閉
    conn.commit()
    conn.close()

get_data()