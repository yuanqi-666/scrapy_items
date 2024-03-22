import hashlib

import jieba
import requests
import random
from newspaper import fulltext
from bs4 import BeautifulSoup
import json

USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
]
headers = {
    'user-agent': random.choice(USER_AGENT_LIST)
}

all_url_md5 = []


def request_url(url, track_id=0):
    try:
        print(f"{track_id} ==> {url}")
        new_dict = {}
        response = requests.get(url=url, headers=headers)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, 'lxml')
        content = fulltext(response.text, 'zh')
        new_dict["id"] = hashlib.md5(url.encode()).hexdigest()
        if new_dict['id'] in all_url_md5:
            return ''
        all_url_md5.append(new_dict['id'])
        new_dict["content"] = content
        new_dict['token_num'] = len(list(jieba.cut(content)))
        new_dict["title"] = soup.find('h1', attrs={"class": "title-article"}).text
        print(new_dict["title"])
        new_dict["source"] = 'CSDN'
        new_dict["language"] = 'zh'
        try:
            new_dict["pub_time"] = soup.find('span', attrs={"class": "time blog-postTime"}).text
        except:
            new_dict["pub_time"] = soup.find('span', attrs={"class": "time"}).text
        new_dict["reserved"] = {
            "keywords": [i.text for i in soup.find('div', attrs={"class": "tags-box artic-tag-box"}).find_all('a')],
            "product_line": '网络与通信',
            "source_catalogue": '博客'
        }
        html = f"""
        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
    {soup.find('div', attrs={"class": "blog-content-box"}).prettify()}
</body>
</html>
        """
        with open(f'./csdn_html/{new_dict["id"]}.html', 'w', encoding='utf-8') as f:
            f.write(html)
        with open(f'./csdn.jsonl', 'a', encoding='utf-8') as f:  # 使用追加模式，避免覆盖之前的内容
            json.dump(new_dict, f, ensure_ascii=False)
            f.write('\n')  # 写入换行符，使JSON Lines格式的文件更加规范
        for i in soup.find_all('a', attrs={"class": "tit"}):
            res_url = i.get('href')
            if 'download' in res_url or 'blog.csdn' not in res_url and track_id < 2:
                continue
            request_url(res_url, track_id=track_id + 1)
    except:
        print(f'错误url {url}')


if __name__ == '__main__':
    request_url('https://blog.csdn.net/Wang_kang1/article/details/124306795')
