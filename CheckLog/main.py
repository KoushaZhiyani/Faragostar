import pymysql
import datetime

# -----------------------------
# تنظیمات اتصال به MySQL لوکال
# -----------------------------
DB_CONFIG = {
    "host": "192.168...",
    "user": "zhe...",
    "password": "z...",   # پسورد خودت
    "database": "b...", # نام دیتابیس
    "cursorclass": pymysql.cursors.DictCursor
}

# -----------------------------
# اتصال به دیتابیس
# -----------------------------
def get_connection():
    return pymysql.connect(**DB_CONFIG)

# -----------------------------
# ثبت لاگ مغایرت
# -----------------------------
def insert_log(conn, table_name, t_count, v_count):
    with conn.cursor() as cursor:
        sql = """
        INSERT INTO mismatch_log 
        (table_name, t_count, v_count, log_date)
        VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(sql, (table_name, t_count, v_count))
    conn.commit()

# -----------------------------
# بررسی ویو
# -----------------------------
def check_view():
    conn = get_connection()
    print(conn)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM check_correct_event WHERE Flag = 0")
            rows = cursor.fetchall()

            if not rows:
                print("✅ هیچ مغایرتی وجود ندارد")
                return

            print("⚠ مغایرت پیدا شد:")
            for row in rows:
                name = row["Name"]
                t_cnt = row["t_count"]
                v_cnt = row["v_count"]

                print(f"Table: {name} | t_count={t_cnt} | v_count={v_cnt}")

                # ثبت در لاگ
                insert_log(conn, name, t_cnt, v_cnt)

    except Exception as e:
        print("❌ خطا:", e)

    finally:
        conn.close()

# -----------------------------
# اجرای مستقیم
# -----------------------------
if __name__ == "__main__":
    print("===== شروع بررسی =====")
    check_view()
    print("===== پایان =====")
