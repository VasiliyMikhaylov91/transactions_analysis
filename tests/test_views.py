import json
from unittest.mock import Mock, patch

from src.views import events, main_page


@patch("src.utils.stock_prices")
@patch("src.utils.currency_rates")
@patch("src.utils.top_transactions")
@patch("src.utils.cards")
def test_main_page(cd_mock: Mock, tt_mock: Mock, cr_mock: Mock, sp_mock: Mock) -> None:
    """Тестирование функции main_page"""

    cd_mock.return_value = [
        {"last_digits": "5814", "total_spent": 1262.00, "cashback": 12.62},
        {"last_digits": "7512", "total_spent": 7.94, "cashback": 0.08},
    ]
    tt_mock.return_value = [
        {
            "date": "21.12.2021",
            "amount": 1198.23,
            "category": "Переводы",
            "description": "Перевод Кредитная карта. ТП 10.2 RUR",
        },
        {"date": "20.12.2021", "amount": 829.00, "category": "Супермаркеты", "description": "Лента"},
        {"date": "20.12.2021", "amount": 421.00, "category": "Различные товары", "description": "Ozon.ru"},
        {"date": "16.12.2021", "amount": -14216.42, "category": "ЖКХ", "description": "ЖКУ Квартира"},
        {"date": "16.12.2021", "amount": 453.00, "category": "Бонусы", "description": "Кешбэк за обычные покупки"},
    ]
    cr_mock.return_value = [{"currency": "USD", "rate": 73.21}, {"currency": "EUR", "rate": 87.08}]
    sp_mock.return_value = [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18},
        {"stock": "GOOGL", "price": 2742.39},
        {"stock": "MSFT", "price": 296.71},
        {"stock": "TSLA", "price": 1007.08},
    ]
    assert main_page("31.12.2021 16:42:04") == json.dumps(
        {
            "greeting": "Добрый день",
            "cards": [
                {"last_digits": "5814", "total_spent": 1262.00, "cashback": 12.62},
                {"last_digits": "7512", "total_spent": 7.94, "cashback": 0.08},
            ],
            "top_transactions": [
                {
                    "date": "21.12.2021",
                    "amount": 1198.23,
                    "category": "Переводы",
                    "description": "Перевод Кредитная карта. ТП 10.2 RUR",
                },
                {"date": "20.12.2021", "amount": 829.00, "category": "Супермаркеты", "description": "Лента"},
                {"date": "20.12.2021", "amount": 421.00, "category": "Различные товары", "description": "Ozon.ru"},
                {"date": "16.12.2021", "amount": -14216.42, "category": "ЖКХ", "description": "ЖКУ Квартира"},
                {
                    "date": "16.12.2021",
                    "amount": 453.00,
                    "category": "Бонусы",
                    "description": "Кешбэк за обычные покупки",
                },
            ],
            "currency_rates": [{"currency": "USD", "rate": 73.21}, {"currency": "EUR", "rate": 87.08}],
            "stock_prices": [
                {"stock": "AAPL", "price": 150.12},
                {"stock": "AMZN", "price": 3173.18},
                {"stock": "GOOGL", "price": 2742.39},
                {"stock": "MSFT", "price": 296.71},
                {"stock": "TSLA", "price": 1007.08},
            ],
        }
    )


@patch("src.utils.stock_prices")
@patch("src.utils.currency_rates")
@patch("src.utils.calculate_finance")
def test_events(cf_mock: Mock, cr_mock: Mock, sp_mock: Mock) -> None:
    """Тестирование функции events"""

    cf_mock.return_value = (
        {
            "total_amount": 32101,
            "main": [
                {"category": "Супермаркеты", "amount": 17319},
                {"category": "Фастфуд", "amount": 3324},
                {"category": "Топливо", "amount": 2289},
                {"category": "Развлечения", "amount": 1850},
                {"category": "Медицина", "amount": 1350},
                {"category": "Остальное", "amount": 2954},
            ],
            "transfers_and_cash": [{"category": "Наличные", "amount": 500}, {"category": "Переводы", "amount": 200}],
        },
        {
            "total_amount": 54271,
            "main": [
                {"category": "Пополнение_BANK007", "amount": 33000},
                {"category": "Проценты_на_остаток", "amount": 1242},
                {"category": "Кэшбэк", "amount": 29},
            ],
        },
    )
    cr_mock.return_value = [{"currency": "USD", "rate": 73.21}, {"currency": "EUR", "rate": 87.08}]
    sp_mock.return_value = [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18},
        {"stock": "GOOGL", "price": 2742.39},
        {"stock": "MSFT", "price": 296.71},
        {"stock": "TSLA", "price": 1007.08},
    ]
    assert events("31.12.2021 16:42:04") == json.dumps(
        {
            "expenses": {
                "total_amount": 32101,
                "main": [
                    {"category": "Супермаркеты", "amount": 17319},
                    {"category": "Фастфуд", "amount": 3324},
                    {"category": "Топливо", "amount": 2289},
                    {"category": "Развлечения", "amount": 1850},
                    {"category": "Медицина", "amount": 1350},
                    {"category": "Остальное", "amount": 2954},
                ],
                "transfers_and_cash": [
                    {"category": "Наличные", "amount": 500},
                    {"category": "Переводы", "amount": 200},
                ],
            },
            "income": {
                "total_amount": 54271,
                "main": [
                    {"category": "Пополнение_BANK007", "amount": 33000},
                    {"category": "Проценты_на_остаток", "amount": 1242},
                    {"category": "Кэшбэк", "amount": 29},
                ],
            },
            "currency_rates": [{"currency": "USD", "rate": 73.21}, {"currency": "EUR", "rate": 87.08}],
            "stock_prices": [
                {"stock": "AAPL", "price": 150.12},
                {"stock": "AMZN", "price": 3173.18},
                {"stock": "GOOGL", "price": 2742.39},
                {"stock": "MSFT", "price": 296.71},
                {"stock": "TSLA", "price": 1007.08},
            ],
        }
    )
