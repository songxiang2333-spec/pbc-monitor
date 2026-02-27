import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import json
import os
import time

URL = "https://www.jianyu360.cn/jylab/supsearch/index.html?keywords=操作系统&selectType=title&searchGroup=1"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

HISTORY_FILE = "history_jianyu.json"

SENDER_EMAIL = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]
RECEIVER_EMAIL = os.environ["RECEIVER_EMAIL"]

EXCLUDE = ["win7","win10","windows"]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(data):
    with open(HISTORY_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

def send_mail(content):

    msg = MIMEText(content,"plain","utf-8")
    msg["Subject"] = "剑鱼360 操作系统招标监控"

    server = smtplib.SMTP_SSL("smtp.163.com",465)
    server.login(SENDER_EMAIL,SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL,RECEIVER_EMAIL,msg.as_string())
    server.quit()

def classify(text):

    category = "桌面操作系统"

    if "服务器" in text:
        category = "服务器操作系统"

    standalone = "否"

    if "操作系统采购" in text or "采购操作系统" in text:
        standalone = "是"

    return category,standalone


def main():

    history = load_history()

    r = requests.get(URL,headers=HEADERS)
    soup = BeautifulSoup(r.text,"html.parser")

    results = []

    for a in soup.find_all("a"):

        title = a.get_text(strip=True)
        link = a.get("href")

        if not title or not link:
            continue

        if "操作系统" not in title:
            continue

        if any(x in title.lower() for x in EXCLUDE):
            continue

        if title in history:
            continue

        try:

            detail = requests.get(link,headers=HEADERS,timeout=10)

            detail_soup = BeautifulSoup(detail.text,"html.parser")

            text = detail_soup.get_text()

            if "招标公告" not in text and "正在招标" not in text:
                continue

            category,standalone = classify(text)

            results.append(
                f"""
标题: {title}
分类: {category}
单独采购: {standalone}
链接: {link}
"""
            )

            history.append(title)

            time.sleep(1)

        except:
            continue


    if results:
        send_mail("\n".join(results))
    else:
        send_mail("hadn't found it")


    save_history(history)


if __name__ == "__main__":
    main()
