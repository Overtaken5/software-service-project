import pandas as pd
from prophet import Prophet
import datetime

class Product:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Prognosis:
    # template link to datasets for prognosis
    LOCAL_FILE = r'https://raw.githubusercontent.com/Overtaken5/software-service-project/refs/heads/master/datasets/product_id.csv'
    '''
    product - instance of Tovar class
    start_date, end_date - string in yyyy-mm-dd format
    '''
    def __init__(self, product, start_date, end_date):
        self.product = product
        self.start_date = start_date
        self.end_date = end_date

        # dataframe that stores prognosis results
        self.series_df = None
    
    # get a dataset to train a forecast model
    def get_train_dataset(self):
        product_id = self.product.id
        df = pd.read_csv(Prognosis.LOCAL_FILE.replace('product_id', str(product_id)))

        # prepare for filter_and_extrapolate function (read its comment above)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df['date'] = df['date'].dt.to_period('M').dt.to_timestamp()

        return df

    # returns False if it's impossible to retrieve or forecast 
    # for the given dates based on train data
    def is_prognosable(self):
        if pd.to_datetime(self.start_date, format='%Y-%m-%d').replace(day=1) < self.get_train_dataset()['date'].min():
            return False
        else:
            return True

    # form series of prognose for the given dates
    def prognose(self):
        series_train_df = self.get_train_dataset()
        series_df = Prognosis.filter_and_extrapolate(series_train_df, self.start_date, self.end_date)
        self.series_df = series_df
    
    # return a json object of series
    # each internal json represents a row in a dataframe
    def get_json_prognosis(self):
        # check if it's possible to prognose/retrieve data
        if self.is_prognosable() == False:
            min_date = self.get_train_dataset()['date'].min()
            raise Exception(f'Prognosis date must be at least {min_date}.')
            return None
        
        # set up prognose if not done yet
        if self.series_df is None:
            self.prognose()
        
        return self.series_df.to_json(orient='records')

    '''
        Возвращает датафрейм в формате дата (год-месяц) и число остатков на заданный промжуток.
        Выполняет прогноз числа остатков, если требуемых дат нет в датасете.

        Входные данные:
        df - датафрейм со столбацами 'date' (datetime формата ггг-мм-01), 'quantity' (integer);
        start_date - дата с которой требуются данные об остатках;
        end_date - дата до которой требуются данные об остатках.

        Выходные данные:
        filtered_df - датафрейм со столбацами 
            'date' (строчного формата ггг-мм-01); 
            'quantity' (integer);
            'actual' (True - исходные данные таблицы, False - спрогнозированные данные).
    '''
    def filter_and_extrapolate(df, start_date, end_date):
        # Ensure the dates are in datetime format
        start_date = pd.to_datetime(start_date, format='%Y-%m-%d').replace(day=1)
        end_date = pd.to_datetime(end_date, format='%Y-%m-%d').replace(day=1)

        filtered_df = df.copy()

        # Convert 'date' to datetime if it's not already
        filtered_df['date'] = pd.to_datetime(filtered_df['date'], format='%Y-%m')

        max_actual_date = max(filtered_df['date'])

        # Filter by date range
        filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]

        # label actual data
        filtered_df['actual'] = True

        # If max date is less than the end date, extrapolate using Prophet
        if filtered_df.empty or filtered_df['date'].max() < end_date:
            # Prepare data for Prophet
            df_prophet = df[['date', 'quantity']].rename(columns={'date': 'ds', 'quantity': 'y'})

            # Initialize and fit Prophet model
            model = Prophet()
            model.fit(df_prophet)

            # Create future dates up to the end_date
            max_date = df_prophet['ds'].max()
            periods = (end_date.year - max_date.year) * 12 + (end_date.month - max_date.month) + 1
            future = model.make_future_dataframe(periods=periods, freq='M')

            # Forecast
            forecast = model.predict(future)

            # Adjust forecast dates to the first of each month
            forecast['ds'] = forecast['ds'].apply(lambda x: x.replace(day=1))

            # Append new forecasts to filtered DataFrame
            forecast_needed = forecast[(forecast['ds'] > max_actual_date.replace(day=1)) & (forecast['ds'] <= end_date)][['ds', 'yhat']]
            forecast_needed = forecast_needed.rename(columns={'ds': 'date', 'yhat': 'quantity'})

            # label forecasted data
            forecast_needed['actual'] = False

            # filter data by date
            filtered_df = pd.concat([filtered_df, forecast_needed], ignore_index=True)
            filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]
        
        filtered_df['date'] = pd.to_datetime(filtered_df['date'], unit='ms').dt.strftime('%Y-%m-%d')
        filtered_df['quantity'] = filtered_df['quantity'].round().astype(int)

        return filtered_df[['date', 'quantity', 'actual']]

# Пример формирования JSON прогноза

# Устанавливаем нужную библиотеку через консоль, если не установлена:
# pip install prophet

# Нужно инцициализировать объект класса Tovar
# Он уже реализован в данном файле 
# Объект Tovar обязательно должен иметь свойства id (int) и name (string)
# product.id можно выбрать между [1, 7]
product = Product(2, 'name doesn\'t matter')

# Нужно определить период прогноза в формате yyyy-mm-01
# Прогноз будет по месяцам, поэтому день не важен
start = '2014-01-01'
end = '2018-06-01'

# Инициализируем сам объект Prognosis с определенными параметрами
# Данные для прогноза загружает из интернета, поэтому никакие файлы себе скачивать не нужно
prognosis = Prognosis(product, start, end)

"""
Выводит список из json (string)
Формат каждого json элемента в списке:
{
    "date": дата формата yyyy-mm-01 (string), 
    "quantity": остаток на эту дату (int), 
    "actual": true, если данные взяты из датасета, false, если это прогноз. 
        Скорее всего у вас всегда будет actual = false, потому что вам интересен прогноз (bool)
}
"""
result = prognosis.get_json_prognosis()
print(result)

# Прочитаем один элемент из списка
import json
list_of_result = json.loads(result)
print('1st element:', list_of_result[0])
print('1st element\'s quantity:', list_of_result[0]['quantity'])