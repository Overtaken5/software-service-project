import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from src.app.product_quantity_forecast.quantity_forecast import *

def plot_prognosis(prognosis_json, start_date, end_date):
    print("Received prognosis_json:", prognosis_json)
    print("Start date:", start_date)
    print("End date:", end_date)
    df = pd.read_json(prognosis_json)
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

    forecasted_data = df[df['actual'] == False]
    plt.plot(forecasted_data['date'], forecasted_data['quantity'], label='Спрогнозированные', color='red',
             linestyle='--', marker='x')
    plt.xlabel('Дата')
    plt.ylabel('Количество')
    plt.title('Прогноз количества товара с {} по {}'.format(start_date, end_date))
    plt.legend()
    plt.xticks(rotation=45)
    filename = f'prognosis_{start_date}_{end_date}.png'
    plt.tight_layout()
    plt.savefig(filename)  # Сохраняем график в файл
    plt.close()  # Закрываем график, чтобы избежать переполнения памяти
    return filename  # Возвращаем путь к файлу

'''
product = Tovar(2, 'name dosn\'t matter')
start = '2021-01-01'
end = '2024-01-01'
prognosis = Prognosis(product, start, end)

# Вызов функции для построения графика
image_path = plot_prognosis(prognosis.get_json_prognosis(), start, end)

# Вернем путь к изображению
print(f'График сохранен как: {image_path}')
'''