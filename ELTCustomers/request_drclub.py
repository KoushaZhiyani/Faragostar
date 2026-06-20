import requests
from pathlib import Path

# ایجاد یک session برای حفظ کوکی‌ها
session = requests.Session()

# -----------------------
# ۱. ورود به حساب کاربری
# -----------------------
login_url = "https://my.drclubs.ir/account/login"

# اگر سایت CSRF Token دارد، باید آن را هم اضافه کنید
# در این مثال فرض می‌کنیم بدون token هم می‌شود login کرد
payload = {
    "username": "zah...",
    "password": "093951..."
}

headers = {
    "Referer": login_url
}

login_resp = session.post(login_url, data=payload, headers=headers)
print("Login status:", login_resp.status_code)

# -----------------------
# ۲. دانلود Excel گزارش مشتریان
# -----------------------
excel_url = (
    "https://my.drclubs.ir/biz/businesscustomer/exportexcel?"
    "CascadeData=%7B%22HasSearch%22%3Atrue,%22SearchInfo%22%3A%5B%7B%22SearchAtf%22%3Atrue,"
    "%22SearchFieldType%22%3A7,%22SearchFieldTitle%22%3A%22%DA%AF%D8%B1%D9%88%D9%87%20%D8%A7%D8%AE%D8%AA%D8%B5%D8%A7%D8%B5%DB%8C%22,"
    "%22SearchField%22%3A%22DedicatedGroup%22,%22SearchOperator%22%3A%22%D8%B4%D8%A7%D9%85%D9%84%22,"
    "%22SearchValue%22%3A%22fe909906%22%7D%5D,%22OrderInfo%22%3A%5B%7B%22FieldName%22%3A%22CreateDate%22,"
    "%22Descending%22%3Atrue%7D%5D%7D"
)

excel_resp = session.get(excel_url)

# ذخیره فایل Excel
file_path = Path(__file__).parent / "customers.xlsx"

with open(file_path, "wb") as f:
    f.write(excel_resp.content)

print("Excel report saved as customers.xlsx")

# -----------------------
# ۳. دانلود Excel مشخصات تکمیلی (اختیاری)
# -----------------------
extra_excel_url = "https://my.drclubs.ir/biz/businesscustomerextrainfo/exportexcel"

extra_resp = session.get(extra_excel_url)

file_path = Path(__file__).parent / "customers_extra.xlsx"
with open(file_path, "wb") as f:
    f.write(extra_resp.content)

print("Extra Excel report saved as customers_extra.xlsx")
