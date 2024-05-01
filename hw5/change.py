import json

# 讀取 JSON 文檔
with open('test.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# 將 JSON 資料轉換成 IPython Notebook 格式
notebook = {
    "cells": json_data["cells"],
    "metadata": json_data["metadata"],
    "nbformat": json_data["nbformat"],
    "nbformat_minor": json_data["nbformat_minor"]
}

# 將轉換後的內容寫入新的 .ipynb 檔案
with open('example.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f)
