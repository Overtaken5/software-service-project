import matplotlib.pyplot as plt
import pandas as pd
from quantity_forecast import *

def plot_prognosis(prognosis_json, start_date, end_date):
    # Преобразуем JSON данные в DataFrame
    df = pd.read_json(prognosis_json)

    # Преобразуем столбец 'date' в формат datetime
    df['date'] = pd.to_datetime(df['date'])

    # Фильтруем данные по введенным датам
    df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

    # Разделим данные на фактические и спрогнозированные
    actual_data = df[df['actual'] == True]
    forecasted_data = df[df['actual'] == False]

    # Построим график для фактических данных
    plt.figure(figsize=(10, 6))
    plt.plot(actual_data['date'], actual_data['quantity'], label='Фактические', color='blue', marker='o')

    # Построим график для спрогнозированных данных
    plt.plot(forecasted_data['date'], forecasted_data['quantity'], label='Спрогнозированные', color='red',
             linestyle='--', marker='x')

    # Добавим подписи осей и название графика
    plt.xlabel('Дата')
    plt.ylabel('Количество')
    plt.title('Прогноз количества товара с {} по {}'.format(start_date, end_date))
    plt.legend()

    # Повернем подписи на оси X для лучшей читаемости
    plt.xticks(rotation=45)

    # Сохраняем график как PNG
    filename = f'prognosis_{start_date}_{end_date}.png'
    plt.tight_layout()
    plt.savefig(filename)  # Сохраняем график в файл
    plt.show()  # Отображаем график

    # Возвращаем путь к файлу с изображением
    return filename


# Пример использования:
# Предположим, что prognosis.get_json_prognosis() возвращает данные в формате JSON

product = Product(2, 'name dosn\'t matter')
start = '2020-01-01'
end = '2024-01-01'
prognosis = Prognosis(product, start, end)
print(prognosis.get_json_prognosis())

# Вызов функции для построения графика
image_path = plot_prognosis(prognosis.get_json_prognosis(), start, end)

# Вернем путь к изображению
print(f'График сохранен как: {image_path}')