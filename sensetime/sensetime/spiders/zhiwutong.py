import hashlib
import time
from io import BytesIO
from typing import Iterable

import requests
import scrapy
from PIL import Image
from bs4 import BeautifulSoup
from scrapy import Request, Selector

from ..items import SensetimeItem


class ZhiwutongSpider(scrapy.Spider):
    name = "zhiwutong"
    allowed_domains = ["www.zhiwutong.com"]
    url_list = [
        "https://www.zhiwutong.com/keyan/keji.htm",
        "https://www.zhiwutong.com/keyan/shehui.htm",
        "https://www.zhiwutong.com/learning/gardens.htm",
        "https://www.zhiwutong.com/learning/interest.htm",
        "https://www.zhiwutong.com/learning/knowledge.htm",
        "https://www.zhiwutong.com/learning/mingci.htm",
        "https://www.zhiwutong.com/learning/why.htm",
        "https://www.zhiwutong.com/learning/rare.htm",
        "https://www.zhiwutong.com/learning/wenxue.htm",
        "https://www.zhiwutong.com/science/botanist.htm",
        "https://www.zhiwutong.com/science/evolve.htm",
        "https://www.zhiwutong.com/science/ex-situ.htm",
        "https://www.zhiwutong.com/yanghua/flower.htm",
        "https://www.zhiwutong.com/yanghua/Succuleats.htm",
        "https://www.zhiwutong.com/yanghua/arethusa.htm",
        "https://www.zhiwutong.com/yanghua/shuipei.htm",
        "https://www.zhiwutong.com/yanghua/qiehua.htm",
        "https://www.zhiwutong.com/yanghua/insect-pest.htm",
        "https://www.zhiwutong.com/yanghua/liyi.htm",
        "https://www.zhiwutong.com/yanghua/xingshang.htm",
        "https://www.zhiwutong.com/yanghua/zhuangshi.htm",
        "https://www.zhiwutong.com/yanghua/meirong.htm",
        "https://www.zhiwutong.com/yanghua/chahua.htm",
        "https://www.zhiwutong.com/yanghua/yangshen.htm",
        "https://www.zhiwutong.com/yanghua/jiajie.htm",
        "https://www.zhiwutong.com/yanghua/feiliao.htm",
        "https://www.zhiwutong.com/yanghua/zaipei.htm",
        "https://www.zhiwutong.com/yanghua/fanzhi.htm"]

    def start_requests(self) -> Iterable[Request]:
        for u in self.url_list:
            yield Request(u)

    def parse(self, response, **kwargs):
        sel = Selector(response)
        next_url = "https://" + sel.css('a[class="next_min"]::attr(href)').extract_first()[2:]
        if next_url != response.url:
            yield Request(next_url, callback=self.parse)
        li_tags = sel.css('ul[class="list05"]>li')

        for li in li_tags:
            sense_item = SensetimeItem()
            url = li.css('a::attr("href")').extract_first()[2:]
            track_id = hashlib.md5(url.encode()).hexdigest()
            sense_item["title"] = li.css('a::text').extract_first()
            sense_item["publish_time"] = li.css('span::text').extract_first()
            sense_item["data_url"] = "https://" + url
            sense_item["data_source"] = '植物通'
            sense_item["track_id"] = track_id
            sense_item["crawler_tm"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            yield Request("https://" + url, callback=self.parse_page, cb_kwargs={"item": sense_item.copy()})

    def parse_page(self, response, **kwargs):
        print(f"{response.url} -- 开始")
        sense_time = kwargs["item"]
        html = response.text
        sel = Selector(response)
        category = sel.css('div[class="bread"]>span>a::text').extract()
        author_elements = sel.css('div[class="articleAuthor"]>span::text').extract()
        author = ''
        source = ''
        for i in author_elements:
            if "来源" in i:
                source = i.replace('来源：', '')
            if '作者' in i:
                author = i.replace('作者：', '')
        sense_time["author"] = author
        sense_time["source"] = source
        if ' 首页' in category:
            category.remove(' 首页')
        sense_time["category"] = category
        content, img_list, html = self.filter_content(html)
        sense_time["content"] = content
        sense_time["content_html"] = html
        sense_time["img_list"] = img_list
        print(f"{response.url} -- 结束")
        yield sense_time

    def filter_content(self, html):
        content_html = html
        soup = BeautifulSoup(html, 'lxml')
        img_list = {}
        content = ''
        div_content_tag = soup.find('div', attrs={"class": "article art"})
        trs_edit = div_content_tag.find_all('div', attrs={"class": "TRS_Editor"})
        if len(trs_edit) != 0:
            div_content_tag = soup.find('div', attrs={"class": "TRS_Editor"})
        img_index = 0
        for i in div_content_tag.children:
            if isinstance(i, str):  # Check if the child is a string
                content += i + "\n"  # Append the text content directly
                continue  # Move to the next child
            if i.name is not None:
                if i.name == 'br':
                    content += '\n'
                img_tags = i.find_all('img')
                if len(img_tags) != 0:
                    for index, img in enumerate(img_tags):
                        img_url = img.get('src')
                        filename = hashlib.sha256(img_url.encode()).hexdigest()
                        img_dict = self.download_image(img_url, filename + ".jpg")
                        if img_dict is not None:
                            img_list[f"img000{img_index}"] = img_dict
                            content += f"\n <$<img>$>img000{img_index}<$<\img>$> \n"
                            img_index += 1
                            content_html.replace(img_url, img_dict.get('img_path', ''))
                        else:
                            continue
                content += i.text + "\n"
        return content.replace('.article strong {font-weight:bold;}', ''), img_list, html

    def download_image(self, url, filename):
        img_dict = dict()
        path = f"D:/scrapy_items/sensetime/sensetime/img/{filename}"
        try:
            response = requests.get(url, timeout=120)
        except:
            return None
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image = image.convert("RGB")
            image.save(path)
            img_dict["img_url"] = url
            img_dict["img_path"] = f'./img/{filename}'
            img_dict["img_description"] = ''
            image.close()
            return img_dict
        else:
            return None
