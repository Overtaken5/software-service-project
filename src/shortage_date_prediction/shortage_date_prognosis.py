from sre_constants import SUCCESS
import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.linear_model import LinearRegression

class ProductShortage:
    def __init__(self, id, name):
        self.id = id
        self.name = name

'''
class to predict shortage date of a product based on a sufficiently big date 
interval (regulated by __init__.min_interval_l) with no raise of quantity.

Results:
self.get_shortage_date:
  Output: (SUCCESS, shortage_prignosis_date)
    SUCCESS - False, if __init__.min_interval_l is too big or insufficient 
    dataset;
    shortage_prignosis_date - nearest date that is likely to have quantity <= 0.

Requirements:
  ShortagePrognosis.load_dataset sets logic to read dataset and load into self.df 
  pandas dataframe. Function reads currently from Github local directory online.

  Dataset:
  must include 2 columns:
    date: string values in yyyy-mm-dd format;
    quantity: integer values.
'''
class ShortagePrognosis:
    GITHUB_DATASET_DIR = r"https://raw.githubusercontent.com/Overtaken5/software-service-project/refs/heads/master/shortage%20date%20prediction/"
    def __init__(self, product, min_interval_l=7):
        self.product = product
        self.min_interval_l = min_interval_l

        self.load_dataset()
    '''
    dataset requirements:
        "date" - date column in 'yyyy-mm-dd' format
        "quantity" - integer amount of products on the warehouse
    '''
    def load_dataset(self):
        path = ShortagePrognosis.GITHUB_DATASET_DIR + str(self.product.id) + '.csv'
        print(f"Dataset path: {path}")

        df = pd.read_csv(path)
        print(f"Dataset volume: {df.shape}")

        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        self.df = df
  
    '''
    input:
    df: dataframe:
        "date" - datetime column
        "quantity" - amount of products on the warehouse
    specific_date: datetime
    '''
    def get_quantity(self, specific_date):
        df = self.df 
        quantity = df.loc[df['date'] == specific_date, 'quantity'] 
        return quantity.iloc[0] if not quantity.empty else None
  
    '''
    find last date interval of length > 7 days in which 
    no new amount was added to stock

    input:
    df: dataframe:
        "date" - datetime column
        "quantity" - amount of products on the warehouse

    output:
        (start_date, end_date, bool) - date interval to calculate, 
        bool = False: interval can't be calculated
    '''
    def find_last_interval(self, min_l=7):
        df = self.df
        end_date = df['date'].max()
        current_date = df['date'].max()
    
        while True:
            # at the end of the whole date range
            if current_date == df['date'].min():
                if (end_date - current_date).days >= min_l:
                    break
                # no interval with length of >= min_l
                return (False, current_date, end_date)
      
            prev_day = current_date - timedelta(days=1)
      
            if self.get_quantity(prev_day) < self.get_quantity(current_date):
                # found suitable date range
                if (end_date - current_date).days >= min_l:
                    break
                # new interval lookup
                else:
                    end_date = prev_day
      
            current_date = prev_day
      
        return (True, current_date, end_date)

    '''
    finds average quantity consumed each day in the interval

    input:
    df: dataframe:
        "date" - datetime column
        "quantity" - amount of products on the warehouse
    start_date, end_date - interval to build model, both are type of datetime

    output:
        float - slope, average quantity consumed each day in the interval
    '''
    def get_slope(self, start_date, end_date):
        df = self.df
        df_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()

        # Convert 'date' to numeric ordinal value for regression
        df_filtered['date_ordinal'] = df_filtered['date'].map(pd.Timestamp.toordinal)

        # Prepare the data for Linear Regression
        X = df_filtered[['date_ordinal']]
        y = df_filtered['quantity']

        # Initialize and fit the model
        model = LinearRegression()
        model.fit(X, y)

        # Extract parameters
        slope = model.coef_[0]

        return float(slope)
  
    '''
    Output: (SUCCESS, shortage_prignosis_date)
        SUCCESS - False, if __init__.min_interval_l is too big or insufficient 
        dataset;
        shortage_prignosis_date - nearest date that is likely to have quantity <= 0.
    '''
    def get_shortage_date(self):
        df = self.df

        if df.shape[0] < self.min_interval_l:
            print(f"Insufficient to calculate prediction for the given min_interval_l={self.min_interval_l}")
            return (False, '2000-01-01')

        # get interval to prepare prediction model
        SUCCESS, start_date, end_date = self.find_last_interval(min_l=self.min_interval_l)

        # check if it's there's enough data to predict for the given paramether
        if not SUCCESS:
            print(f"There's no big enough date interval to calculate prediction " + \
                  f"for the given min_interval_l={self.min_interval_l}")
            return (False, '2000-01-01')

        # get prediction model's paramether
        slope = self.get_slope(start_date, end_date)

        # calculate 
        current_quantity = self.get_quantity(df['date'].max())
        days_left = np.ceil(current_quantity / abs(slope))
        shortage_date = df['date'].max() + timedelta(days=days_left)
        return (True, shortage_date.strftime('%Y-%m-%d'))

