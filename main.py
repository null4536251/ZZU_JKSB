# -*- coding: UTF-8 -*-
import os

os.environ["http_proxy"] = "127.0.0.1:4973"
import re
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlencode

import requests
from fake_useragent import UserAgent

LOGIN_URL = 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login'
SECOND_URL = 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/first0?fun2=&door='
THIRD_URL = 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb'
username = '' #学号{填写}
password = '' #密码{填写}
ua = UserAgent(path = "fake_useragent_0.1.11.json")
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'}
header['User-Agent'] = ua.random
s = requests.Session()
data = {'uid': username, 'upw': password}
mail_user = '2248019104@qq.com'  # 发件人用户名 (我的邮箱)
mail_pass = 'grksagtpvguteagj'  # 发件人密码
receivers = ['']  # 收件人邮箱{填写}

try:
    response = s.post(LOGIN_URL, headers = header, data = data)
    response_html = str(response.content.decode('utf-8'))
    result = re.findall(r'ptopid=(.*?)&sid=(.*?)"', response_html)
    ptopid = result[0][0]
    sid = result[0][1]
    response.close()
    parameter = {'ptopid': ptopid, 'sid': sid}
    data1 = urlencode(parameter)
    response = s.post(LOGIN_URL + "?" + data1, headers = header, data = data)
    response_html = str(response.content.decode('utf-8'))
    response.close()
    url = re.findall(r'parent.window.location="(.*?)"}', response_html)[0]
    response = s.get(url, headers = header)
    response_html = str(response.content.decode('utf-8'))
    response.close()
    # print(response_html)
    url = re.findall(r'<iframe name="zzj_top_6s" id="zzj_top_6s" src="(.*?)" marginwid', response_html)[0]
    response = s.get(url, headers = header)
    response_html = str(response.content.decode('utf-8'))
    response.close()
    data2 = {}
    data2['did'] = 1
    data2['door'] = ''
    data2['men6'] = 'a'
    data2['ptopid'] = re.findall(r'<input type="hidden" name="ptopid" value="(.*?)">', response_html)[0]
    data2['sid'] = re.findall(r'<input type="hidden" name="sid" value="(.*?)>', response_html)[0]
    response = s.post(THIRD_URL, headers = header, data = data2)
    response.close()
    data3 = {
        'myvs_1': '否',
        'myvs_2': '否',
        'myvs_3': '否',
        'myvs_4': '否',
        'myvs_5': '否',
        'myvs_6': '否',
        'myvs_7': '否',
        'myvs_8': '否',
        'myvs_9': '否',
        'myvs_10': '否',
        'myvs_11': '否',
        'myvs_12': '否',
        'did': 2,
        'door': '',
        'day6': 'b',
        'men6': 'a',
        'sheng6': '',
        'shi6': '',
        'fun3': '',
        'jingdu': '113.631419',
        'weidu': '34.753439',
        'ptopid': data2['ptopid'],
        'sid': data2['sid'],
        'myvs_13': 'g',
        'myvs_13a': '41',  # 省代码
        'myvs_13b': '4101',  # 市代码
        'myvs_13c': '河南省.郑州市.中原区',
        'myvs_24': '否',
        'myvs_26': 2,
    }
    response = s.post(THIRD_URL, headers = header, data = data3)
    html = response.content.decode('utf-8')
    res = re.findall(r'(感谢你今日上报健康状况)', html)[0]
    print(res)
    if res == '':
        raise Exception("error!")
    try:
        msg = MIMEMultipart()
        conntent = "打卡提醒"
        # 把内容加进去
        msg.attach(MIMEText(conntent, 'plain', 'utf-8'))
        # 设置邮件主题
        msg['Subject'] = "打卡成功!"
        # 发送方信息
        msg['From'] = mail_user
        sml = smtplib.SMTP_SSL("smtp.qq.com", 465)
        sml.login(mail_user, mail_pass)
        sml.sendmail(mail_user, receivers, msg.as_string())
        print("打卡成功, 邮件发送成功")
    except Exception as err:
        print(err)
        print("打卡成功但是发送邮件失败")

except Exception as err:
    print(err)
    traceback.print_exc()
    print('打卡失败')
    msg = MIMEMultipart()
    conntent = "打卡提醒"
    # 把内容加进去
    msg.attach(MIMEText(conntent, 'plain', 'utf-8'))
    # 设置邮件主题
    msg['Subject'] = "打卡失败!打卡失败!打卡失败!!"
    # 发送方信息
    msg['From'] = mail_user
    sml = smtplib.SMTP_SSL("smtp.qq.com", 465)
    sml.login(mail_user, mail_pass)
    sml.sendmail(mail_user, receivers, msg.as_string())
