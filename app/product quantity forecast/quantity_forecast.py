import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

'''
    Возвращает датафрейм в формате дата (год-месяц) и число остатков на заданный промжуток.
    Выполняет прогноз числа остатков, если требуемых дат нет в датасете.

    Входные данные:
    df - датафрейм со столбацами 'date' (datetime формата ггг-мм-01), 'quantity' (integer);
    start_date - дата с которой требуются данные об остатках;
    end_date - дата до которой требуются данные об остатках.

    Выходные данные:
    filtered_df - датафрейм со столбацами 'date' (datetime формата ггг-мм-01), 'quantity' (integer).
'''
def filter_and_extrapolate(df, start_date, end_date):
    # Ensure the dates are in datetime format
    start_date = pd.to_datetime(start_date, format='%Y-%m-%d')
    end_date = pd.to_datetime(end_date, format='%Y-%m-%d')
    
    # Filter by chosen sub-category
    filtered_df = df.copy()
    
    # Convert 'Order Date' to datetime if it's not already
    filtered_df['date'] = pd.to_datetime(filtered_df['date'], format='%Y-%m')

    max_actual_date = max(filtered_df['date'])
    
    # Filter by date range
    filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]
    
    # If max date is less than the end date, extrapolate using Prophet
    if filtered_df.empty or filtered_df['date'].max() < end_date:
        # Prepare data for Prophet
        df_prophet = df[['date', 'quantity']].rename(columns={'date': 'ds', 'quantity': 'y'})
        
        # Initialize and fit Prophet model
        model = Prophet()
        model.fit(df_prophet)
        
        # Create future dates up to the end_date
        max_date = df_prophet['ds'].max()
        periods = (end_date.year - max_date.year) * 12 + (end_date.month - max_date.month)
        future = model.make_future_dataframe(periods=periods, freq='M')
        
        # Forecast
        forecast = model.predict(future)

        # Adjust forecast dates to the first of each month
        forecast['ds'] = forecast['ds'].apply(lambda x: x.replace(day=1))
        
        # Append new forecasts to filtered DataFrame
        forecast_needed = forecast[(forecast['ds'] > max_actual_date) & (forecast['ds'] <= end_date)][['ds', 'yhat']]
        forecast_needed = forecast_needed.rename(columns={'ds': 'date', 'yhat': 'quantity'})
        
        filtered_df = pd.concat([filtered_df, forecast_needed], ignore_index=True)
        
    return filtered_df[['date', 'quantity']]

'''
    Строит временной график остатков продукта. 
    Прогнозированный временной интервал будет прорисован красной линией, а исходные данные - синей.
    
    Входные данные:
    df - датафрейм со столбацами 'date' (datetime формата ггг-мм-01), 'quantity' (integer);
    product_name - название продукта. На прогноз не влияет. Будет выведен на графике.
    start_date - дата с которой требуются данные об остатках;
    end_date - дата до которой требуются данные об остатках.

    Выходные данные:
    Отсутствуют.
'''
def plot_data(df, product_name, start_date, end_date):
    # Filter and extrapolate data
    result_df = filter_and_extrapolate(df, start_date, end_date)
    
    # Separate actual data and predictions
    max_actual_date = max(df['date'])
    actual_data = result_df[result_df['date'] <= max_actual_date]
    predicted_data = result_df[result_df['date'] >= max_actual_date]
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(actual_data['date'], actual_data['quantity'], label='Actual Data', color='blue')
    plt.plot(predicted_data['date'], predicted_data['quantity'], label='Predictions', color='red')
    plt.title(f'Distribution of Quantity for {product_name} Over Time')
    plt.xlabel('Date')
    plt.ylabel('Quantity')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage:

# plot_data(chairs_df, 'Chairs', '2018-07-01', '2025-07-31')