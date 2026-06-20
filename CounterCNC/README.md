# CounterCNC

A CNC board monitoring and data logging system designed to collect production data from multiple CNC devices over TCP, store decoded packets in a SQLite database, and provide a real-time web dashboard for monitoring machine activity.

---

## Overview

CounterCNC receives binary packets from CNC controller boards, decodes production events, stores raw logs in a database, and provides monitoring and reporting capabilities through a web dashboard.

The system consists of:

* TCP Server for receiving board data
* Packet Decoder
* SQLite-based data storage
* Real-time Monitoring Dashboard
* Excel Export Module
* Network Watchdog Service
* Production Session Processor

---

## Features

### Real-Time CNC Monitoring

* Monitor multiple CNC boards simultaneously
* Track board connection status
* Display latest received packet information
* View board activity through a web dashboard

### Packet Processing

Supports decoding of:

| Packet ID | Description              |
| --------- | ------------------------ |
| 0x01      | Session Start            |
| 0x02      | Production Count         |
| 0x03      | Session End / Stop Codes |
| 0x04      | Scrap & Rework Data      |
| 0x05      | Forms Data               |

### Database Logging

* Stores all decoded packets in SQLite
* Uses WAL mode for better write performance
* Background queue-based database insertion
* Batch processing support

### Session Management

Automatically:

* Creates production sessions
* Tracks quantities
* Records scrap and rework
* Stores form information
* Handles out-of-order packets
* Recovers from temporary network interruptions

### Network Watchdog

Continuously monitors CNC board availability:

* Periodically pings all configured boards
* Detects network-wide outages
* Detects network recovery events
* Inserts recovery markers into the database

### Excel Export

Export production session data by date range directly from the dashboard.

---

## Project Structure

```text
CounterCNC/
│
├── main.py                 # TCP Server
├── dashboard.py            # Flask Dashboard
├── test_decoder.py         # Packet Decoder & Database Writer
├── session_processor.py    # Production Session Builder
├── network_watchdog.py     # Network Monitoring Service
├── run_script.bat          # Startup Script
│
├── templates/
│   ├── index.html
│   └── export.html
│
└── database.db
```

---

## Requirements

Install dependencies:

```bash
pip install flask pandas openpyxl requests
```

---

## Configuration

Before running the application, update the configuration values according to your environment.

### TCP Server

```python
self.host = "..."
self.port = 100
```

### Database Path

```python
DB_PATH = "..."
```

### CNC Board IP List

```python
BOARD_IPS = [
    "...",
    "...",
    "..."
]
```

### SMS Service Configuration (Optional)

```python
url = "..."
headers = {
    "X-API-KEY": "..."
}
```

---

## Running

### Start all services

```bash
run_script.bat
```

Or manually:

```bash
python main.py
```

```bash
python network_watchdog.py
```

---

## Dashboard

After startup, open:

```text
http://localhost:5000
```

Available pages:

| Route             | Description          |
| ----------------- | -------------------- |
| /                 | Monitoring Dashboard |
| /export-page      | Excel Export Page    |
| /api/boards       | Board Status API     |
| /api/export-excel | Excel Export API     |

---

## Data Flow

```text
CNC Boards
      │
      ▼
 TCP Server
      │
      ▼
 Packet Decoder
      │
      ▼
 SQLite WAL Storage
      │
      ▼
 Session Processor
      │
      ▼
 Production Sessions
      │
      ▼
 Dashboard / Excel Export
```

---

## Session Processing Logic

The session processor:

1. Receives decoded packets from WAL storage.
2. Creates production sessions from Packet 0x01.
3. Updates production quantity using Packet 0x02.
4. Updates scrap and rework using Packet 0x04.
5. Stores form information from Packet 0x05.
6. Closes sessions using Packet 0x03.
7. Handles delayed packets after network recovery events.

---

## Logging

The application generates logs for:

* Client connections
* Client disconnections
* Packet reception
* Network outages
* Network recovery events
* Database processing

---

## License

This project is intended for internal industrial monitoring and production tracking purposes.
