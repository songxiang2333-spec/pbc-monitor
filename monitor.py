import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import json
import time
from datetime import datetime

# ==============================
# 配置
# ==============================
BASE_URL = "https://jzcg.pbc.gov.cn"
LIST_TEMPLATE = "https://jzcg.pbc.gov.cn/freecms/site/rmyh/ggxx/index_{}.html"
FIRST_PAGE = "https://jzcg.pbc.gov.cn/freecms/site/rmyh/ggxx/index.html"

MAX_PAGES = 5   # 抓前5页（防漏）
DATA_FILE = "history.json"

SENDER_EMAIL = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]
RECEIVER_EMAIL = "songxiang2333@gmail.com"

# ==============================
# 邮件
# ==============================
def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    server = smtplib.SMTP_SSL("smtp.163.com", 465)
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    server.quit()

# ==============================
# 历史记录
# ==============================
def load_history():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==============================
# 抓取页面
# ==============================
def fetch_page(url):
    for i in range(3):  # 自动重试3次
        try:
            response = requests.get(url, timeout=15)
            response.encoding = "utf-8"
            return response.text
        except Exception:
            time.sleep(2)
    return None

# ==============================
# 解析公告列表
# ==============================
def parse_list(html):
    soup = BeautifulSoup(html, "html.parser")
    items = []

    links = soup.find_all("a")
    for link in links:
        title = link.get_text().strip()
        href = link.get("href")

        if not title or not href:
            continue

        if "info" in href:  # 公告详情页特征
            full_link = href if href.startswith("http") else BASE_URL + href
            items.append({
                "title": title,
                "link": full_link
            })

    return items

# ==============================
# 检查是否包含关键词（查详情页）
# ==============================
KEYWORDS = ["桌面操作系统", "服务器操作系统"]

def contains_keyword(url):
    html = fetch_page(url)
    if not html:
        return False

    for keyword in KEYWORDS:
        if keyword in html:
            return True
    return False

# ==============================
# 主逻辑
# ==============================
def main():
    history = load_history()
    all_items = []

    # 抓首页
    first_html = fetch_page(FIRST_PAGE)
    if not first_html:
        send_email("警告：网站无法访问", "采购网首页访问失败")
        return

    all_items.extend(parse_list(first_html))

    # 抓后续页
    for page in range(1, MAX_PAGES):
        url = LIST_TEMPLATE.format(page)
        html = fetch_page(url)
        if html:
            all_items.extend(parse_list(html))

    # 去重
    unique_items = {item["link"]: item for item in all_items}.values()

    new_matches = []

    for item in unique_items:
        if item["link"] not in history:
            # 新公告才检查关键词
            if contains_keyword(item["link"]):
                new_matches.append(item)
            history.append(item["link"])

    if new_matches:
        body = "发现新的操作系统相关招标公告：\n\n"
        for item in new_matches:
            body += f"{item['title']}\n{item['link']}\n\n"

        send_email("【新增】操作系统招标公告", body)

    save_history(history)
    print("检测完成")

if __name__ == "__main__":
    main()
