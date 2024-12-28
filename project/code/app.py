from flask import Flask, request, abort
import os
from pymongo import MongoClient, UpdateOne
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import requests
from bs4 import BeautifulSoup
import random


app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 全局變數來保存用戶的區域選擇
user_region = {}
user_category = {}
new_data = {}
user_chat_status = {}
now = ""
user_scores = {}
question_index = {}
user_answers = {}
game_data = {}

# 定義台中市區域列表
taichung_regions = [
    '南區', '北區', '中區', '西區', '東區', '北屯區', '大里區', '烏日區',
    '南屯區', '西屯區', '大雅區', '豐原區', '潭子區'
]

def create_quick_reply_buttons():
    items = [
        QuickReplyButton(action=PostbackAction(label=region, data=f'region={region}'))
        for region in taichung_regions
    ]
    return QuickReply(items=items)

# 連接到 MongoDB Atlas
def get_database(dbname):
    CONNECTION_STRING = "mongodb+srv://r0980040:nuToa9PunCm65tgH@cluster0.wpk1rjx.mongodb.net/traveling"
    client = MongoClient(CONNECTION_STRING)
    return client[dbname]

# 從資料庫中獲取隨機的項目
def get_random_items_from_db(category, region):
    db = get_database(category)
    collection = db[region]
    random_items = collection.aggregate([{'$sample': {'size': 3}}])
    return list(random_items)
    
# 從資料庫中獲取前三高評分的項目
def get_top_rated_items_from_db(category, region):
    db = get_database(category)
    collection = db[region]
    top_items = collection.find().sort('Star', -1).limit(3)
    return list(top_items)

def create_flex_message(data):
    bubbles = []
    for item in data:
        title = item.get("Title", "無標題")
        phone = item.get("Phone", "無電話")
        address = item.get("Address", "無地址")
        business_hours = item.get("Business Hours", "無營業時間")
        google_maps_link = item.get("Google Maps Link", "https://maps.google.com")
        star = item.get("Star", "0.0")
        image_link = item.get("Image Link", "")

        # 確認電話號碼格式是否有效
        phone_text = TextComponent(text=f"電話：{phone}", wrap=True)
        if phone != "無電話" and phone != "no phone":
            phone_text = TextComponent(
                text=f"電話：{phone}",
                wrap=True,
                action=URIAction(uri=f"tel:{phone}")
            )

        # 確認 Google Maps Link 是否有效
        if not google_maps_link.startswith("http"):
            google_maps_link = "https://maps.google.com"

        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url=image_link,
                size='full',
                aspect_ratio='16:9',
                aspect_mode='cover'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=title, weight='bold', size='lg'),
                    BoxComponent(layout='vertical', margin='lg', spacing='sm', contents=[
                        phone_text,
                        TextComponent(text=f"地址：{address}", wrap=True),
                        TextComponent(text=f"評分：{star}", wrap=True),
                        TextComponent(text=f"營業時間：{business_hours}", wrap=True),
                        ButtonComponent(
                            style='link',
                            height='sm',
                            action=URIAction(label='查看地圖', uri=google_maps_link)
                        ),
                        BoxComponent(
                            layout='horizontal',
                            spacing='sm',
                            contents=[
                                ButtonComponent(
                                    style='primary',
                                    color='#FF0000',
                                    height='sm',
                                    action=PostbackAction(label='1', data=f'rating=1&title={title}')
                                ),
                                ButtonComponent(
                                    style='primary',
                                    color='#FF7F00',
                                    height='sm',
                                    action=PostbackAction(label='2', data=f'rating=2&title={title}')
                                ),
                                ButtonComponent(
                                    style='primary',
                                    color='#FFFF00',
                                    height='sm',
                                    action=PostbackAction(label='3', data=f'rating=3&title={title}')
                                ),
                                ButtonComponent(
                                    style='primary',
                                    color='#7FFF00',
                                    height='sm',
                                    action=PostbackAction(label='4', data=f'rating=4&title={title}')
                                ),
                                ButtonComponent(
                                    style='primary',
                                    color='#00FF00',
                                    height='sm',
                                    action=PostbackAction(label='5', data=f'rating=5&title={title}')
                                )
                            ]
                        )
                    ])
                ]
            )
        )
        bubbles.append(bubble)

    return FlexSendMessage(alt_text="想選嗎都給你選", contents=CarouselContainer(contents=bubbles))

def get_weather_info(region):
    url = f"https://weather.yam.com/{region}/臺中"
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        weather_info = {}

        img_tag = soup.find('div', class_='Wpic').find('img')
        if img_tag:
            img_url = img_tag['src']
            full_img_url = requests.compat.urljoin(url, img_url)
            weather_info['img'] = full_img_url
        else:
            print('未找到圖片標籤')

        detail_section = soup.find('div', class_='detail')
        if detail_section:
            for p in detail_section.find_all('p'):
                text = p.text.strip()
                if "體感溫度" in text:
                    weather_info['feels_like'] = text.split(":")[1].strip()
                elif "降雨機率" in text:
                    weather_info['rain_probability'] = text.split(":")[1].strip()
                elif "紫外線" in text:
                    weather_info['uv_index'] = text.split(":")[1].strip()
                elif "空氣品質" in text:
                    weather_info['air_quality'] = text.split(":")[1].strip()
        return weather_info
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def get_game_questions():
    db = get_database("遊戲")
    collection = db["臺中知識王"]
    questions = list(collection.aggregate([{'$sample': {'size': 5}}]))
    return questions


def create_game_question_message(question_data, index):
    question_text = question_data['Question']
    options = [question_data['A'], question_data['B'], question_data['C'], question_data['D']]
    random.shuffle(options)

    buttons = [
        PostbackAction(label=options[i], data=f'game_answer={index}&choice={options[i]}')
        for i in range(4)
    ]

    return TemplateSendMessage(
        alt_text='臺中知識王問題',
        template=ButtonsTemplate(
            title=f'問題 {index + 1}',
            text=question_text,
            actions=buttons
        )
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_input = event.message.text
    global now, new_data
    if user_input == "驚喜":
        now = "驚喜"
        reply_message = TextSendMessage(
            text='請選擇您的所在區域',
            quick_reply=create_quick_reply_buttons()
        )
        line_bot_api.reply_message(event.reply_token, reply_message)
    elif user_input == "推薦":
        now = "推薦"
        reply_message = TextSendMessage(
            text='請選擇您的所在區域',
            quick_reply=create_quick_reply_buttons()
        )
        line_bot_api.reply_message(event.reply_token, reply_message)
    elif user_input == "新增":
        now = "新增"
        reply_message = TextSendMessage(text='請輸入項目標題')
        line_bot_api.reply_message(event.reply_token, reply_message)
    elif now == "新增" and user_input:
        # 保存用戶輸入的標題
        new_data[user_id] = {"Title": user_input}
        reply_message = TextSendMessage(
            text='請為項目評分',
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=PostbackAction(label=str(i), data=f'new_rating={i}')) for i in range(1, 6)
            ])
        )
        line_bot_api.reply_message(event.reply_token, reply_message)
        now = ""
    elif user_input == "知識王":
        questions = get_game_questions()
        game_data[user_id] = questions
        user_scores[user_id] = 0
        question_index[user_id] = 0
        user_answers[user_id] = []
        
        first_question = create_game_question_message(questions[0], 0)
        line_bot_api.reply_message(event.reply_token, first_question)
    elif user_input in ["美食", "點心", "景點"]:
        region = user_region.get(user_id)
        user_category[user_id] = user_input
        if region:
            if user_input == "景點":
                # 獲取天氣資訊
                weather_info = get_weather_info(region)
                if weather_info:
                    flex_message = FlexSendMessage(
                        alt_text="天氣資訊",
                        contents={
                            "type": "bubble",
                            "body": {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "flex": 5,
                                        "contents": [
                                            {"type": "text", "text": f"{region}目前天氣狀況：", "weight": "bold", "size": "md", "wrap": True},
                                            {"type": "text", "text": f"體感溫度：{weather_info.get('feels_like', 'N/A')}", "wrap": True, "size": "sm"},
                                            {"type": "text", "text": f"降雨機率：{weather_info.get('rain_probability', 'N/A')}", "wrap": True, "size": "sm"},
                                            {"type": "text", "text": f"紫外線：{weather_info.get('uv_index', 'N/A')}", "wrap": True, "size": "sm"},
                                            {"type": "text", "text": f"空氣品質：{weather_info.get('air_quality', 'N/A')}", "wrap": True, "size": "sm"}
                                        ]
                                    },
                                    {
                                        "type": "image",
                                        "url": weather_info.get("img"),
                                        "size": "md",
                                        "aspect_ratio": "4:3",
                                        "aspect_mode": "fit",
                                        "flex": 3
                                    }
                                ]
                            }
                        }
                    )
                    line_bot_api.reply_message(event.reply_token, flex_message)
                    # 景點推薦的 Flex Message
                    if now == "驚喜":
                        items = get_random_items_from_db(user_input, region)
                    elif now == "推薦":
                        items = get_top_rated_items_from_db(user_input, region)
                    spots_flex_message = create_flex_message(items)
                    line_bot_api.push_message(user_id, spots_flex_message)
                else:
                    reply_message = TextSendMessage(text="無法獲取天氣資訊")
                    line_bot_api.reply_message(event.reply_token, reply_message)
            else:
                # 從資料庫中獲取資料
                if now == "驚喜":
                    items = get_random_items_from_db(user_input, region)
                elif now == "推薦":
                    items = get_top_rated_items_from_db(user_input, region)
                reply_message = create_flex_message(items)
                line_bot_api.reply_message(event.reply_token, reply_message)
        else:
            reply_message = TextSendMessage(text="請先選擇您的所在區域")
            line_bot_api.reply_message(event.reply_token, reply_message)
    else:
        reply_message = TextSendMessage(text="請輸入 '驚喜' 或 '推薦' 來選擇您的所在區域")
        line_bot_api.reply_message(event.reply_token, reply_message)
        
def send_to_specific_user(data):
    specific_user_id = 'Ueb0d6dea2a95c12fdf716b078d624834'  # 替換為特定用戶的ID
    title = data.get("Title", "無標題")
    star = data.get("Star", "無評分")
    
    message = TextSendMessage(text=f"新增項目：\n標題：{title}\n評分：{star}")
    line_bot_api.push_message(specific_user_id, message)

def send_to_specific_user2(category, region, title, rating):
    specific_user_id = 'Ueb0d6dea2a95c12fdf716b078d624834'  # 替換為特定用戶的ID

    
    message = TextSendMessage(text=f"新增評分：\n類別:{category}\n區域:{region}\n標題：{title}\n評分：{rating}")
    line_bot_api.push_message(specific_user_id, message)

@handler.add(PostbackEvent)
@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    user_id = event.source.user_id

    if data.startswith('region='):
        region = data.split('=')[1]
        user_region[user_id] = region
        
        reply_message = TemplateSendMessage(
            alt_text='請選擇類別',
            template=ButtonsTemplate(
                title='請選擇服務項目',
                text='請選擇您要找的是美食、點心還是景點',
                actions=[
                    MessageAction(label='美食', text='美食'),
                    MessageAction(label='點心', text='點心'),
                    MessageAction(label='景點', text='景點')
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, reply_message)

    elif data.startswith('rating='):
        rating = data.split('&')[0].split('=')[1]
        title = data.split('&')[1].split('=')[1]
        # 處理評分邏輯，例如更新數據庫中的評分
        handle_rating(user_id, title, rating)
        reply_message = TextSendMessage(text=f"感謝您的評分！您給了 {title} {rating} 分。")
        line_bot_api.reply_message(event.reply_token, reply_message)
    elif data.startswith('new_rating='):
        rating = data.split('=')[1]
        if user_id in new_data:
            new_data[user_id]["Star"] = rating
            send_to_specific_user(new_data[user_id])
            reply_message = TextSendMessage(text=f"已收到您的新增項目：{new_data[user_id]['Title']}，評分：{rating}，感謝你的推薦!等待後臺更新資料")
            line_bot_api.reply_message(event.reply_token, reply_message)
        else:
            reply_message = TextSendMessage(text="出現錯誤，請重新嘗試新增。")
            line_bot_api.reply_message(event.reply_token, reply_message)
    elif data.startswith('game_answer='):
        index, choice = data.split('&')
        index = int(index.split('=')[1])
        choice = choice.split('=')[1]
        user_id = event.source.user_id
        correct_answer = game_data[user_id][index]['Answer']

        if choice == correct_answer:
            user_scores[user_id] += 1

        user_answers[user_id].append(choice)
        
        # 發送選擇的答案
        choice_message = TextSendMessage(text=f"你選擇了: {choice}\n答案是:{correct_answer}")
        line_bot_api.reply_message(event.reply_token, choice_message)
        
        if index + 1 < len(game_data[user_id]):
            next_question = create_game_question_message(game_data[user_id][index + 1], index + 1)
            line_bot_api.push_message(user_id, next_question)
        else:
            final_score = user_scores[user_id] * 20
            total_questions = len(game_data[user_id])
            if final_score == 0:
                score_message = f"遊戲結束！你的最終得分是 {final_score}\n太誇張了吧。"
            elif final_score == 20 or final_score == 40:
                score_message = f"遊戲結束！你的最終得分是 {final_score}\n可以多來台中旅遊。"
            elif final_score == 60 or final_score == 80:
                score_message = f"遊戲結束！你的最終得分是 {final_score}\n離成為台中地頭蛇更進一步。"
            elif final_score == 100:
                score_message = f"遊戲結束！你的最終得分是 {final_score}\n好厲害!不愧是臺中地頭蛇。"
            else:
                score_message = f"遊戲結束！你的最終得分是 {final_score}"
            line_bot_api.push_message(user_id, TextSendMessage(text=score_message))

        
def handle_rating(user_id, title, rating):

    # 獲取用戶選擇的分類和區域
    category = user_category.get(user_id)
    region = user_region.get(user_id)
    
    # 連接到數據庫
    db = get_database(category)
    # 查找符合條件的文檔
    collection = db[region]
    
    if category and region:

        item = collection.find_one({"Title": title})

        if item:
            send_to_specific_user2(category, region, title, rating)
            # 確保 Count 是整數
            count = item.get('Count', 1)

            # 確保 Star 是浮點數
            current_star = item.get('Star', 0.0)

            # 計算新的評分
            new_count = count + 1
            new_star = (current_star * count + float(rating)) / new_count
            new_star = round(new_star, 1)
            
            # 更新數據庫中的評分和計數
            collection.update_one(
                {"Title": title},
                {"$set": {"Star": new_star, "Count": new_count}}
            )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
