import datetime
import json
import re
from typing import Any


def cashback_benefits(data: list[dict], year: int, month: int) -> str:
    """Функция показывает сколько на каждой категории можно заработать кешбэка в указанном месяце года."""

    result: dict[str, Any] = dict()
    for transaction in data:
        dt = datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
        if dt.year == year and dt.month == month:
            if transaction["Категория"] in result:
                result[transaction["Категория"]] += transaction["Кэшбэк"]
            else:
                result[transaction["Категория"]] = transaction["Кэшбэк"]
    return json.dumps(result)


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """Функция возвращает сумму, которую удалось бы отложить в «Инвесткопилку»."""

    dt_month = datetime.datetime.strptime(month, "%Y-%m")
    year = dt_month.year
    mon = dt_month.month
    result = 0.0
    for transaction in transactions:
        dt_trans = datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
        if dt_trans.year == year and dt_trans.month == mon:
            result += limit - (transaction["Сумма операции"] % limit)
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
    return json.dumps(result)


def search_description(data: list[dict[str, Any]], pattern: str) -> str:
    """Функция возвращает JSON со всеми транзакциями, содержащими в описании pattern"""

    result = [x for x in data if re.search(pattern, x["Описание"])]
    return json.dumps(result)


def phone_search(data: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера."""

    return search_description(data, r"\+7 9\d\d \d+-\d\d-\d\d")


def name_search(data: list[dict[str, Any]]) -> str:
    """Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам."""

    return search_description(data, r"\D+ \D\.")
