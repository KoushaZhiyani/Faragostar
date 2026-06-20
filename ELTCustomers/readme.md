# 📊 ELT Customers Pipeline

Automated ETL pipeline for collecting, cleaning, validating, and maintaining customer data from DrClub reports.

## 📌 Overview

This project automates the process of:

1. Downloading customer reports from the DrClub platform.
2. Extracting and normalizing customer information.
3. Cleaning addresses, cities, and provinces.
4. Generating structured customer datasets.
5. Validating new records against existing customer databases.
6. Updating master customer files and maintaining recovery backups.
7. Assigning Mashhad district information using the Neshan API.

The pipeline is designed to reduce manual data processing and ensure customer databases remain synchronized and up-to-date.

---

## 🏗 Project Structure

```text
ELTCustomers/
│
├── pipline.py                 # Main pipeline runner
├── request_drclub.py          # Downloads customer reports
├── preprocess_file.py         # Data cleaning and transformation
├── validator_data.py          # Validation and merge process
├── APINeshan.py               # Mashhad neighborhood detection
│
├── processors/
│   └── CUstomerProcessorOOP.py
│
├── customers.xlsx
├── customers_extra.xlsx
├── FileCustomer_Research.xlsx
├── Mashhad_Research.xlsx
│
└── log/
    └── customer_processor.log
```

---

## ⚙️ Workflow

### 1. Download Reports

`request_drclub.py`

Logs into the DrClub panel and downloads:

* Customer report
* Additional customer information report

Generated files:

```text
customers.xlsx
customers_extra.xlsx
```

---

### 2. Data Preprocessing

`preprocess_file.py`

Responsibilities:

* Normalize Persian/Arabic characters
* Fix common province naming mistakes
* Clean addresses
* Extract city and province information
* Generate customer datasets
* Remove duplicates
* Create timestamp information

Generated files:

```text
FileCustomer_Research.xlsx
Mashhad_Research.xlsx
```

---

### 3. Customer Validation

`validator_data.py`

Compares generated customer records against existing customer databases and:

* Detects new customers
* Appends missing records
* Creates recovery files
* Generates processing logs

Generated files:

```text
Recovery_FileCustomer.xlsx
Recovery_MashhadCustomer.xlsx
```

Log file:

```text
log/customer_processor.log
```

---

### 4. Mashhad Region Detection

`APINeshan.py`

Uses the Neshan Search API to identify Mashhad neighborhoods based on customer addresses.

Input:

```text
Mashhad_Research.xlsx
```

Output:

```text
MashhadCustomer.xlsx
```

---

## 🚀 Running the Pipeline

Execute the complete workflow:

```bash
python pipline.py
```

Pipeline execution order:

```text
request_drclub.py
      ↓
preprocess_file.py
      ↓
validator_data.py
```

---

## 🔧 Configuration

Before running the project, configure the following values:

### DrClub Credentials

```python
payload = {
    "username": "...",
    "password": "..."
}
```

### Neshan API Key

```python
headers = {
    "Api-Key": "..."
}
```

### Master Customer Files

```python
main_path = r"..."
```

### Region Mapping File

```python
RegionMashad.xlsx
```

---

## 📦 Dependencies

Install required packages:

```bash
pip install pandas numpy requests openpyxl
```

---

## 📝 Output Files

| File                          | Description                     |
| ----------------------------- | ------------------------------- |
| customers.xlsx                | Raw customer export             |
| customers_extra.xlsx          | Additional customer information |
| FileCustomer_Research.xlsx    | Processed customer dataset      |
| Mashhad_Research.xlsx         | Mashhad customers dataset       |
| Recovery_FileCustomer.xlsx    | Customer backup file            |
| Recovery_MashhadCustomer.xlsx | Mashhad customer backup file    |
| customer_processor.log        | Processing logs                 |


---

## 📄 License

This project is intended for internal customer data processing and automation workflows.
