import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

# ==============================
# 目标网站
# ==============================
URL = "https://jzcg.pbc.gov.cn/"
KEYWORDS = ["桌面操作系统", "服务器操作系统"]

# ==============================
# 从 GitHub Secrets 读取邮箱信息
# ==============================
SENDER_EMAIL = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]

# 收件邮箱（可以和发件邮箱相同）
RECEIVER_EMAIL = "songxiang2333@gmail.com"

# ==============================
# 发送邮件函数（163 SMTP）
# ==============================
def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    try:
        server = smtplib.SMTP_SSL("smtp.163.com", 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print("邮件发送失败:", e)
        raise e

# ==============================
# 检查网站
# ==============================
def check():
    try:
        response = requests.get(URL, timeout=15)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text()

        found_keywords = []

        for keyword in KEYWORDS:
            if keyword in text:
                found_keywords.append(keyword)

        if found_keywords:
            body = "发现相关招标信息关键词：\n\n"
            body += "\n".join(found_keywords)
            body += "\n\n请登录官网查看详细公告：\n" + URL
            send_email("发现操作系统相关招标信息", body)
        else:
            send_email("检查结果", "hadn't found it")

    except Exception as e:
        send_email("检查失败", f"网站访问失败：{e}")

# ==============================
# 主程序入口
# ==============================
if __name__ == "__main__":
    check()
