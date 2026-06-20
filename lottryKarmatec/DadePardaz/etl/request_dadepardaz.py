import requests
import pandas as pd
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys


LOGIN_URL = "https://wsp2.adpdigital.com/index.php/fa/auth/login"
HOME_URL = "https://wsp2.adpdigital.com/"


def get_authenticated_cookies(username, password):
    options = Options()
    # برای دیباگ headless رو خاموش بذار، بعداً می‌تونی روشنش کنی
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    # 1) صفحه اصلی (گرفتن کوکی اولیه)
    driver.get(HOME_URL)
    time.sleep(2)

    # 2) صفحه لاگین
    driver.get(LOGIN_URL)

    # 3) صبر تا فیلدها
    username_input = wait.until(
        EC.visibility_of_element_located((By.NAME, "handle"))
    )
    password_input = wait.until(
        EC.visibility_of_element_located((By.NAME, "passwd"))
    )

    username_input.clear()
    username_input.send_keys(username)

    password_input.clear()
    password_input.send_keys(password)

    password_input.send_keys(Keys.RETURN)


    # 5) صبر تا ورود
    time.sleep(5)

    # 6) گرفتن کوکی‌ها
    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

    driver.quit()
    return cookies



cookies = get_authenticated_cookies(
    "rizanfelez",
    "rizanfelez.com"
)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest"
})
session.cookies.update(cookies)


all_rows = []
start = 0
length = 100

while True:
    params = {
        "sEcho": 1,
        "iColumns": 6,
        "iDisplayStart": start,
        "iDisplayLength": length,
        "mDataProp_0": 0,
        "mDataProp_1": 1,
        "mDataProp_2": 2,
        "mDataProp_3": 3,
        "mDataProp_4": 4,
        "mDataProp_5": 5,
        "sSearch": "",
        "bRegex": "false",
        "sSearch_2": "~"
    }

    r = session.get(
        "https://wsp2.adpdigital.com/index.php/fa/messages/incoming/",
        params=params
    )

    # اگر سشن پرید
    if "text/html" in r.headers.get("Content-Type", ""):
        raise Exception("Session expired – need relogin")

    data = r.json()
    rows = data.get("aaData", [])

    if not rows:
        break

    all_rows.extend(rows)
    start += length

df = pd.DataFrame(
    all_rows,
    columns=[
        "row",
        "phone_number",
        "text_sent",
        "col4",
        "col5",
        "col6"
    ]
)


current_dir = os.path.dirname(__file__)
base_dir = os.path.dirname(current_dir)        # مسیر folder_project_city
data_dir = os.path.join(base_dir, "data")


file_path = os.path.join(data_dir, "extract_dadepardaz.xlsx")
df.to_excel(file_path, index=False)
print("✅ extract_dadepardaz.xlsx ساخته شد")

