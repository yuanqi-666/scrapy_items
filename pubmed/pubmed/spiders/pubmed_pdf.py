import hashlib
import urllib.parse
from typing import Iterable
import requests
import scrapy
from bs4 import BeautifulSoup
from scrapy import Request
from pubmed.items import PubmedItem
from datetime import datetime, timedelta


def get_first_and_last_day_of_each_month(year):
    result = []
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    for month in range(1, 13):
        if year < current_year or (year == current_year and month < current_month):
            first_day = datetime(year, month, 1)
            if month == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month + 1
                next_year = year
            last_day = datetime(next_year, next_month, 1) - timedelta(days=1)
            result.append((first_day, last_day))
    return result


def format_date_range(date_range):
    start_date = date_range[0].strftime("%Y/%m/%d")
    end_date = date_range[1].strftime("%Y/%m/%d")
    return f"{start_date}-{end_date}"


class PubmedPdfSpider(scrapy.Spider):
    name = "pubmed-pdf"
    allowed_domains = ["pubmed.ncbi.nlm.nih.gov"]
    url = "https://pubmed.ncbi.nlm.nih.gov/"
    year = [2022, 2021]

    # start_urls = ["https://pubmed.ncbi.nlm.nih.gov"]
    def start_requests(self) -> Iterable[Request]:
        for year in self.year:
            date_ranges = get_first_and_last_day_of_each_month(year)
            formatted_ranges = [
                format_date_range(date_range) for date_range in date_ranges
            ]
            for formatted_range in formatted_ranges:
                params = {
                    "term": "covid 19",
                    "filter": [
                        "simsearch2.ffrft",
                        f"dates.{formatted_range}",
                        "lang.english",
                    ],
                    "sort": "pubdate",
                    "sort_order": "asc",
                    "size": "200",
                    "page": "1",
                }
                url_with_params = "{}?{}".format(
                    self.url, urllib.parse.urlencode(params, doseq=True)
                )
                yield Request(url_with_params, cb_kwargs={"item": params, "y": year})

    def parse(self, response, **kwargs):
        print(f"{kwargs['y']} --> {response.url} --> {response.status}")
        soup = BeautifulSoup(response.text, "lxml")
        page_to = soup.find("label", attrs={"class": "of-total-pages"}).text.replace(
            "of", ""
        )
        params_item = kwargs["item"]
        for t in range(1, int(page_to) + 1):
            params_item["page"] = str(t)
            url_with_params = "{}?{}".format(
                self.url, urllib.parse.urlencode(params_item, doseq=True)
            )
            yield Request(
                url_with_params,
                callback=self.download_page,
                cb_kwargs={"y": kwargs["y"]},
            )

    def download_page(self, response, **kwargs):
        # 对info页进行解析，获取所有的详情页url
        soup = BeautifulSoup(response.text, "lxml")
        article_tags = soup.find_all("article", attrs={"class": "full-docsum"})
        for article_tag in article_tags:
            pubmed_item = PubmedItem()
            page_view_url = "https://pubmed.ncbi.nlm.nih.gov/" + article_tag.find(
                "a", attrs={"class": "docsum-title"}
            ).get("href")
            pubmed_item["title"] = (
                article_tag.find("a", attrs={"class": "docsum-title"})
                .text.replace("\n", "")
                .strip()
            )
            pubmed_item["id"] = hashlib.md5(page_view_url.encode()).hexdigest()
            pubmed_item["author"] = (
                article_tag.find("span", attrs={"class": "docsum-authors full-authors"})
                .text.replace("\n", "")
                .strip()
            )
            pubmed_item["intro"] = article_tag.find(
                "div", attrs={"class": "full-view-snippet"}
            ).text
            pubmed_item["xueke"] = "医学-mammary"
            yield Request(
                url=page_view_url,
                cb_kwargs={"item": pubmed_item, "y": kwargs["y"]},
                callback=self.page_view,
            )

    def page_view(self, response, **kwargs):
        soup = BeautifulSoup(response.text, "lxml")
        pubmeb_i = kwargs.get("item")
        try:
            pubmeb_i["create_time"] = soup.find("span", attrs={"class": "cit"}).text
        except:
            pubmeb_i["create_time"] = ""
        try:
            pubmeb_i["type"] = soup.find(
                "div", attrs={"class": "publication-type"}
            ).text
        except:
            pubmeb_i["create_time"] = ""
        try:
            pubmeb_i["doi"] = (
                soup.find("span", attrs={"class": "identifier doi"})
                .text.replace("\n", "")
                .replace(" ", "")
            )
        except:
            pubmeb_i["doi"] = ""

        link_list = []
        a_tags = soup.find("div", attrs={"class": "full-text-links-list"}).find_all("a")
        for a in a_tags:
            title = a.get("data-ga-action")
            if title == "PMC":
                down_url = a.get("href")
                link_list.append({title: down_url})
                cookies = {
                    "ncbi_sid": "6F5C3BF35A4A2A73_1998SID",
                    "pmc-frontend-csrftoken": "I9o4TNnaL8yb8HTkVK4p1eGbN4KxUzDy",
                    "_ce.s": "v~1745283c4f5386fb8f284a53a36145a02f1079e5~lcw~1705996256046~lva~1705996256046~vpv~0~lcw~1705996256046",
                    "_ga": "GA1.4.1438227569.1705289726",
                    "books.article.report": "",
                    "_gid": "GA1.2.1927024768.1710915618",
                    "_gid": "GA1.4.1927024768.1710915618",
                    "_gat_ncbiSg": "1",
                    "_gat_dap": "1",
                    "_ga_DP2X732JSX": "GS1.1.1710923969.24.1.1710928043.0.0.0",
                    "_ga": "GA1.1.1438227569.1705289726",
                    "_gat_GSA_ENOR0": "1",
                    "_ga_CSLL4ZEK4L": "GS1.1.1710923968.15.1.1710928043.0.0.0",
                    "ncbi_pinger": "N4IgDgTgpgbg+mAFgSwCYgFwgJwGZsBCuAggBwAM5AwgOwCMulArJZQCxV1MAiLB13OgDphAWzgAmEABoQAVwB2AGwD2AQ1QKoADwAumUFKxhRAYwC0AMwgqFuqAvSzcmcGZkg2rtRF3JTSlAeTK4A9D5+AVAAzqEACgCyVKRspNhMpLihHnReWNC6EMiwUE4gEuSueIQkFNT0jOQsrBxcvOT8VIIiQuJSshJ0riYW1rb2jhgjGBH+gRjhvnMx8UkpaRlZHhJGIADuB0IKpgBGyEdKokfIiEIA5iow29iudNgVHoyv5BSfQ1hvD7OXZ0chsSrOFxYSxqJTRILOPIgQpyBEgXCkVyfF5YJi4NguWTg1w0ABsdH6nihIHIQnwdI8bCRilUGi0ekZISwEJAeNe7x5TCR2DewVJrkFNAlHnJJJoUgAvgqgA=",
                }

                headers = {
                    "authority": "www.ncbi.nlm.nih.gov",
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "accept-language": "zh-CN,zh;q=0.9",
                    "cache-control": "max-age=0",
                    # 'cookie': 'ncbi_sid=6F5C3BF35A4A2A73_1998SID; pmc-frontend-csrftoken=I9o4TNnaL8yb8HTkVK4p1eGbN4KxUzDy; _ce.s=v~1745283c4f5386fb8f284a53a36145a02f1079e5~lcw~1705996256046~lva~1705996256046~vpv~0~lcw~1705996256046; _ga=GA1.4.1438227569.1705289726; books.article.report=; _gid=GA1.2.1927024768.1710915618; _gid=GA1.4.1927024768.1710915618; _gat_ncbiSg=1; _gat_dap=1; _ga_DP2X732JSX=GS1.1.1710923969.24.1.1710928043.0.0.0; _ga=GA1.1.1438227569.1705289726; _gat_GSA_ENOR0=1; _ga_CSLL4ZEK4L=GS1.1.1710923968.15.1.1710928043.0.0.0; ncbi_pinger=N4IgDgTgpgbg+mAFgSwCYgFwgJwGZsBCuAggBwAM5AwgOwCMulArJZQCxV1MAiLB13OgDphAWzgAmEABoQAVwB2AGwD2AQ1QKoADwAumUFKxhRAYwC0AMwgqFuqAvSzcmcGZkg2rtRF3JTSlAeTK4A9D5+AVAAzqEACgCyVKRspNhMpLihHnReWNC6EMiwUE4gEuSueIQkFNT0jOQsrBxcvOT8VIIiQuJSshJ0riYW1rb2jhgjGBH+gRjhvnMx8UkpaRlZHhJGIADuB0IKpgBGyEdKokfIiEIA5iow29iudNgVHoyv5BSfQ1hvD7OXZ0chsSrOFxYSxqJTRILOPIgQpyBEgXCkVyfF5YJi4NguWTg1w0ABsdH6nihIHIQnwdI8bCRilUGi0ekZISwEJAeNe7x5TCR2DewVJrkFNAlHnJJJoUgAvgqgA=',
                    "referer": "https://pubmed.ncbi.nlm.nih.gov/",
                    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "same-site",
                    "sec-fetch-user": "?1",
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                }
                res = requests.get(
                    down_url, headers=headers, cookies=cookies, timeout=120
                )

                pdf_soup = BeautifulSoup(res.text, "lxml")
                download_link = "https://www.ncbi.nlm.nih.gov" + (
                    pdf_soup.find("li", attrs={"class": "pdf-link other_item"})
                    .find("a")
                    .get("href")
                )
                response = requests.get(
                    download_link, headers=headers, cookies=cookies, timeout=120
                )
                file_name = hashlib.md5(response.url.encode()).hexdigest()
                if response.status_code == 200:
                    # 将文件保存到本地
                    with open(
                        f"C:\\Users\\hayu\\appen\\scrapy_items\\pubmed\\pubmed\\pdf\\{file_name}.pdf",
                        "wb",
                    ) as pdf_file:
                        pdf_file.write(response.content)
                        pubmeb_i["pdf_name"] = file_name
                    yield pubmeb_i
