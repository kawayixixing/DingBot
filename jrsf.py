# 获取每天的今日说法，并取得相关链接。
from selenium import webdriver
from lxml import etree
import requests
from lxml import etree
import json
import hashlib
import base64
import hmac
import os
import time
from urllib.parse import quote_plus

# 钉钉机器人类
class Messenger:

    def __init__(self, token=None, secret=None):
        self.timestamp = str(round(time.time() * 1000))
        self.URL = 'https://oapi.dingtalk.com/robot/send'
        self.headers = {'Content-Type': 'application/json'}
        self.token = token or os.getenv('DD_ACCESS_TOKEN')
        self.secret = secret or os.getenv('DD_SECRET')
        self.sign = self.generate_sign()
        self.params = {'access_token': self.token, 'sign': self.sign}

    def generate_sign(self):
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(self.timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        return quote_plus(base64.b64encode(hmac_code))   
    # md
    def send_md(self, title, text):
        data = {
            'msgtype': 'markdown',
            'markdown': {
                'title': title, 
                'text': text}
        }
        self.params['timestamp'] = self.timestamp
        return requests.post(
            url=self.URL,
            data=json.dumps(data),
            params=self.params,
            headers=self.headers
        )


url = "https://tv.cctv.com/lm/jrsf/"

# 配置浏览器选项
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 无界面模式，可选
options.add_argument("--disable-gpu")  # 禁用GPU加速，可选

# 启动浏览器
driver = webdriver.Chrome(options=options)

# 访问网站
driver.get(url)

# 获取动态加载的结果
dynamic_content = driver.page_source

# 使用lxml解析页面内容
html = etree.HTML(dynamic_content)

# 使用XPath提取信息
# 使用最新的今日说法
title = html.xpath('//*[@id="SUBD1455860682972942"]/div[3]/div/div[3]/div/ul/li[1]/div[2]/p/a/@title')
link = html.xpath('//*[@id="SUBD1455860682972942"]/div[3]/div/div[3]/div/ul/li[1]/div[2]/p/a/@href')

# 完整版视频链接
whmole_link = '[视频链接]({})'.format(link[0])   

# 访问第一条视频
response = requests.get(link[0])
response.encoding = 'utf-8'
if response.status_code == 200:
    html = response.text

    # 使用lxml解析HTML
    tree = etree.HTML(html)
    
    # 假设要提取正文内容
    content = tree.xpath('/html/head/meta[5]/@content')
    # print("内容简介：", content)
else:
    print('请求失败，状态码：', response.status_code)

m = Messenger(
    token='哈里',
    secret='路亚'
)

title = title[0]
text = content[0] + ''.join(whmole_link)
m.send_md(title, text)

# 关闭浏览器
driver.quit()
