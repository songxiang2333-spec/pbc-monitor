import requests
import smtplib
from email.mime.text import MIMEText
import json
import os
import time

API_URL = "https://www.jianyu360.cn/front/pcAjaxReq"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

EXCLUDE = ["windows","win7","win10","win11","windows server"]

HISTORY_FILE = "history_jianyu.json"

SENDER_EMAIL = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]
RECEIVER_EMAIL = os.environ["RECEIVER_EMAIL"]


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

    results = []

    for page in range(1,6):

        payload = {
            "searchWord":"操作系统",
            "pageNum":page
        }

        r = requests.post(API_URL,json=payload,headers=HEADERS)

        try:
            data = r.json()
        except:
            continue

        items = data.get("data",[])

        for item in items:

            title = item.get("title","")
            url = item.get("url","")

            if not title:
                continue

            if any(x in title.lower() for x in EXCLUDE):
                continue

            if title in history:
                continue

            try:

                detail = requests.get(url,headers=HEADERS,timeout=10)

                text = detail.text.lower()

                if any(x in text for x in EXCLUDE):
                    continue

                if "招标" not in text:
                    continue

                category,standalone = classify(text)

                results.append(
f"""
标题: {title}
分类: {category}
单独采购操作系统: {standalone}
链接: {url}
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
