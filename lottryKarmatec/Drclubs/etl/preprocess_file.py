import numpy as np
import pandas as pd
import os
from datetime import datetime

def fa_to_en_digits(row):
    fa_digits = '۰۱۲۳۴۵۶۷۸۹'
    en_digits = '0123456789'
    translation_table = str.maketrans(fa_digits, en_digits)
    row['MessageReceiveTime'] = row['MessageReceiveTime'].translate(translation_table)
    row['MessageReadTime'] = row['MessageReadTime'].translate(translation_table)
    row['MessageContent'] = row['MessageContent'].translate(translation_table)
    return row


current_dir = os.path.dirname(__file__)

base_dir = os.path.dirname(current_dir)
data_dir = os.path.join(base_dir, "data")

# READ File

file_path = os.path.join(data_dir, "extract_Drclubs.xlsx")
df_get = pd.read_excel(file_path)


data_dir_dis = r"Z:/Zhiani/باشگاه مشتریان/"
file_path2 = os.path.join(data_dir_dis, "FileCustomer.xlsx")
df_cus_get = pd.read_excel(file_path2)

# PREPROCESS (Edit Value, Trim, Name Column)
df_get.columns = ['row', 'phone_number', 'date_sent', 'text_sent', 'status']
df_get['Tarikh'] = df_get['date_sent'].astype(str).str[:7]

# print(df_get.iloc[0])

filter_date = "1404/11"
filter_df = df_get[(df_get['Tarikh'] == filter_date) & (df_get['status'].isin(['ارسال شد']))][['phone_number', 'text_sent', 'date_sent']]
filter_df.to_excel('file_path.xlsx', index=False)

df_cus_subset = df_cus_get[['PhoneNumber', 'Name', 'Province']]

df_merged = filter_df.merge(df_cus_subset, left_on='phone_number', right_on='PhoneNumber',how='left')
df_merged.drop('PhoneNumber', axis=1, inplace=True)

file_path_dest = os.path.join(data_dir_dis, f"data/clean_{filter_date.replace("/", "")}_DrClubs.xlsx")

df_merged.to_excel(file_path_dest, index=False)



