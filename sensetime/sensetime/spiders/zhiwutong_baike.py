import hashlib
import time
from io import BytesIO
import requests
import scrapy
from PIL import Image
from bs4 import BeautifulSoup, NavigableString
from scrapy import Request, Selector

from ..items import ZhiWuBaiKE


class ZhiwutongBaikeSpider(scrapy.Spider):
    name = "zhiwutong-baike"
    allowed_domains = ["www.zhiwutong.com"]

    start_urls = ["https://www.zhiwutong.com/daohang/families_pinyin.htm"]

    def parse(self, response, **kwargs):
        sel = Selector(response)
        # 提取
        urls = [url for url in sel.re(r'/(.*?)(?=";)')[1:] if "families2" not in url]
        for url in urls:
            yield Request(
                "https://www.zhiwutong.com/" + url,
                callback=self.filter_page,
            )

    def filter_page(self, response, **kwargs):
        html = response.text
        f_sel = Selector(response)
        zhiwu_item = ZhiWuBaiKE()
        zhiwu_item["title"] = (
            f_sel.css("title::text").extract_first().replace("_植物通", "")
        )
        zhiwu_item["data_source"] = "植物通"
        zhiwu_item["data_url"] = response.url
        zhiwu_item["crawler_tm"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        zhiwu_item["track_id"] = hashlib.md5(response.url.encode()).hexdigest()
        zhiwu_item["category"] = ["物种数据库"]
        content, img_list, html = self.filter_content(html)
        zhiwu_item["content_html"] = html
        zhiwu_item["content"] = content
        zhiwu_item["img_list"] = img_list
        if len(zhiwu_item["content"]) == 0:
            yield ""
        else:
            yield zhiwu_item
        href_list = f_sel.css('div[class="article art"]>a::attr(href)').extract()
        if len(href_list) != 0:
            for href in href_list:
                if "pdf" not in href:
                    yield Request(
                        "https://www.zhiwutong.com/" + href, callback=self.filter_page
                    )

    def filter_content(self, html):
        soup = BeautifulSoup(html, "lxml")
        img_list = {}
        content = ""
        img_index = 0
        for element in soup.find_all("div", class_="article art"):
            for child in element.children:
                if child.name == "a" and content[-1] != "：":
                    content = content[:-1]
                if child.name == "br":
                    content += "\n "
                else:
                    r, img_dict, img_index = self.process_tag(
                        child, img_index=img_index
                    )
                    if len(r) <= 3:
                        content = content[:-1] + r
                    else:
                        content = content + r
                    if img_dict:
                        img_list.update(img_dict)
        return (
            content.replace(".article strong {font-weight:bold;}", ""),
            img_list,
            html,
        )

    def process_tag(self, tag, img_index, depth=0):
        result = ""
        img_dict = {}
        if tag.name == "img":
            img_url = tag.get("src")
            filename = hashlib.sha256(img_url.encode()).hexdigest()
            img_dict_test = self.download_image(img_url, filename + ".jpg")
            if img_dict_test is not None:
                img_dict.update({f"img000{img_index}": img_dict_test})
                result += f"\n <$<img>$>img000{img_index}<$<\img>$> \n"
                img_index += 1
        elif isinstance(tag, str):
            result += tag.strip()
        elif tag.contents:
            for child in tag.contents:
                r, c_img_dict, img_index = self.process_tag(child, img_index, depth + 1)
                result += r
                img_dict.update(c_img_dict)
        if len(result) != 0 and result[-1] == "：" and depth == 0:
            return result, img_dict, img_index
        if depth == 0:
            result += "\n"
        return result, img_dict, img_index

    def download_image(self, url, filename):
        img_dict = dict()
        path = f"C:/Users/hayu/appen/scrapy_items/sensetime/sensetime/baike-imgs/{filename}"
        if "http" not in url:
            url = "https://www.zhiwutong.com" + url
        try:
            response = requests.get(url)
        except:
            return None
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image = image.convert("RGB")
            image.save(path)
            img_dict["img_url"] = url
            img_dict["img_path"] = f"./baike-imgs/{filename}"
            img_dict["img_description"] = ""
            image.close()
            return img_dict
        else:
            return None
