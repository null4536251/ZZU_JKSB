import os
import re
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent


os.environ["http_proxy"] = "127.0.0.1:4973"

LOGIN_URL = 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login'
JKSB_URL = 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb'

ua = UserAgent(path="fake_useragent_0.1.11.json")
headers = {'User-Agent': ua.random}

username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]
data = {'uid': username, 
        'upw': password
       }

sev = os.environ["SEV"]

mail_user = os.environ["MAIL_USER"]  # QQ邮箱账户
mail_pass = os.environ["MAIL_PASS"]  # QQ邮箱授权码
receivers = os.environ["RECEIVERS"]  # QQ邮箱账户

try:
    session = requests.Session()
    response = session.post(LOGIN_URL, headers=headers, data=data)

    #print(response.text)
    url = re.findall(r'location="(.*?)"', response.text)[0]
    #print('登录成功后的第一个url', url)
    response.close()

    frameUrl = url.replace('first6', 'jksb') + '&fun2='

    response = session.get(frameUrl, headers=headers)
    new_page = BeautifulSoup(response.text, "html.parser")
    div = new_page.find('div', attrs={'id': 'bak_0'})

    did = div.find('input', attrs={'name': 'did'}).get('value')
    #print('did', did)
    fun18 = div.find('input', attrs={'name': 'fun18'}).get('value')
    #print('fun18', fun18)
    door = div.find('input', attrs={'name': 'door'}).get('value')
    #print('door', door)
    sid1 = div.findAll('input', attrs={'name': 'sid'})[0].get('value')
    #print('sid1', sid1)
    men6 = div.find('input', attrs={'name': 'men6'}).get('value')
    #print('men6', men6)
    ptopid = div.find('input', attrs={'name': 'ptopid'}).get('value')
    #print('ptopid', ptopid)
    sid2 = div.findAll('input', attrs={'name': 'sid'})[1].get('value')
    #print('sid2', sid2)

    data1 = {
        'did': did,
        'door': door,
        'fun18': fun18,
        'sid': sid1,
        'men6': men6,
        'ptopid': ptopid,
        'sid': sid2
    }

    response = session.post(JKSB_URL, headers=headers, data=data1)
    response.encoding = 'utf-8'
    # print(response.text)

    data2 = {
        'myvs_1': '否',
        'myvs_2': '否',
        'myvs_3': '否',
        'myvs_4': '否',
        'myvs_5': '否',
        'myvs_7': '否',
        'myvs_8': '否',
        'myvs_9': '做了',
        'myvs_11': '否',
        'myvs_12': '否',
        'myvs_13': '否',
        'myvs_15': '否',
        'did': 2,
        'door': '',
        'day6': 'b',
        'men6': 'a',
        'sheng6': '',
        'shi6': '',
        'fun3': '',
        'fun18': fun18,
        'jingdu': '113.535663',  # 经度 TODO:注意更换
        'weidu': '34.811384',  # 维度 TODO:注意更换
        'ptopid': data1['ptopid'],
        'sid': data1['sid2'],
        'myvs_13': 'g',
        'myvs_13a': '41',  # 省代码 TODO:注意更换
        'myvs_13b': '4101',  # 市代码 TODO:注意更换
        'myvs_13c': '郑州市.高新区',  # TODO:注意更换
        'myvs_24': '否',
        'myvs_26': 5,
        'memo22': '郑州大学主校区'
    }
    response = session.post(JKSB_URL, headers=headers, data=data2)
    html = response.content.decode('utf-8')
    res = re.findall(r'(感谢你今日上报健康状况)', html)[0]
    #print(res)
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
        requests.post('https://sctapi.ftqq.com/'+str(sev)+'.send?title=打卡成功')
    except Exception as err:
        print(err)
        requests.post('https://sctapi.ftqq.com/'+str(sev)+'.send?title=打卡成功但是发送邮件失败')
        print("打卡成功但是发送邮件失败")

except Exception as err:
    print(err)
    traceback.print_exc()
    requests.post('https://sctapi.ftqq.com/'+str(sev)+'.send?title=打卡失败')
    
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
