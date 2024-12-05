import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from io import StringIO
from quantity_forecast import Product, Prognosis  # Импортируйте класс из вашего модуля


class TestPrognosis(unittest.TestCase):

    @patch('pandas.read_csv')
    def setUp(self, mock_read_csv):
        # Подготавливаем тестовые данные для замены реальных данных из csv файла
        csv_data = StringIO("""
        date,quantity
        2014-01-01,100
        2015-01-01,150
        2016-01-01,200
        """)
        mock_read_csv.return_value = pd.read_csv(csv_data)

        # Инициализация тестового продукта и объекта Prognosis
        self.product = Product(2, 'Test Product')
        self.start_date = '2014-01-01'
        self.end_date = '2016-06-01'
        self.prognosis = Prognosis(self.product, self.start_date, self.end_date)

    def test_get_train_dataset(self):
        # Проверяем, что метод корректно возвращает данные
        df = self.prognosis.get_train_dataset()
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 3)  # У нас три строки в тестовом наборе данных
        self.assertIn('date', df.columns)
        self.assertIn('quantity', df.columns)

    def test_is_prognosable(self):
        # Проверяем корректную проверку на прогнозируемость
        self.assertTrue(self.prognosis.is_prognosable())

        # Прогноз на слишком раннюю дату должен возвращать False
        self.prognosis.start_date = '2010-01-01'
        self.assertFalse(self.prognosis.is_prognosable())

    @patch('quantity_forecast.Prophet')  # Мокаем Prophet, чтобы не тренировать модель в тесте
    def test_prognose(self, mock_prophet):
        # Настраиваем мок для Prophet
        mock_model = MagicMock()
        mock_model.predict.return_value = pd.DataFrame({
            'ds': pd.to_datetime(['2016-02-01', '2016-03-01', '2016-04-01']),
            'yhat': [250, 260, 270]
        })
        mock_prophet.return_value = mock_model

        # Прогнозируем
        self.prognosis.prognose()

        # Проверяем, что в результате есть данные с нужными датами и полями
        self.assertIsNotNone(self.prognosis.series_df)
        self.assertEqual(len(self.prognosis.series_df), 6)  # 3 строки из оригинального + 3 спрогнозированных
        self.assertIn('date', self.prognosis.series_df.columns)
        self.assertIn('quantity', self.prognosis.series_df.columns)
        self.assertIn('actual', self.prognosis.series_df.columns)

    @patch('quantity_forecast.Prophet')
    def test_get_json_prognosis(self, mock_prophet):
        # Настраиваем мок для Prophet
        mock_model = MagicMock()
        mock_model.predict.return_value = pd.DataFrame({
            'ds': pd.to_datetime(['2016-02-01', '2016-03-01', '2016-04-01']),
            'yhat': [250, 260, 270]
        })
        mock_prophet.return_value = mock_model

        # Проверяем, что json прогноз возвращается корректно
        json_prognosis = self.prognosis.get_json_prognosis()
        self.assertIsNotNone(json_prognosis)
        self.assertIn('date', json_prognosis)
        self.assertIn('quantity', json_prognosis)

    def test_prognose_error_on_early_dates(self):
        # Проверка исключения на слишком ранние даты для прогноза
        self.prognosis.start_date = '2010-01-01'
        with self.assertRaises(Exception) as context:
            self.prognosis.get_json_prognosis()
        self.assertTrue('Prognosis date must be at least' in str(context.exception))


if __name__ == '__main__':
    unittest.main()
