import requests
import pandas as pd
import json
from collections import Counter
import time


def get_add(row):
    time.sleep(1)
    params = {
        "term": row['Address'],
        "lat": 36.2972,
        "lng": 59.6067
    }
    response = session.get(url, headers=headers, params=params)
    most_number = get_most_number(response)
    return most_number


def get_most_number(response):

    if response.status_code != 200:
        print("HTTP Error:", response.status_code)
        return None
    print(response.status_code)

    try:
        data = response.json()
    except Exception as e:
        print("JSON error:", e)
        print("Response text:", response.text)
        return None


    items = data.get("items", [])
    if not items:
        return None

    df = pd.json_normalize(items)

    # محله‌ها
    neighs = df["neighbourhood"].dropna()
    neighs = neighs[neighs != ""]

    if neighs.empty:
        return None

    counts = Counter(neighs)
    most_common_neigh, freq = counts.most_common(1)[0]
    return most_common_neigh


session = requests.Session()

url = "https://api.neshan.org/v1/search"
headers = {
    "Api-Key": "service.82d7d9abd..."
}

df = pd.read_excel(r'....xlsx')


filter_df = df[df['RegionNumber'].isna()]

filter_df['RegionNumber'] = filter_df.apply(lambda row:get_add(row), axis=1)

filter_df.to_excel('MashhadCustomer5.xlsx', index=False)