import datetime
import json
import logging
import re
from typing import Any

services_logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("../logs/services.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(funcName)s %(message)s")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)
services_logger.addHandler(file_handler)
services_logger.setLevel(logging.DEBUG)


def cashback_benefits(data: list[dict], year: int, month: int) -> str:
    """Функция показывает сколько на каждой категории можно заработать кешбэка в указанном месяце года."""

    result: dict[str, Any] = dict()

    try:
        for transaction in data:
            dt = datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
            if dt.year == year and dt.month == month:
                if transaction["Категория"] in result:
                    result[transaction["Категория"]] += transaction["Кэшбэк"]
                else:
                    result[transaction["Категория"]] = transaction["Кэшбэк"]
        services_logger.info("Получение наиболее выгодных предложений кэшбека")
    except Exception as error:
        services_logger.error(error)

    return json.dumps(result)


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """Функция возвращает сумму, которую удалось бы отложить в «Инвесткопилку»."""

    dt_month = datetime.datetime.strptime(month, "%Y-%m")
    year = dt_month.year
    mon = dt_month.month
    result = 0.0

    try:
        for transaction in transactions:
            dt_trans = datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
            if dt_trans.year == year and dt_trans.month == mon:
                result += limit - (transaction["Сумма операции"] % limit)
        services_logger.info(f"Получена сумма инвесткопилки {result} с учетом округления {limit}")
    except Exception as error:
        services_logger.error(error)

    return round(result, 2)


def simple_search(data: list[dict[str, Any]], search_word: str) -> str:
    """
    Пользователь передает строку для поиска, возвращается JSON-ответ со всеми транзакциями,
    содержащими запрос в описании или категории.
    """

    result = [
        x
        for x in data
        if re.search(search_word, x["Описание"], flags=re.I) or re.search(search_word, x["Категория"], flags=re.I)
    ]
    services_logger.info(f"Поиск по слову {search_word} нашел {len(result)} транзакций")
    return json.dumps(result)


def search_description(data: list[dict[str, Any]], pattern: str) -> str:
    """Функция возвращает JSON со всеми транзакциями, содержащими в описании pattern"""

    result = [x for x in data if re.search(pattern, x["Описание"])]
    services_logger.info(f"Поиск по {pattern} нашел {len(result)} транзакций")
    return json.dumps(result)


def phone_search(data: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера."""

    return search_description(data, r"\+7 9\d\d \d+-\d\d-\d\d")


def name_search(data: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам."""

    return search_description(data, r"\D+ \D\.")
