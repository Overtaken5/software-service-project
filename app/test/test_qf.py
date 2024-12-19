import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys, os

# Путь к модулю
sys.path.append(os.path.join(os.getcwd(), '..', 'product_quantity_forecast'))

# Теперь можно использовать ваш модуль
from quantity_forecast import Product, Prognosis

# Создаем фикстуры для объектов
@pytest.fixture
def product():
    return Product(2, 'name doesn\'t matter')

@pytest.fixture
def prognosis(product):
    return Prognosis(product, '2014-01-01', '2018-06-01')

# Тестирование метода get_train_dataset
@patch('pandas.read_csv')
def test_get_train_dataset(mock_read_csv, prognosis):
    # Создаем фейковый DataFrame
    mock_df = pd.DataFrame({
        'date': ['2014-01-01', '2014-02-01'],
        'quantity': [10, 20]
    })
    mock_read_csv.return_value = mock_df

    # Вызов метода
    df = prognosis.get_train_dataset()

    # Проверка корректности обработки данных
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert df['date'].dtype == 'datetime64[ns]'
    assert df['quantity'].dtype == 'int64'

# Тестирование метода is_prognosable
@patch.object(Prognosis, 'get_train_dataset')
def test_is_prognosable(mock_get_train_dataset, prognosis):
    # Мокаем возвращаемое значение для get_train_dataset
    mock_df = pd.DataFrame({
        'date': ['2014-01-01', '2014-02-01'],
        'quantity': [10, 20]
    })
    mock_get_train_dataset.return_value = mock_df

    # Проверка, когда прогнозировать можно
    assert prognosis.is_prognosable() is True

    # Проверка, когда прогнозировать нельзя
    prognosis.start_date = '2010-01-01'
    assert prognosis.is_prognosable() is False

# Тестирование метода prognose
@patch.object(Prognosis, 'get_train_dataset')
@patch('prophet.Prophet')
def test_prognose(mock_prophet, mock_get_train_dataset, prognosis):
    # Мокаем возвращаемое значение для get_train_dataset
    mock_df = pd.DataFrame({
        'date': ['2014-01-01', '2014-02-01'],
        'quantity': [10, 20]
    })
    mock_get_train_dataset.return_value = mock_df

    # Мокаем работу Prophet
    mock_model = MagicMock()
    mock_model.fit.return_value = None
    mock_model.make_future_dataframe.return_value = pd.DataFrame({'ds': pd.to_datetime(['2018-07-01'])})
    mock_model.predict.return_value = pd.DataFrame({
        'ds': pd.to_datetime(['2018-07-01']),
        'yhat': [25]
    })
    mock_prophet.return_value = mock_model

    # Вызов метода prognose
    prognosis.prognose()

    # Проверка, что series_df был заполнен
    assert prognosis.series_df is not None
    assert prognosis.series_df.shape[0] > 0

# Тестирование метода get_json_prognosis
@patch.object(Prognosis, 'is_prognosable')
@patch.object(Prognosis, 'prognose')
def test_get_json_prognosis(mock_prognose, mock_is_prognosable, prognosis):
    # Мокаем is_prognosable, чтобы возвращал True
    mock_is_prognosable.return_value = True

    # Мокаем прогноз
    mock_prognose.return_value = None
    prognosis.series_df = pd.DataFrame({
        'date': ['2014-01-01', '2014-02-01'],
        'quantity': [10, 20],
        'actual': [True, True]
    })

    # Вызов метода
    json_result = prognosis.get_json_prognosis()

    # Проверка, что результат корректный
    assert isinstance(json_result, str)  # JSON должен быть строкой
    assert 'date' in json_result
    assert 'quantity' in json_result

# Тестирование исключений
@patch.object(Prognosis, 'is_prognosable')
def test_get_json_prognosis_exception(mock_is_prognosable, prognosis):
    # Мокаем is_prognosable, чтобы возвращал False
    mock_is_prognosable.return_value = False

    # Проверка, что исключение выбрасывается
    with pytest.raises(Exception):
        prognosis.get_json_prognosis()
