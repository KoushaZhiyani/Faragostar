import struct
import time
from datetime import datetime
import json
import copy
import threading
import requests  

class CNCSessionManager:

    def __init__(self):
        self.boards_status = {} 
        self.device_mapping = {}
        # دیتابیس و صف‌ها حذف شدند

    def get_device_name(self, ip_address):
        if not ip_address:
            return "Unknown"
        
        ip_suffix = str(ip_address).split('.')[-1]
        
        if ip_address in self.device_mapping:
            return self.device_mapping[ip_address]
        elif ip_suffix in self.device_mapping:
            return self.device_mapping[ip_suffix]
        
        return f"Board-{ip_suffix}"

    def process_log(self, ip_address, log_line):
        parsed_packets = self.parse_device_hex_log(log_line)
        for data in parsed_packets:
            msg_id = data["ID"]
            
            # 1. بروزرسانی داشبورد
            self.update_board_last_log(ip_address, f"ID: {msg_id:#04x}", data)
            
            # 2. آماده‌سازی دیتا و پرینت به جای ذخیره در دیتابیس
            device_name = self.get_device_name(ip_address)
            decoded_json = json.dumps(data, ensure_ascii=False)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # چاپ خروجی
            print(f"[{current_time}] IP: {ip_address} | Device: {device_name} | MsgID: {msg_id:#04x} | Data: {decoded_json}")


    def parse_device_hex_log(self, log_line):
        if "->" in log_line:
            hex_string = log_line.split("->")[1].strip()
        else:
            hex_string = log_line.strip()

        try:
            raw_bytes = bytes.fromhex(hex_string)
        except ValueError:
            return []

        if len(raw_bytes) < 13:
            return []

        parsed_data = []
        FULL_HEADER_LEN = 11
        
        msg_id = raw_bytes[FULL_HEADER_LEN]
        msg_len = raw_bytes[FULL_HEADER_LEN + 1]
        payload = raw_bytes[FULL_HEADER_LEN + 2 : FULL_HEADER_LEN + 2 + msg_len]

        if msg_id == 0x01 and len(payload) >= 4:
            personnel_id = struct.unpack(">H", payload[0:2])[0]
            part_code = struct.unpack(">H", payload[2:4])[0]
            process_bytes = payload[5:].split(b'\x00')[0]
            process_code = process_bytes.decode('ascii', errors='ignore')
            personnel_name = self.get_personnel_name(personnel_id)
            part_name = self.get_part_name(part_code)
    
            parsed_data.append({
                "ID": 0x01, 
                "Personnel": personnel_id, 
                "PersonnelName": personnel_name, 
                "Part": part_code, 
                "PartName": part_name, 
                "Process": process_code
            })

        elif msg_id == 0x02 and len(payload) >= 2:
            count = struct.unpack(">H", payload[0:2])[0]
            parsed_data.append({"ID": 0x02, "Count": count})

        elif msg_id == 0x04 and len(payload) >= 4:
            scrap = struct.unpack(">H", payload[0:2])[0]
            rework = struct.unpack(">H", payload[2:4])[0]
            parsed_data.append({"ID": 0x04, "Scrap": scrap, "Rework": rework})

        elif msg_id == 0x05:
            forms = []
            for i in range(0, len(payload), 4):
                if i + 4 <= len(payload):
                    f1, f2 = struct.unpack(">HH", payload[i:i+4])
                    if f1 != 0 or f2 != 0:
                        forms.append(f"{f1}/{f2}")
            parsed_data.append({"ID": 0x05, "Forms": forms})

        elif msg_id == 0x03 and len(payload) >= 4:
            device_stop_code, person_stop_code = struct.unpack(">HH", payload[0:4])
            parsed_data.append({"ID": 0x03, "DeviceStopCode": device_stop_code / 100, "PersonStopCode": person_stop_code})

        return parsed_data

    def update_board_connection(self, board_id, is_connected, ip_address=None):
        if board_id not in self.boards_status:
            self.boards_status[board_id] = {
                "ip": ip_address,
                "device_name": self.get_device_name(ip_address),
                "is_connected": False,
                "last_seen": None,
                "last_log_type": "-",
                "last_log_data": {},
                "session_logs": [] 
            }
        
        self.boards_status[board_id]["is_connected"] = is_connected
        self.boards_status[board_id]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_board_last_log(self, board_id, log_type, log_data):
        if board_id in self.boards_status:
            self.boards_status[board_id]["last_log_type"] = log_type
            self.boards_status[board_id]["last_log_data"] = log_data
            self.boards_status[board_id]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            current_id = log_data.get("ID")
            
            if "session_logs" not in self.boards_status[board_id]:
                self.boards_status[board_id]["session_logs"] = []

            if current_id == 0x01:
                self.boards_status[board_id]["session_logs"] = []

            log_with_time = dict(log_data)
            log_with_time["Time"] = datetime.now().strftime("%H:%M:%S")
            
            if current_id == 0x04:
                self.boards_status[board_id]["session_logs"] = [
                    log for log in self.boards_status[board_id]["session_logs"] 
                    if log.get("ID") != 0x04
                ]

            self.boards_status[board_id]["session_logs"].append(log_with_time)

    def get_all_boards_status(self):
        return copy.deepcopy(self.boards_status)

    def get_personnel_name(self, personnel_id):
        # چون دیتابیس حذف شده، یک مقدار پیش‌فرض برمی‌گردانیم
        return "نامشخص"
    
    def get_part_name(self, part_code):
        # چون دیتابیس حذف شده، یک مقدار پیش‌فرض برمی‌گردانیم
        return "نامشخص"

    def send_sms_ir(self, message):
        try:
            url = "https://api.sms.ir/v1/send/bulk"
            headers = {
                "X-API-KEY": "PBapxUHXiM0iPFlMp0r6jCXTxT7XdvDBBtoHb8T7gRApq9cQ",
                "Content-Type": "application/json"
            }
            payload = {
                "lineNumber": 30002128001557,
                "messageText": message,
                "mobiles": ["09394413663"],
                "sendDateTime": None
            }
            r = requests.post(url, json=payload, headers=headers, timeout=5)
            r.raise_for_status()
            print("SMS Sent Successfully:", r.json())

        except Exception as e:
            print(f"Error sending SMS: {e}")

logs_to_process = [
    ("192.168.1.169", "45 00 A9 54 4E 43 32 33 00 00 00 02 04 00 01 00 00"),
    ("192.168.1.164", "45 00 A4 54 4E 43 31 32 00 00 00 02 04 00 03 00 00"),
    ("192.168.1.115", "45 00 73 54 4E 43 30 32 00 00 00 02 04 00 01 00 00"),
    ("192.168.1.147", "45 00 93 54 4E 43 38 37 00 00 00 02 04 00 00 00 00"),
    ("192.168.1.148", "45 00 94 54 4E 43 33 32 00 00 00 02 04 DA 4E 00 00"),
    ("192.168.1.106", "45 00 6A 54 4E 43 35 34 00 00 00 02 04 00 F5 00 00"),
    ("192.168.1.115", "45 00 73 54 4E 43 30 32 00 00 00 01 1B 03 5D 00 25 00 54 30 38 30 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    ("192.168.1.156", "45 00 9C 54 4E 43 39 37 00 00 00 02 04 00 04 00 00"),
    ("192.168.1.156", "45 00 9C 54 4E 43 39 37 00 00 00 02 04 00 00 00 00"),
    ("192.168.1.107", "45 00 6B 54 4E 43 39 38 00 00 00 02 04 00 01 00 00"),
    ("192.168.1.106", "45 00 6A 54 4E 43 35 34 00 00 00 04 04 00 00 00 00"),
    ("192.168.1.106", "45 00 6A 54 4E 43 35 34 00 00 00 05 28 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    ("192.168.1.106", "45 00 6A 54 4E 43 35 34 00 00 00 03 04 00 00 00 00"),
    ("192.168.1.169", "45 00 A9 54 4E 43 32 33 00 00 00 01 1B 03 03 00 25 00 54 30 34 32 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    ("192.168.1.164", "45 00 A4 54 4E 43 31 32 00 00 00 01 1B 03 03 00 25 00 54 30 34 31 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    ("192.168.1.138", "45 00 8A 54 4E 43 32 37 00 00 00 02 04 00 38 00 00"),
    ("192.168.1.156", "45 00 9C 54 4E 43 39 37 00 00 00 01 1B 05 F9 00 12 00 44 42 31 31 30 00 00 00 00 00 00 00 00 00 00 00 00"),
    ("192.168.1.156", "45 00 9C 54 4E 43 39 37 00 00 00 04 04 00 00 00 00"),
    ("192.168.1.156", "45 00 9C 54 4E 43 39 37 00 00 00 05 28 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    ("192.168.1.156", "45 00 9C 54 4E 43 39 37 00 00 00 03 04 02 BC 00 00"),
    ("192.168.1.145", "45 00 91 54 4E 43 32 36 00 00 00 01 1B 05 5A 00 19 00 44 54 30 36 30 00 00 00 00 00 00 00 00 00 00 00 00"),
    ("192.168.1.107", "45 00 6B 54 4E 43 39 38 00 00 00 01 1B 05 F9 00 16 00 44 50 31 31 30 00 00 00 00 00 00 00 00 00 00 00 00"),
    ("192.168.1.138", "45 00 8A 54 4E 43 32 37 00 00 00 01 1B 05 03 00 16 00 44 50 31 30 38 00 00 00 00 00 00 00 00 00 00 00 00"),
    ("192.168.1.162", "45 00 A2 54 4E 43 36 30 00 00 00 01 1B 05 DA 00 19 00 44 54 30 37 30 00 00 00 00 00 00 00 00 00 00 00 00"),
]


manager = CNCSessionManager()

for ip_address, log_line in logs_to_process:
    manager.process_log(ip_address, log_line)

