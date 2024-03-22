import requests
from bs4 import BeautifulSoup

res = requests.get('https://novelup.plus/story/206612087?p=1')
soup = BeautifulSoup(res.text, 'lxml')
