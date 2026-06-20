import numpy as np
import pandas as pd
import re
import os
from datetime import datetime


def extract_message(html):
        if not html:
            return ""

        matches = re.findall(
            r"<p[^>]*>(.*?)</p>",
            html,
            flags=re.DOTALL | re.IGNORECASE
        )
        return " | ".join(m.strip() for m in matches)


def fa_to_en_digits(row):
    fa_digits = '۰۱۲۳۴۵۶۷۸۹'
    en_digits = '0123456789'
    translation_table = str.maketrans(fa_digits, en_digits)
    row['MessageReceiveTime'] = row['MessageReceiveTime'].translate(translation_table)
    row['MessageContent'] = row['MessageContent'].translate(translation_table)
    row['PhoneNumber'] = row['PhoneNumber'].translate(translation_table)
    return row

current_dir = os.path.dirname(__file__)
base_dir = os.path.dirname(current_dir)
data_dir = os.path.join(base_dir, "data")

# READ File
file_path = os.path.join(data_dir, "extract_dadepardaz.xlsx")
df = pd.read_excel(file_path)


df.columns = ['row', 'PhoneNumber', 'text_sent','MessageReceiveTime' , 'col5','MessageContent']
df["MessageContent"] = df["MessageContent"].apply(extract_message)



df = df.apply(lambda row: fa_to_en_digits(row), axis=1)

df['Tarikh'] = df['MessageReceiveTime'].str.extract(r'(\d{4}/\d{2})')
df['PhoneNumber'] = (
    df['PhoneNumber']
    .astype(str)
    .str.replace(r'^98', '', regex=True)
)

df.drop(columns=['MessageReceiveTime'], inplace=True)


file_path2 = os.path.join(data_dir, "FileCustomer.xlsx")
df_cus_get = pd.read_excel(file_path2)

# PREPROCESS (Edit Value, Trim, Name Column)



filter_df = df[(df['Tarikh'] == "1404/10")]
print(filter_df)
input()
df_cus_subset = df_cus_get[['PhoneNumber', 'Name', 'Province']]

df_cus_subset = df_cus_subset.copy()

df_cus_subset["PhoneNumber"] = df_cus_subset["PhoneNumber"].astype(str)

df_merged = filter_df.merge(df_cus_subset, on='PhoneNumber',how='left')


df_merged.drop_duplicates(subset=['PhoneNumber', 'MessageContent'], inplace=True)

df_merged.drop(['row', 'text_sent' ,'col5'], axis=1, inplace=True)



file_path_dest = os.path.join(data_dir, "temp_clean_DadePardaz.xlsx")
df_merged.to_excel(file_path_dest, index=False)




