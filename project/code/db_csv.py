import csv, os
from pymongo import MongoClient
def get_database():
    # 提供 mongodb atlas url 以使用 pymongo 將 python 連接到 mongodb
    CONNECTION_STRING = "mongodb+srv://r0980040:nuToa9PunCm65tgH@cluster0.wpk1rjx.mongodb.net/traveling"

    # 使用 MongoClient 導入 MongoClient 或者使用 pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    return client['景點']

dbname = get_database()


files = os.listdir('景點')
    
for file in files:

    name = file.replace('_景點.csv', '')
    print(name)
    collection = dbname[name]

    # 開啟CSV檔案
    file_path = f"景點/{file}"
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        # 建立 CSV 讀取物件
        csv_reader = csv.reader(csvfile)
        
        # 提取第一列（標題列）   
        headers = next(csv_reader)
        headers[0] = headers[0].lstrip('\ufeff')

        for row in csv_reader:
            item = {}
            for i in range(len(row)):
                item[headers[i]] = row[i]
            # print(item)
            result = collection.insert_one(item)
            print("Inserted item with ID:", result.inserted_id)