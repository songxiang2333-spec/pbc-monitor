import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

URL = "https://jzcg.pbc.gov.cn/"
KEYWORDS = ["桌面操作系统", "服务器操作系统"]

SENDER_EMAIL = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]
RECEIVER_EMAIL = "songxiang2333@gmail.com"

def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    server.quit()

def check():
    response = requests.get(URL, timeout=15)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text()

    found = []
    for keyword in KEYWORDS:
        if keyword in text:
            found.append(keyword)

    if found:
        body = "发现关键词：\n\n" + "\n".join(found) + "\n\n请登录官网查看详细信息。"
        send_email("发现操作系统招标信息", body)
    else:
        send_email("检查结果", "hadn't found it")

if __name__ == "__main__":
    check()
