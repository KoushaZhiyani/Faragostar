import pymysql
import datetime
exit()
# -----------------------------
# تنظیمات اتصال به MySQL لوکال
# -----------------------------
DB_CONFIG = {
    "host": "192.168.0.43",
    "user": "zheiani",
    "password": "zh@123456",   # پسورد خودت
    "database": "bitnami_pm", # نام دیتابیس
    "cursorclass": pymysql.cursors.DictCursor
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)


conn = get_connection()

with conn.cursor() as cursor:
    cursor.execute("SELECT * FROM v_test_process")
    rows = cursor.fetchall()

print(rows[0])