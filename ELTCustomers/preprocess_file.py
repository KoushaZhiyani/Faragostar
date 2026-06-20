import numpy as np
import pandas as pd
import re
from datetime import datetime

# Dicts & Functions

provinces = [
    "آذربایجان شرقی",
    "آذربایجان غربی",
    "اردبیل",
    "اصفهان",
    "البرز",
    "ایلام",
    "بوشهر",
    "تهران",
    "چهارمحال و بختیاری",
    "خراسان جنوبی",
    "خراسان رضوی",
    "خراسان شمالی",
    "خوزستان",
    "زنجان",
    "سمنان",
    "سیستان و بلوچستان",
    "فارس",
    "قزوین",
    "قم",
    "کردستان",
    "کرمان",
    "کرمانشاه",
    "کهگیلویه و بویراحمد",
    "گلستان",
    "گیلان",
    "لرستان",
    "مازندران",
    "مرکزی",
    "هرمزگان",
    "همدان",
    "یزد"
]


false_value = {
    "خراسن  رضوی": "خراسان رضوی",
    "مشهد": "خراسان رضوی",
    "مارندران": "مازندران",
    "گلستان شهرستان کردکوی": "گلستان",
    "سیستا ن بلوچستان": "سیستان و بلوچستان",
    "سیستان بلوچستان": "سیستان و بلوچستان",
    "سیستان وبلوچستان": "سیستان و بلوچستان",
    "خراسان‌رضوي": "خراسان رضوی",
    "خراسان‌رضوی": "خراسان رضوی",
    "خراسان رضویی": "خراسان رضوی",
    "خراسان رضویه": "خراسان رضوی",
    "خراسان رضویمشهد": "خراسان رضوی",
    "خرسان رضوی": "خراسان رضوی",
    "خراسان رضچی": "خراسان رضوی",
    "آذربایجانغربی": "آذربایجان غربی",
    ",آ. غ": "آذربایجان غربی",
    "اورمیه": "آذربایجان غربی",
    "استان سیستان بلوچستان": "سیستان و بلوچستان",
    "ا. غ": "خراسان رضوی",
    ",خراسان رضوی": "خراسان رضوی",
    "اذربایجانغربی": "خراسان رضوی",
    "استان سیستان و بلوچستان": "خراسان رضوی",
    "خراسان رصوی": "خراسان رضوی",
    "خراسان رضویخراسان رضوی": "خراسان رضوی",
    "گیاتن": "خراسان رضوی",
    "خرسان شمالی": "خراسان شمالی",


}

def strip_value(row):
    return  row.strip().replace("-", " ")

def normalize_arabic_to_persian(text: str) -> str:
    mapping = {
        'ك': 'ک',   # arabic kaf -> persian kaf
        'ي': 'ی',   # arabic yeh -> persian ye
        'ة': 'ه',   # taa marbuta -> heh
        'أ': 'ا',   # alef with hamza -> alef
        'إ': 'ا',
        'آ': 'ا',
    }
    # تبدیل با یک حلقه ساده
    for a, p in mapping.items():
        text = text.replace(a, p)
    return text

def false_city(row: str) -> str:
    if row['عنوان'] == 'استان':
        for a, p in false_value.items():
            row['محتوا'] = row['محتوا'].replace(a, p)

    return row


def transform(row, df):
    if len(df[df['نام مشتری'] == row['Name']]) > 0:

        return df[df['نام مشتری'] == row['Name']].values[0][4]

    else:
        return np.nan


def extract_city(row):

    if pd.isna(row['City']):
        for c in City_df['City']:
            if pd.notna(c):
                pattern = r'\b' + re.escape(c) + r'\b'
                if re.search(pattern, row['Address']):
                    return c

        province = extract_province_in_city(row)



        if pd.isna(row['Province']) and pd.isna(province):
            return "احتمالا مشهد"

        elif not pd.isna(row['Province']):
            return f"شهرستانی در {row['Province']}"

        elif not pd.isna(province):
            return  f"شهرستانی در {province}"


    else:

        return row['City']


def extract_province_in_city(row):

    for c in provinces:
        pattern = r'\b' + re.escape(c) + r'\b'
        if re.search(pattern, row['Address']):
            return c
    return np.nan



def extract_province(row):
    if pd.isna(row['Province']):


        for c in provinces:

            pattern = r'\b' + re.escape(c) + r'\b'

            if re.search(pattern, row['Address']):
                return c

        city = row['City']
        if not pd.isna(city):

            province = City_df.loc[City_df['City'] == city, 'Province'].tolist()
            province = province[0] if province else np.nan

            if pd.isna(province):

               return "احتمالا خراسان رضوی"
            else:

               return province

        else:
            return "احتمالا خراسان رضوی"

    return row['Province']

# READ File

df_get = pd.read_excel('customers_extra.xlsx')
City_df = pd.read_excel('listofCity.xlsx')
# PREPROCESS (Edit Value, Trim, Name Column)

df_get['محتوا'] = (
    df_get['محتوا']
    .fillna("")
    .astype(str)
    .apply(strip_value)
    .apply(normalize_arabic_to_persian)
)
df_get['شماره مشتری'] = "0" + df_get['شماره مشتری'].fillna('').astype(str)



df_get =  df_get.apply(lambda row: false_city(row), axis=1)
# df_get = df_get[df_get['نام مشتری'].isin(['مجتبی  عسگری', ' رسول یزدانی', ' کاریزکی'])]

df_processed = df_get.copy()

# TRANSFORM DATA (X->Y)



output_df = pd.DataFrame(columns=['Name', 'PhoneNumber' ,'Address'])




df_filtered = df_processed[['نام مشتری', 'شماره مشتری', 'محتوا']][df_processed['عنوان'] == 'آدرس'].copy()

df_filtered.columns = ['Name', 'PhoneNumber', 'Address']
df_filtered.drop_duplicates(subset=['Name', 'PhoneNumber', 'Address'], inplace=True)



df_filtered['Province'] = df_filtered.apply(lambda row: transform(row, df_processed[df_processed['عنوان'] == 'استان']), axis=1)
df_filtered['City'] = df_filtered.apply(lambda row: transform(row, df_processed[df_processed['عنوان'] == 'شهر']), axis=1)
df_filtered['Job'] = df_filtered.apply(lambda row: transform(row, df_processed[df_processed['عنوان'] == 'شغل']), axis=1)
df_filtered['CartNum'] = df_filtered.apply(lambda row: transform(row, df_processed[df_processed['عنوان'] == 'شماره کارت']), axis=1)
df_filtered['PostCode'] = df_filtered.apply(lambda row: transform(row, df_processed[df_processed['عنوان'] == 'کدپستی(لطفاً کدپستی آدرس دریافت بسته را ارسال نمایید)']), axis=1)

# EXTRACT City Province

df_filtered['City'] = df_filtered.apply(lambda row: extract_city(row), axis=1)
df_filtered['Province'] = df_filtered.apply(lambda row: extract_province(row), axis=1)


# HASH For Editing in future

now = datetime.now()
formatted_date = now.strftime("%Y-%m-%d")

df_filtered['TimeAdded'] = formatted_date
df_filtered['sum_na'] = df_filtered.isna().sum(axis=1)

mashhad_df = df_filtered[(df_filtered['Province'].str.contains('خراسان')) & (df_filtered['City'].str.contains('مشهد'))]

####

# SAVE Data File
df_filtered.to_excel(r'FileCustomer_Research.xlsx', index=False)
mashhad_df.to_excel(r'Mashhad_Research.xlsx', index=False)
