import pandas as pd


class CustomerProcessor:
    def __init__(self, generated_path, main_path, recovery_path):
        self.generated_path = generated_path
        self.main_path = main_path
        self.recovery_path = recovery_path
        self.df_generated = None
        self.df_main = None
        self.new_rows = None

    def load_data(self):
        self.df_generated = pd.read_excel(self.generated_path)
        self.df_main = pd.read_excel(self.main_path)

    @staticmethod
    def create_index(df):
        df['index'] = df['PhoneNumber'].astype(int).astype(str) + '_' + df['Name']
        return df

    def add_new_customers(self):
        self.df_main.to_excel('test.xlsx')
        self.df_generated = self.create_index(self.df_generated)
        self.df_main = self.create_index(self.df_main)

        new_rows = self.df_generated[
            ~self.df_generated['index'].isin(self.df_main['index'])
        ]

        self.new_rows = new_rows

        self.df_main = pd.concat([self.df_main, new_rows], ignore_index=True)

    def save(self):
        self.df_main.to_excel(self.main_path, index=False)
        self.df_main.to_excel(self.recovery_path, index=False)



class MashhadCustomerProcessor(CustomerProcessor):
    def __init__(self, generated_path, main_path, region_path, recovery_path):
        super().__init__(generated_path, main_path, recovery_path)
        self.region_path = region_path
        self.region_df = None
        self.new_rows = None

    def load_data(self):
        super().load_data()
        self.region_df = pd.read_excel(self.region_path)

    def merge_region(self):
        if 'RegionNumber' in self.new_rows.columns:
            self.new_rows['trim_region'] = self.new_rows['RegionNumber'].str.replace(
                'محله ', '', regex=False
            )

            self.new_rows = self.df_main.merge(
                self.region_df[['Region', 'Number']],
                left_on='trim_region',
                right_on='Region',
                how='left'
            )

            self.df_main.drop(columns=['Region'], inplace=True)
        self.df_main = pd.concat([self.df_main, self.new_rows], ignore_index=True)

    def add_new_customers(self):
        self.df_generated = self.create_index(self.df_generated)
        self.df_main = self.create_index(self.df_main)

        self.new_rows = self.df_generated[
            ~self.df_generated['index'].isin(self.df_main['index'])
        ]

        # self.df_main = pd.concat([self.df_main, new_rows], ignore_index=True)
