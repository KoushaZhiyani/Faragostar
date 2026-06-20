# 📋 CheckLog - Database Mismatch Monitoring Tool

A lightweight Python utility for monitoring data consistency in a MySQL database.

The script periodically checks a database view (`check_correct_event`) and automatically logs any detected discrepancies into a dedicated logging table (`mismatch_log`).

---

## 🚀 Features

* Connects to a MySQL database
* Checks records from a validation view
* Detects count mismatches automatically
* Stores mismatch history in a log table
* Simple CLI execution
* Easy integration with Windows Task Scheduler, Cron Jobs, or ETL workflows

---

## 📂 Project Structure

```text
CheckLog/
│
├── main.py                # Main monitoring script
└── README.md
```

---

## ⚙️ Requirements

* Python 3.8+
* MySQL Server
* PyMySQL

Install dependencies:

```bash
pip install pymysql
```

---

## 🔧 Database Configuration

Update the database connection settings inside `main.py`:

```python
DB_CONFIG = {
    "host": "...",
    "user": "...",
    "password": "...",
    "database": "...",
    "cursorclass": pymysql.cursors.DictCursor
}
```

---

## 🗄 Expected Database Objects

### Validation View

The script reads data from the following view:

```sql
check_correct_event
```

Expected columns:

| Column  | Description         |
| ------- | ------------------- |
| Name    | Table name          |
| t_count | Actual table count  |
| v_count | Expected/view count |
| Flag    | Validation status   |

Rows with:

```sql
Flag = 0
```

are considered mismatches.

---

### Log Table

Detected mismatches are stored in:

```sql
mismatch_log
```

Example structure:

```sql
CREATE TABLE mismatch_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(255),
    t_count INT,
    v_count INT,
    log_date DATETIME
);
```

---

## ▶️ Running the Script

Execute manually:

```bash
python main.py
```

Example output:

```text
===== Start Check =====

⚠ Mismatch Found:
Table: Orders | t_count=150 | v_count=148

===== End =====
```

If no inconsistencies exist:

```text
===== Start Check =====

✅ No mismatches found

===== End =====
```

---

## 🔄 Recommended Usage

This tool is designed for:

* Data quality monitoring
* ETL validation
* Replication verification
* Scheduled consistency checks
* Operational database health monitoring

Typical deployment methods:

* Windows Task Scheduler
* Cron Jobs
* ETL Pipelines
* Monitoring Servers

---

## 📝 Workflow

```text
Connect to MySQL
        │
        ▼
Read check_correct_event
        │
        ▼
Filter Flag = 0
        │
        ▼
Mismatch Found?
    │         │
   No        Yes
    │         │
    ▼         ▼
 Finish   Insert into
          mismatch_log
```

---

## 📄 License

This project is provided as-is for internal database monitoring and validation purposes.
