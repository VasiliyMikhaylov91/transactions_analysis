import json
import logging

import src.utils

views_logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("../logs/views.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(funcName)s %(message)s")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)
views_logger.addHandler(file_handler)
views_logger.setLevel(logging.DEBUG)


def main_page(date_and_time: str) -> str:
    """Подготовка данных для страницы Главная"""

    try:
        data = src.utils.read_xlsx_transactions()
        views_logger.info(f"Получены данные по транзакциям в {date_and_time}")
    except Exception as error:
        data = []
        views_logger.error(error)

    try:
        res = {
            "greeting": src.utils.greetings(date_and_time),
            "cards": src.utils.cards(data),
            "top_transactions": src.utils.top_transactions(data, date_and_time),
            "currency_rates": src.utils.currency_rates(date_and_time),
            "stock_prices": src.utils.stock_prices(date_and_time),
        }
        views_logger.info(f"Получены данные из utils {date_and_time}")
        return json.dumps(res)
    except Exception as error:
        views_logger.error(error)
        return json.dumps({})


def events(date_and_time: str) -> str:
    """Подготовка данных для страницы События"""

    try:
        data = src.utils.read_xlsx_transactions()
        views_logger.info(f"Получены данные по транзакциям в {date_and_time}")
    except Exception as error:
        data = []
        views_logger.error(error)

    try:
        expenses, income = src.utils.calculate_finance(data, date_and_time)
        res = {
            "expenses": expenses,
            "income": income,
            "currency_rates": src.utils.currency_rates(date_and_time),
            "stock_prices": src.utils.stock_prices(date_and_time),
        }
        views_logger.info(f"Получены данные из utils {date_and_time}")
        return json.dumps(res)
    except Exception as error:
        views_logger.error(error)
        return json.dumps({})
