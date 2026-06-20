import numpy as np
from processors.CUstomerProcessorOOP import CustomerProcessor, MashhadCustomerProcessor
import os
import logging
import pandas as pd
from pathlib import Path
# ساخت فولدر log در صورت نیاز
if not os.path.exists('log'):
    os.makedirs('log')

# Logger اصلی
logger = logging.getLogger("CustomerLogger")
logger.setLevel(logging.INFO)  # سطح لاگ

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# FileHandler (ذخیره در فایل)
file_handler = logging.FileHandler('log/customer_processor.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# StreamHandler (نمایش روی کنسول)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.info("Start Processing CustomerProcessor")
df= pd.read_excel('FileCustomer_Research.xlsx')

customer_processor = CustomerProcessor(
    generated_path='FileCustomer_Research.xlsx',
    main_path=r'Z:/Zhiani/باشگاه مشتریان/FileCustomer.xlsx',
    recovery_path='Recovery_FileCustomer.xlsx'
)

customer_processor.load_data()
customer_processor.add_new_customers()
customer_processor.save()

logger.info("Finish Processing CustomerProcessor")

if  isinstance(customer_processor.new_rows, pd.DataFrame):
    if not customer_processor.new_rows.empty:
        logger.info(f"Row Added: {customer_processor.new_rows}")



logger.info("Start Processing MashhadCustomerProcessor")

BASE_DIR = Path(__file__).resolve().parent
region_path = BASE_DIR / "RegionMashad.xlsx"

mashhad_processor = MashhadCustomerProcessor(
    generated_path='Mashhad_Research.xlsx',
    main_path=r'Z:/Zhiani/باشگاه مشتریان/MashhadCustomer.xlsx',
    region_path=region_path,
    recovery_path='Recovery_MashhadCustomer.xlsx'

)


mashhad_processor.load_data()
mashhad_processor.add_new_customers()
mashhad_processor.merge_region()
mashhad_processor.save()




logger.info("End Processing MashhadCustomerProcessor")


if  isinstance(mashhad_processor.new_rows, pd.DataFrame):
    if not mashhad_processor.new_rows.empty:
        logger.info(f"Row Added: {mashhad_processor.new_rows}")
