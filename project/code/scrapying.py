import requests
from bs4 import BeautifulSoup
import csv

# 爬取資訊並寫入CSV的函數
def scrape_to_csv(base_url, theme, total_pages, writer):
    for page in range(1, total_pages + 1):
        url = f'{base_url}/zh-tw/shop/consumelist?theme={theme}&sortby=Random&page={page}'
        
        # 發送GET請求到目標URL
        response = requests.get(url)
        response.encoding = 'utf-8'

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到所有資訊卡
        info_cards = soup.select('.info-card-list .item')
        
        # 爬取每個資訊卡的詳細內容
        for card in info_cards:
            link = card.find('a', href=True)
            if link:
                detail_url = base_url + link['href']
                
                # 發送GET請求到詳細頁面
                detail_response = requests.get(detail_url)
                detail_response.encoding = 'utf-8'
                
                # 使用BeautifulSoup解析詳細頁面的HTML
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                title = detail_soup.find('h2').get_text() if detail_soup.find('h2') else 'No Title'
                
                # 找到class為"d-flex flex-column w-100 px-2 pt-2 fz-14px bg-light"的容器
                detail_container = detail_soup.find('div', class_='d-flex flex-column w-100 px-2 pt-2 fz-14px bg-light')
                phone = detail_container.find('span', string='電話').next_sibling.strip() if detail_container.find('span', string='電話') else 'No Phone'
                address = detail_container.find('span', string='地址').next_sibling.strip() if detail_container.find('span', string='地址') else 'No Address'
                
                # 找到營業時間信息
                business_hours = detail_soup.find('p', class_='mb-12px mb-0-last').get_text() if detail_soup.find('p', class_='mb-12px mb-0-last') else 'No Business Hours'
                
                # 找到Google Maps連結
                google_maps_link = detail_soup.find('a', href=True, class_="btn h-5 fz-15px fz-md-16px")
                google_maps_url = google_maps_link['href'] if google_maps_link else ''
                
                # 圖片
                image_tag = detail_soup.find('div', class_='thumb-frame').find('img')
                image_link = base_url + image_tag['data-src'] if image_tag and image_tag.has_attr('data-src') else (base_url + image_tag['src'] if image_tag and image_tag.has_attr('src') else 'No Image')

                # 寫入CSV檔案
                writer.writerow({'Title': title, 'Phone': phone, 'Address': address, 'Business Hours': business_hours, 'Google Maps Link': google_maps_url, 'Image Link': image_link})

# 定義要爬取的網站參數
websites = [
    {'base_url': 'https://travel.taichung.gov.tw', 'theme': 'night-market-snacks', 'total_pages': 5},
    {'base_url': 'https://travel.taichung.gov.tw', 'theme': 'scenic-restaurants', 'total_pages': 3},
    {'base_url': 'https://travel.taichung.gov.tw', 'theme': 'bbq', 'total_pages': 2},
    {'base_url': 'https://travel.taichung.gov.tw', 'theme': 'exotic-cuisine', 'total_pages': 5},
    {'base_url': 'https://travel.taichung.gov.tw', 'theme': 'hinese-food', 'total_pages': 5},
    {'base_url': 'https://travel.taichung.gov.tw', 'theme': 'vegetarian-food', 'total_pages': 2}
]

# CSV檔案名稱
csv_file_name = 'image.csv'

# 開啟CSV檔案，寫入標題
with open(csv_file_name, mode='w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['Title', 'Phone', 'Address', 'Business Hours', 'Google Maps Link', 'Image Link']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # 迴圈遍歷每個網站進行爬取
    for site in websites:
        scrape_to_csv(site['base_url'], site['theme'], site['total_pages'], writer)
