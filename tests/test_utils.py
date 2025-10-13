import os
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.utils import (calculate_finance, cards, currency_rates, greetings, read_xlsx_transactions, stock_prices,
                       top_transactions)


def test_read_xlsx_transactions(xlsx_simples: tuple[dict, list[dict]]) -> None:
    """Тестирование функции read_xlsx_transactions"""

    test_df = pd.DataFrame(xlsx_simples[0])
    test_df.to_excel("test.xlsx", index=False)
    # mock_read_excel = Mock(return_value=test_df)
    # pd.read_excel = mock_read_excel
    assert read_xlsx_transactions("test.xlsx") == xlsx_simples[1]
    os.remove("test.xlsx")


@pytest.mark.parametrize(
    "date_time, result",
    [
        ("21.03.2014 21:05:31", "Добрый вечер"),
        ("31.12.2020 09:00:12", "Доброе утро"),
        ("13.09.2019 12:54:00", "Добрый день"),
        ("13.09.2021 03:54:57", "Доброй ночи"),
    ],
)
def test_greetings(date_time: str, result: str) -> None:
    """Тестирование функции greetings"""

    assert greetings(date_time) == result


def test_cards(transactions_test: list[dict]) -> None:
    """Тестирование функции cards"""

    assert cards(transactions_test) == [
        {"cashback": 5.0, "last_digits": "7197", "total_spent": 264.0},
        {"cashback": 0.0, "last_digits": "5091", "total_spent": 1.51},
    ]


@pytest.mark.parametrize(
    "date_time, result",
    [
        (
            "31.12.2021 16:42:04",
            [
                {
                    "Дата операции": "31.12.2021 16:42:04",
                    "Дата платежа": "31.12.2021",
                    "Номер карты": "*7197",
                    "Статус": "OK",
                    "Сумма операции": -64.00,
                    "Валюта операции": "RUB",
                    "Сумма платежа": -64.00,
                    "Валюта платежа": "RUB",
                    "Кэшбэк": 1.0,
                    "Категория": "Супермаркеты",
                    "MCC": 5411,
                    "Описание": "Колхоз",
                    "Бонусы (включая кэшбэк)": 1.0,
                    "Округление на инвесткопилку": 0.0,
                    "Сумма операции с округлением": 64.00,
                },
                {
                    "Дата операции": "23.12.2021 22:33:11",
                    "Дата платежа": "24.12.2021",
                    "Номер карты": "*5091",
                    "Статус": "OK",
                    "Сумма операции": -1.51,
                    "Валюта операции": "RUB",
                    "Сумма платежа": -1.51,
                    "Валюта платежа": "RUB",
                    "Кэшбэк": 0.0,
                    "Категория": "Каршеринг",
                    "MCC": 7512,
                    "Описание": "Ситидрайв",
                    "Бонусы (включая кэшбэк)": 0.0,
                    "Округление на инвесткопилку": 0.0,
                    "Сумма операции с округлением": 1.51,
                },
            ],
        ),
        (
            "07.07.2019 19:12:23",
            [
                {
                    "Дата операции": "07.07.2019 19:12:23",
                    "Дата платежа": "08.07.2019",
                    "Номер карты": "*7197",
                    "Статус": "OK",
                    "Сумма операции": -200.00,
                    "Валюта операции": "RUB",
                    "Сумма платежа": -200.00,
                    "Валюта платежа": "RUB",
                    "Кэшбэк": 4.0,
                    "Категория": "Рестораны",
                    "MCC": 5812,
                    "Описание": "Restaruant Jetset",
                    "Бонусы (включая кэшбэк)": 4.0,
                    "Округление на инвесткопилку": 0.0,
                    "Сумма операции с округлением": 200.00,
                }
            ],
        ),
        (
            "25.07.2019 14:13:42",
            [
                {
                    "Дата операции": "25.07.2019 14:13:42",
                    "Дата платежа": "25.07.2019",
                    "Номер карты": "*4556",
                    "Статус": "OK",
                    "Сумма операции": 50000,
                    "Валюта операции": "RUB",
                    "Сумма платежа": 50000,
                    "Валюта платежа": "RUB",
                    "Кэшбэк": 0.0,
                    "Категория": "Пополнения",
                    "MCC": None,
                    "Описание": "Возврат денежных средств по договору беспроцентного займа № 1 от 15.07.2019 г. ",
                    "Бонусы (включая кэшбэк)": 0.0,
                    "Округление на инвесткопилку": 0.0,
                    "Сумма операции с округлением": 50000,
                },
                {
                    "Дата операции": "07.07.2019 19:12:23",
                    "Дата платежа": "08.07.2019",
                    "Номер карты": "*7197",
                    "Статус": "OK",
                    "Сумма операции": -200.00,
                    "Валюта операции": "RUB",
                    "Сумма платежа": -200.00,
                    "Валюта платежа": "RUB",
                    "Кэшбэк": 4.0,
                    "Категория": "Рестораны",
                    "MCC": 5812,
                    "Описание": "Restaruant Jetset",
                    "Бонусы (включая кэшбэк)": 4.0,
                    "Округление на инвесткопилку": 0.0,
                    "Сумма операции с округлением": 200.00,
                },
            ],
        ),
    ],
)
def test_top_transactions(transactions_test: list[dict], date_time: str, result: list[dict]) -> None:
    """Тестирование функции top_transactions"""

    assert top_transactions(transactions_test, date_time) == result


class CurRatesTest:
    """Класс-заглушка для теста функции test_currency_rates"""

    text = '{"currency": "USD", "result": 1}'


@patch("requests.request")
def test_currency_rates(mock_get: Mock) -> None:
    """Тестирование функции currency_rates"""
    mock_get.return_value = CurRatesTest()
    assert currency_rates("07.07.2019 19:12:23") == [{"currency": "USD", "rate": 1}, {"currency": "EUR", "rate": 1}]


class StockPricesTest:
    """Класс-заглушка для теста функции test_stock_prices"""

    text = '{"Time Series (Daily)": {"2019-07-07": {"4. close": 1}}}'


@patch("requests.request")
def test_stock_prices(mock_get: Mock) -> None:
    """Тестирование функции stock_prices"""

    mock_get.return_value = StockPricesTest()
    assert stock_prices("07.07.2019 19:12:23") == [
        {"stock": "AAPL", "price": 1},
        {"stock": "AMZN", "price": 1},
        {"stock": "GOOGL", "price": 1},
        {"stock": "MSFT", "price": 1},
        {"stock": "TSLA", "price": 1},
    ]


@pytest.mark.parametrize(
    "date_time, result",
    [
        (
            "31.12.2021 16:42:04",
            (
                {
                    "main": [{"amount": 64.0, "category": "Супермаркеты"}, {"amount": 1.51, "category": "Каршеринг"}],
                    "total_amount": 65.51,
                    "transfers_and_cash": [],
                },
                {"main": [], "total_amount": 0},
            ),
        ),
        (
            "07.07.2019 19:12:23",
            (
                {
                    "main": [{"amount": 200.0, "category": "Рестораны"}],
                    "total_amount": 200.0,
                    "transfers_and_cash": [],
                },
                {"main": [{"amount": 50000, "category": "Пополнения"}], "total_amount": 50000},
            ),
        ),
        (
            "25.07.2019 14:13:42",
            (
                {
                    "main": [{"amount": 200.0, "category": "Рестораны"}],
                    "total_amount": 200.0,
                    "transfers_and_cash": [],
                },
                {"main": [{"amount": 50000, "category": "Пополнения"}], "total_amount": 50000},
            ),
        ),
    ],
)
def test_calculate_finance(transactions_test: list[dict], date_time: str, result: tuple[dict]) -> None:
    """Тестирование функции calculate_finance"""

    assert calculate_finance(transactions_test, date_time) == result
