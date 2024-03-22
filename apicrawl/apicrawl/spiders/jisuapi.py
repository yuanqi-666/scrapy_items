import scrapy
from bs4 import BeautifulSoup
from ..items import ApicrawlItem


class JisuapiSpider(scrapy.Spider):
    name = "jisuapi"
    allowed_domains = ["www.jisuapi.com"]
    start_urls = ["https://www.jisuapi.com/api/"]

    def parse(self, response):
        # 获取所有的类型api列表
        soup = BeautifulSoup(response.text, 'lxml')
        # 获取所有类型页面的url
        a_tags = soup.find('div', attrs={"id": "apileft"}).find_all('a')
        for a in a_tags:
            info_url = "https://www.jisuapi.com" + a.get('href')
            yield scrapy.Request(url=info_url, callback=self.filter_page_url, cb_kwargs={'to_num': 0, "page_num": 1})

    def filter_page_url(self, response, **kwargs):
        page_soup = BeautifulSoup(response.text, 'lxml')
        div_tag = page_soup.find("div", attrs={"id": "apirtitle"})
        api_list_num = int(div_tag.find('h1').find('span').text[:-1])
        if api_list_num - 20 > kwargs['to_num']:
            yield scrapy.Request(f'https://www.jisuapi.com/api/7/{kwargs["page_num"] + 1}',
                                 callback=self.filter_page_url,
                                 cb_kwargs={'to_num': 20 + kwargs['to_num'], "page_num": 1 + kwargs['page_num']})
        li_tags = page_soup.find('div', attrs={"id": "apilistbox"}).find_all('a')
        for li in li_tags:
            page_url = "https://www.jisuapi.com" + li.get('href')
            yield scrapy.Request(url=page_url, callback=self.filter_api_page)

    def filter_api_page(self, response, **kwargs):
        api_item = ApicrawlItem()
        api_list = [{
            "name": "",
            "url": "",
            "description": "",
            "method": "",
            "required_parameters": [
            ],
            "optional_parameters": [],
            "code": ""
        }]
        api_soup = BeautifulSoup(response.text, 'lxml')
        api_item['tool_name'] = api_soup.find('div', attrs={"id": "apiitop"}).find('h1').text
        api_item['tool_description'] = api_soup.find('div', attrs={"id": "apiidesc"}).text
        api_item['url'] = response.url

        api_list[0]['name'] = api_soup.find('div', attrs={"id": "apiitop"}).find('h1').text
        api_list[0]['url'] = api_soup.find_all('div', attrs={"class": "apiline"})[0].find('span').text
        api_list[0]['description'] = api_soup.find('div', attrs={"id": "apiidesc"}).text
        api_list[0]['method'] = api_soup.find_all('div', attrs={"class": "apiline"})[2].find('span').text
        tr_tags = api_soup.find('div', attrs={"class": "apilinebox"}).find('table').find_all('tr')
        required_parameters = []
        if tr_tags != None and len(tr_tags) != 1:
            for tr in tr_tags[1:]:
                tr_dict = {}
                tr_dict["name"] = tr.find_all('td')[0].text
                tr_dict["type"] = tr.find_all('td')[1].text
                tr_dict["description"] = tr.find_all('td')[3].text
                tr_dict["default"] = ""
                required_parameters.append(tr_dict)
        else:
            required_parameters.append({})

        api_list[0]['required_parameters'] = required_parameters
        try:
            content = ''
            for i in api_soup.find('pre', attrs={"class": "brush:python;"}).getText().splitlines():
                content += i + '\n'
            api_list[0]['code'] = content
        except:
            api_list[0]['code'] = ''
        api_item['api_list'] = api_list
        yield api_item
