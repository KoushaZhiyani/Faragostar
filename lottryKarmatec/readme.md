# 🎯 Lottery Customer Data Processing Toolkit

A collection of Python automation scripts used for extracting, cleaning, enriching, and consolidating customer-related data from multiple external platforms and services.

## 📋 Overview

This repository contains several independent data-processing utilities used to:

* Extract customer communication records from external platforms.
* Clean and normalize exported datasets.
* Merge customer information from multiple sources.
* Enrich customer records with geographical information.
* Generate final Excel reports for business analysis and marketing activities.

The project consists of three primary modules:

1. **DadePardaz ETL**
2. **DrClubs ETL**
3. **Neshan Address Enrichment**

---

# 📂 Project Structure

```text
lottryKarmatec/
│
├── APINeshan.py
│
├── DadePardaz/
│   ├── pipline.py
│   ├── data/
│   └── etl/
│       ├── request_dadepardaz.py
│       ├── preprocess_file.py
│       └── merger.py
│
├── Drclubs/
│   ├── pipline.py
│   ├── data/
│   └── etl/
│       ├── request_drclub.py
│       └── preprocess_file.py
│
└── README.md
```

---

# 🔹 DadePardaz ETL

Automates the extraction and processing of incoming SMS records from the DadePardaz messaging platform.

## Workflow

### 1. Data Extraction

`request_dadepardaz.py`

* Authenticates against the DadePardaz platform.
* Retrieves incoming message records using paginated requests.
* Stores raw data as Excel files.

### 2. Data Transformation

`preprocess_file.py`

* Extracts message content from HTML.
* Converts Persian digits to English digits.
* Normalizes phone numbers.
* Filters records by target Persian month.
* Joins message data with customer information.

### 3. Data Consolidation

`merger.py`

* Merges newly processed records with historical datasets.
* Removes duplicate records.
* Produces a consolidated output file.

### Run Complete Pipeline

```bash
python pipline.py
```

---

# 🔹 DrClubs ETL

Automates customer communication report extraction from the DrClubs platform.

## Workflow

### 1. Download Reports

`request_drclub.py`

* Authenticates using platform credentials.
* Downloads customer communication reports.
* Downloads additional customer information reports.

### 2. Data Processing

`preprocess_file.py`

* Loads exported Excel files.
* Filters records by target period.
* Keeps only successfully delivered messages.
* Merges report data with customer master records.
* Generates final Excel outputs.

### Run Complete Pipeline

```bash
python pipline.py
```

---

# 🔹 Neshan Address Enrichment

`APINeshan.py`

Uses the Neshan Search API to enrich customer address information.

## Features

* Reads customer addresses from Excel.
* Queries the Neshan API.
* Detects the most frequently matched neighborhood.
* Populates missing region information.
* Exports enriched customer data.

### Input

```text
MashhadCustomer.xlsx
```

### Output

```text
MashhadCustomer5.xlsx
```

---

# 📊 Data Processing Features

* Excel-based ETL workflows
* Data cleansing and normalization
* Persian-to-English digit conversion
* Phone number standardization
* Customer data enrichment
* Duplicate removal
* Automated report generation
* External API integration

---

# ⚙️ Requirements

```bash
pip install pandas
pip install numpy
pip install requests
pip install openpyxl
pip install selenium
```

---

# 🔐 Configuration

Before running the project, configure the following values:

```python
API_KEY = "YOUR_API_KEY"

USERNAME = "YOUR_USERNAME"

PASSWORD = "YOUR_PASSWORD"
```

Sensitive information such as:

* API Keys
* Usernames
* Passwords
* Internal file paths

should be stored outside the source code and loaded from environment variables whenever possible.

---

# 📁 Generated Files

Typical outputs include:

```text
extract_dadepardaz.xlsx
temp_clean_DadePardaz.xlsx
clean_DadePardaz.xlsx

extract_Drclubs.xlsx
customers_extra.xlsx

MashhadCustomer5.xlsx
```

---

# 🚀 Use Cases

* Customer club analytics
* SMS campaign reporting
* Customer segmentation
* Address enrichment
* Marketing data preparation
* Monthly communication reporting

---

# ⚠️ Notes

* The scripts are designed around specific report formats exported from third-party systems.
* Changes in external platform structures may require updates to extraction logic.
* Large datasets may increase execution time, especially during API enrichment operations.
* Selenium-based extraction requires a compatible Chrome browser and ChromeDriver installation.
