import requests
import os
import logging


# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

# ایجاد یک session برای حفظ کوکی‌ها
session = requests.Session()

# -----------------------
# ۱. ورود به حساب کاربری
# -----------------------
login_url = "https://my.drclubs.ir/account/login"

# اگر سایت CSRF Token دارد، باید آن را هم اضافه کنید
# در این مثال فرض می‌کنیم بدون token هم می‌شود login کرد
payload = {
    "username": "za...",
    "password": "09395..."
}

headers = {
    "Referer": login_url
}

try:
    login_resp = session.post(login_url, data=payload, headers=headers)
    logging.info(f" {login_resp.status_code}")
    if login_resp.status_code == 200:
        logging.info("Successfully logged in")
    else:
        logging.error(f"{login_resp.status_code}")
        exit() # خروج در صورت بروز خطا در ورود به سیستم
except requests.exceptions.RequestException as e:
    logging.error(f"Unsuccessfully logged in {e}")
    exit()

# -----------------------
# ۲. دانلود Excel گزارش مشتریان
# -----------------------
excel_url = (
    "https://my.drclubs.ir/biz/smssecretary/exportexcel?CascadeData=%7B%22HasSearch%22%3Atrue,%22SearchInfo%22%3A%5B%5D,%22Page%22%3A1%7D"
)


current_dir = os.path.dirname(__file__)
base_dir = os.path.dirname(current_dir)        # مسیر folder_project_city
data_dir = os.path.join(base_dir, "data")
file_path = os.path.join(data_dir, "extract_Drclubs.xlsx")


try:
    excel_resp = session.get(excel_url)
    excel_resp.raise_for_status()  # بررسی خطاهای HTTP (مانند 404)

    with open(file_path, "wb") as f:
        f.write(excel_resp.content)
    logging.info(f"Path Saved: {file_path} ")

except requests.exceptions.RequestException as e:
    logging.error(f"Error: {e}")
except Exception as e:
    logging.error(f"Error: {e}")


# print("Excel report saved as customers.xlsx")

# -----------------------
# ۳. دانلود Excel مشخصات تکمیلی (اختیاری)
# -----------------------
extra_excel_url = "https://my.drclubs.ir/biz/businesscustomerextrainfo/exportexcel"


file_path2 = os.path.join(data_dir, "customers_extra.xlsx")

try:
    extra_resp = session.get(extra_excel_url)
    extra_resp.raise_for_status()

    with open(file_path2, "wb") as f:
        f.write(extra_resp.content)

    logging.info(f"Path Saved: {file_path2}")

except requests.exceptions.RequestException as e:
    logging.error(f"Error: {e}")
except Exception as e:
    logging.error(f"Error: {e}")


# print("Extra Excel report saved as customers_extra.xlsx")
