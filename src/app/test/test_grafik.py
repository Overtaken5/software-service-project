import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
from io import StringIO
import json
import matplotlib.pyplot as plt
from src.app.product_quantity_forecast.quantity_forecast import Prognosis
from src.app.product_quantity_forecast.grafik import plot_prognosis  # Импортируй модуль с функцией plot_prognosis


class TestPlotPrognosis(unittest.TestCase):

    def setUp(self):
        # Пример JSON данных для прогноза
        self.prognosis_json = json.dumps([
            {"date": "2020-01-01", "quantity": 100, "actual": True},
            {"date": "2020-02-01", "quantity": 120, "actual": True},
            {"date": "2020-02-15", "quantity": 40, "actual": True},
            {"date": "2020-03-01", "quantity": 30, "actual": False},
            {"date": "2020-04-01", "quantity": 70, "actual": False}
        ])
        self.start_date = '2020-01-01'
        self.end_date = '2020-04-1'

    @patch('matplotlib.pyplot.savefig')  # Мокаем сохранение графика
    def test_plot_prognosis(self, mock_savefig):
        # Мокаем savefig, чтобы не сохранять файл на диск
        mock_savefig.return_value = None

        # Вызываем функцию
        image_path = plot_prognosis(self.prognosis_json, self.start_date, self.end_date)

        # Проверяем, что savefig был вызван
        mock_savefig.assert_called_once()

        # Проверяем, что возвращенный путь соответствует ожидаемому формату
        expected_filename = f'prognosis_{self.start_date}_{self.end_date}.png'
        self.assertEqual(image_path, expected_filename)

        # Проверяем, что файл действительно не был создан (поскольку savefig замокан)
        self.assertFalse(os.path.exists(image_path))

    @patch('matplotlib.pyplot.show')  # Мокаем plt.show()
    def test_plot_prognosis_show(self, mock_show):
        # Мокаем show, чтобы не показывать график
        mock_show.return_value = None

        # Вызываем функцию
        plot_prognosis(self.prognosis_json, self.start_date, self.end_date)

        # Проверяем, что show был вызван
        mock_show.assert_called_once()

    def tearDown(self):
        # Очистка (если бы мы реально сохраняли файлы)
        filename = f'prognosis_{self.start_date}_{self.end_date}.png'
        if os.path.exists(filename):
            os.remove(filename)


if __name__ == '__main__':
    unittest.main()