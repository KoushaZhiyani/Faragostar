# monitor.py
import json
import requests
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque
from datetime import datetime
import logging
import time
import os

    # ---------------------------
    # تنظیمات Logging
    # ---------------------------
logging.basicConfig(
        filename=r'C:\Users\zhiani\Desktop\folder_project_city\Server_Stauts\monitor.log',
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        encoding='utf-8'
    )


app = Flask(__name__)

DATA_FILE = 'servers.json'
servers = []           # [{'ip':..., 'name':..., 'drive':...}, ...]
status_data = {}       # {"ip::drive": {...}}
history_data = {}      # {"ip::drive": deque([...])}
_last_sms_time = {}    # {"ip::drive": datetime}

HISTORY_LIMIT = 30
SMS_COOLDOWN_SECONDS = 300
MONITOR_RESULT_FILE = r'C:\Users\zhiani\Desktop\folder_project_city\Server_Stauts\monitor_result.json'


history_data = {}  # {ip: deque([...])}


def send_sms_ir(message):
        url = "https://api.sms.ir/v1/send/bulk"

        headers = {
            "X-API-KEY": "PBapxUHXiM0iPFlMp0r6jCXTxT7XdvDBBtoHb8T7gRApq9cQ",
            "Content-Type": "application/json"
        }

        payload = {
            "lineNumber": 30002128001557,  # شماره ارسال
            "messageText": message,
            "mobiles": [
                "09394413663"
            ],
            "sendDateTime": None
        }

        r = requests.post(url, json=payload, headers=headers, timeout=5)
        r.raise_for_status()
        return r.json()

# ---------- مدیریت فایل ----------

def load_servers():
        global servers
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                servers = json.load(f)
        except FileNotFoundError:
            servers = []

def save_servers():
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(servers, f, ensure_ascii=False, indent=2)


# ---------- دریافت وضعیت ----------

# def fetch_server_stats(server_info):
#         """از Agent درخواست می‌کند و داده‌ها را برمی‌گرداند"""

#         ip = server_info['ip']
#         drive = server_info.get('drive', 'D:')
#         base_url = f'http://{ip}:5000'
#         stats = {'ip': ip, 'online': False, 'drive': drive}

            
#         try:
#             cpu_resp = requests.get(f'{base_url}/cpu', timeout=5)
#             if cpu_resp.status_code == 200:
#                 stats['cpu'] = cpu_resp.json().get('cpu_percent')
#                 stats['online'] = True

#             mem_resp = requests.get(f'{base_url}/memory', timeout=5)
#             if mem_resp.status_code == 200:
#                 stats['memory'] = mem_resp.json()

#             # استفاده از درایو مشخص شده برای سرور
#             disk_resp = requests.get(f'{base_url}/disk?drive={drive}', timeout=5)
#             if disk_resp.status_code == 200:
#                 stats['disk'] = disk_resp.json()
#             else:
#                 # تلاش برای درایو C: اگر درایو مشخص شده نبود
#                 disk_resp = requests.get(f'{base_url}/disk?drive=C:', timeout=5)
#                 if disk_resp.status_code == 200:
#                     stats['disk'] = disk_resp.json()
#                     stats['drive_fallback'] = True  # نشان‌دهنده استفاده از درایو جایگزین
#         except requests.exceptions.RequestException as e:
#             stats['error'] = str(e)

#         # print("stats:", stats)
#         return stats


# ---------- به‌روزرسانی دوره‌ای ----------
def update_all_servers():
    global history_data, _last_sms_time, status_data

    print("1")
    if not os.path.exists(MONITOR_RESULT_FILE):
        logging.warning(f"File {MONITOR_RESULT_FILE} not found.")
        return

    # خواندن فایل JSON
    try:
        with open(MONITOR_RESULT_FILE, 'r', encoding='utf-8-sig') as f:   # تغییر اینجا
            raw = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load/parse JSON: {e}")
        return

    # آرایه بودن داده‌ها بررسی شود
    if not isinstance(raw, list):
        logging.error("JSON structure is not a list.")
        return

    # ساختن یک دیکشنری برای جستجوی سریع‌تر: کلید = "IP::Drive" (بزرگ‌کردن درایو)
    lookup = {}
    for entry in raw:
        ip = entry.get('Computer')
        drive = entry.get('Disk', {}).get('drive', '').upper()
        if ip and drive:
            key = f"{ip}::{drive}"
            # اگر چند نمونه با یک کلید وجود داشت، آخرین را ذخیره می‌کنیم (اختیاری)
            lookup[key] = entry

    # بازنشانی وضعیت‌ها و سپس پُر کردن بر اساس لیست سرورها
    status_data.clear()

    for srv in servers:
        ip = srv['ip']
        drive = srv.get('drive', 'D:').upper()   # یکسان‌سازی فرمت
        key = f"{ip}::{drive}"

        if key in lookup:
            entry = lookup[key]
            # ساختن دیکشنری داده به همان شکلی که فرانت‌اند انتظار دارد
            data = {
                'ip': ip,
                'drive': drive,
                'online': True,
                'cpu': entry.get('CPU', 0),
                'memory': entry.get('Memory', {}),
                'disk': entry.get('Disk', {}),
                'time': entry.get('Time', '')
            }

            # استخراج درصدها برای بررسی وضعیت و تاریخچه
            cpu_percent = data['cpu']
            ram_percent = data['memory'].get('percent', 0)
            disk_percent = data['disk'].get('percent', 0)

            # تعیین وضعیت متنی
            status_text = explain_status(cpu_percent, ram_percent, disk_percent)
            data['status_text'] = status_text

            # ذخیره وضعیت جاری
            status_data[key] = data

            # ---- هشدار و پیامک ----
            if ram_percent >= 80 or cpu_percent >= 90 or disk_percent >= 90:
                logging.warning(
                    f'HIGH USAGE | IP: {key} | RAM: {ram_percent}% | CPU: {cpu_percent}% | STATUS: {status_text}'
                )
                now = datetime.now()
                last_time = _last_sms_time.get(key)
                if last_time is None or (now - last_time).total_seconds() > SMS_COOLDOWN_SECONDS:
                    try:
                        message = (
                            f"⚠️ هشدار مانیتورینگ\n"
                            f"IP: {key}\n"
                            f"RAM: {ram_percent}%\n"
                            f"CPU: {cpu_percent}%\n"
                            f"Disk: {disk_percent}%\n"
                            f"وضعیت: {status_text}"
                        )
                        resp = send_sms_ir(message)
                        logging.info(f"SMS sent for {key}: {resp}")
                    except Exception as e:
                        logging.error(f"Failed to send SMS for {key}: {e}")
                    finally:
                        _last_sms_time[key] = now

            # ---- تاریخچه ----
            history_data.setdefault(key, deque(maxlen=HISTORY_LIMIT))
            history_data[key].append({
                'time': datetime.now().strftime('%H:%M:%S'),
                'cpu': cpu_percent,
                'ram': ram_percent,
                'disk': disk_percent,
                'status': status_text
            })

        else:
            # سرور در فایل یافت نشد → آفلاین
            offline_data = {
                'ip': ip,
                'drive': drive,
                'online': False,
                'error': 'No data in monitor_result.json'
            }
            status_data[key] = offline_data


def explain_status(cpu, ram, disk):
        """
        Evaluates system health based on CPU, RAM, and Disk usage.
        Returns a detailed status with severity level.
        """

        severity = 0     # 0=Normal, 1=Warning, 2=Critical
        reasons = []     # list of components causing the status

        # --- RAM checks ---
        if ram >= 90:
            severity = max(severity, 2)
            reasons.append(f"RAM Critical ({ram}%)")
        elif ram >= 70:
            severity = max(severity, 1)
            reasons.append(f"RAM High ({ram}%)")

        # --- CPU checks ---
        if cpu >= 90:
            severity = max(severity, 2)
            reasons.append(f"CPU Critical ({cpu}%)")
        elif cpu >= 70:
            severity = max(severity, 1)
            reasons.append(f"CPU High ({cpu}%)")
        elif cpu >= 50:
            severity = max(severity, 1)
            reasons.append(f"CPU Elevated ({cpu}%)")

        # --- Disk checks ---
        if disk >= 95:
            severity = max(severity, 2)
            reasons.append(f"Disk Critical ({disk}%)")
        elif disk >= 80:
            severity = max(severity, 1)
            reasons.append(f"Disk High ({disk}%)")

        # --- Final status ---
        if severity == 2:
            level = "Critical"
        elif severity == 1:
            level = "Warning"
        else:
            level = "Normal (Healthy System)"

        if reasons:
            return f"{level}  |  Causes: " + ", ".join(reasons)
        else:
            return level


# ---------- زمان‌بند ----------
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_all_servers, trigger="interval", seconds=10)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())





# ---------- مسیرهای Flask ----------


@app.route('/')
def dashboard():
        """داشبورد اصلی"""
        return render_template('dashboard.html', servers=servers, status=status_data)

    # API برای مدیریت سرورها
@app.route('/api/servers', methods=['GET', 'POST'])
def manage_servers():
        global servers
        if request.method == 'POST':
            data = request.get_json()

            ip = data.get('ip')
            name = data.get('name', ip)
            drive = data.get('drive', 'D:')  # دریافت درایو، پیش‌فرض D:
            if not ip:
                return jsonify({'error': 'IP الزامی است'}), 400
            

            # جلوگیری از ثبت تکراری
            if any(s['ip'] == ip and s['drive'] == drive for s in servers):
                return jsonify({'error': 'این IP قبلاً ثبت شده'}), 409
            
            servers.append({'ip': ip, 'name': name, 'drive': drive})  # اضافه کردن درایو
            save_servers()
            return jsonify({'message': 'سرور اضافه شد'}), 201
        else:
            return jsonify(servers)


@app.route('/api/servers/<ip>', methods=['DELETE'])
def delete_server(ip):
    drive = request.args.get('drive')
    global servers

    if drive:
        # حذف فقط یک درایو
        servers = [s for s in servers if not (s['ip'] == ip and s['drive'] == drive)]
        key = f"{ip}::{drive}"
        status_data.pop(key, None)
        history_data.pop(key, None)
        _last_sms_time.pop(key, None)
    else:
        # حذف کل IP
        servers = [s for s in servers if s['ip'] != ip]
        keys_to_del = [k for k in status_data if k.startswith(f"{ip}::")]
        for k in keys_to_del:
            del status_data[k]
            history_data.pop(k, None)
            _last_sms_time.pop(k, None)

    save_servers()
    return jsonify({'message': 'سرور حذف شد'}), 200



@app.route('/api/status')
def api_status():
    # مستقیماً کلیدهای ترکیبی را برمی‌گردانیم تا فرانت‌اند با srv.ip + '::' + srv.drive بخواند
    return jsonify(status_data)



@app.route('/api/history/<ip>')
def api_history(ip):
    drive = request.args.get('drive')
    if drive:
        key = f"{ip}::{drive}"
        return jsonify(list(history_data.get(key, [])))
    else:
        # برگرداندن کل تاریخچه‌های IP به صورت دیکشنری
        result = {}
        for key, val in history_data.items():
            if key.startswith(f"{ip}::"):
                drv = key.split('::')[1]
                result[drv] = list(val)
        return jsonify(result)

    # اجرای اولیه
if __name__ == '__main__':
    load_servers()
    update_all_servers()
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
