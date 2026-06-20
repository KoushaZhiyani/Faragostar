import pandas as pd
import os

current_dir = os.path.dirname(__file__)
base_dir = os.path.dirname(current_dir)
data_dir = os.path.join(base_dir, "data")


file_path = os.path.join(data_dir, "clean_DadePardaz.xlsx")
df = pd.read_excel(file_path)

file_path2 = os.path.join(data_dir, "temp_clean_DadePardaz.xlsx")
temp_df = pd.read_excel(file_path2)


df = pd.concat([df, temp_df])
df.drop_duplicates(inplace=True)



file_dest = os.path.join(data_dir, "clean_DadePardaz.xlsx")
df.to_excel(file_dest, index=False)
