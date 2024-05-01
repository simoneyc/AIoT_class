import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
movie_info= {'電影名稱':[],'類型':[],'國家':[],'時長':[],'上映時間':[],'分數':[]}

# header = {'Referer':'https://ssr1.scrape.center/',
#           'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}

# response = requests.get('https://p0.meituan.net/movie/ce4da3e03e655b5b88ed31b5cd7896cf62472.jpg@464w_644h_1e_1c',headers=header)
# print(response.content)
# with open('test.jpg','wb') as f:
#     f.write(response.content)


header = {'Referer':'https://scrape.center/',
          'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}

for page in range(1,11):

    response = requests.get('https://ssr1.scrape.center/page/%d' % page,headers=header)

    soup = BeautifulSoup(response.text,'html.parser')
    result = soup.find_all(name='div',class_='el-card item m-t is-hover-shadow')

    for i in range(len(result)):


        # print(result)
        movie_info['電影名稱'].append(result[i].h2.string)
        # print(result[i].h2.string)
        
        btn_list = result[i].find_all(name='button',class_='el-button category el-button--primary el-button--mini')
        movie_type = ''
        for btn in btn_list:
            movie_type += btn.span.string + ','
        movie_info['類型'].append(movie_type)
        # for btn in btn_list:
        #     print(btn.span.string)

        info_list = result[i].find_all(name='div',class_='m-v-sm info')
        span_list = info_list[0].find_all(name='span')

        # if '中国台湾' in span_list[0].string:
        #     span_list[0].string.replace('中国台湾','台湾')
        span_list[0].string = re.sub(r'中国台湾', '台湾', span_list[0].string)
        movie_info['國家'].append(span_list[0].string)
        movie_info['時長'].append(span_list[2].string)
        span_list = info_list[1].find_all(name='span')
        if len(span_list) > 0:
            movie_info['上映時間'].append(span_list[0].string)
        else:
            movie_info['上映時間'].append('')
        # for info in info_list:
        #     span_list = info.find_all(name='span')
        #     for s in span_list:
        #         if s.string != ' / ':
        #             print(s.string)

        score = soup.find_all(name='p',class_='score m-t-md m-b-n-sm')
        movie_info['分數'].append(score[i].string.strip())
        # print(score[i].string.strip())
        # print('--'*10)
        # https://ssr1.scrape.center/page/2
        # https://ssr1.scrape.center/page/3
# print(movie_info)
data = pd.DataFrame(movie_info)
# print(data)
data.to_excel('./movieinfo.xlsx',index=False)
