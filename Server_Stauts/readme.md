# 📊 Server Status Monitoring System

A lightweight server monitoring solution for Windows environments that collects CPU, Memory, and Disk usage metrics from remote machines and displays them through a centralized web dashboard.

---

## 🚀 Overview

This project provides a simple monitoring platform consisting of:

* **Agent Service** running on monitored servers
* **Central Monitoring Dashboard**
* **Historical Resource Tracking**
* **Automatic Alerting System**
* **SMS Notifications**
* **Web-based Management Interface**

The system continuously tracks server health and generates alerts when resource utilization exceeds configured thresholds.

---

## 🏗 Architecture

```text
┌─────────────────┐
│ Monitored Server│
│  Agent Service  │
└────────┬────────┘
         │ HTTP API
         ▼
┌─────────────────┐
│ Monitor Service │
│   Flask App     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Web Dashboard   │
└─────────────────┘

         │
         ▼
┌─────────────────┐
│ SMS Alerting    │
└─────────────────┘
```

---

## 📂 Project Structure

```text
Server_Status/
│
├── agent.py                 # Python monitoring agent
├── agent.ps1                # PowerShell monitoring agent
├── monitor.py               # Central monitoring service
│
├── templates/
│   └── dashboard.html       # Dashboard UI
│
├── servers.json             # Registered servers
├── monitor_result.json      # Monitoring data source
├── monitor.log              # Application logs
│
└── README.md
```

---

## ✨ Features

### Monitoring

* CPU utilization monitoring
* Memory consumption monitoring
* Disk usage monitoring
* Multi-server support
* Per-drive monitoring
* Historical metric tracking

### Dashboard

* Real-time server status
* Auto refresh every 2 seconds
* Resource utilization bars
* Online/Offline detection
* Server management interface

### Alerting

* SMS notifications
* Alert cooldown protection
* Warning and critical states
* Event logging

### API

Agent endpoints:

```http
GET /cpu
GET /memory
GET /disk?drive=D:
```

Example response:

```json
{
  "cpu_percent": 24.5
}
```

```json
{
  "total_gb": 32,
  "used_gb": 18,
  "percent": 56
}
```

---

## ⚙ Requirements

### Python

* Python 3.9+

### Packages

```bash
pip install flask
pip install requests
pip install psutil
pip install apscheduler
```

or

```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration

### Monitor Service

Update configuration values inside `monitor.py`:

```python
DATA_FILE = "servers.json"

MONITOR_RESULT_FILE = r"..."

SMS_COOLDOWN_SECONDS = 300

HISTORY_LIMIT = 30
```

### SMS Provider

Configure your SMS provider settings:

```python
API_KEY = "********"
LINE_NUMBER = "********"
MOBILES = [
    "********"
]
```

---

## ▶ Running Agent

### Python Agent

```bash
python agent.py
```

Default:

```text
http://0.0.0.0:5000
```

---

### PowerShell Agent

```powershell
.\agent.ps1
```

Custom port:

```powershell
.\agent.ps1 -Port 5000
```

---

## ▶ Running Monitor

```bash
python monitor.py
```

Dashboard:

```text
http://localhost:8000
```

---

## 📈 Status Evaluation

The system classifies servers into three states:

### Normal

```text
CPU < 50%
RAM < 70%
Disk < 80%
```

### Warning

```text
CPU >= 50%
RAM >= 70%
Disk >= 80%
```

### Critical

```text
CPU >= 90%
RAM >= 90%
Disk >= 95%
```

---

## 📱 Alerting Rules

SMS alerts are generated when:

```text
RAM >= 80%
OR
CPU >= 90%
OR
Disk >= 90%
```

To prevent notification flooding, a cooldown period is applied:

```text
5 Minutes
```

---

## 🔍 API Endpoints

### Servers

```http
GET /api/servers
POST /api/servers
DELETE /api/servers/<ip>
```

### Monitoring Data

```http
GET /api/status
GET /api/history/<ip>
```

---

## 📝 Logging

Application events are recorded in:

```text
monitor.log
```

Examples:

* High resource usage
* SMS delivery results
* JSON parsing errors
* Server status changes

---

## 🔒 Security Notes

Current implementation is intended for trusted internal networks.

Recommended improvements:

* API authentication
* HTTPS support
* Agent authorization
* Secret management via environment variables
* Firewall restrictions

---

## 📄 License

Internal Company Project

Use and modification are permitted according to organizational policies.
