import datetime
import json
import logging
import os
from typing import Any, Union

import pandas as pd
import requests
from dotenv import load_dotenv
from requests import RequestException

TOP_TRANSACTION_NUMBER = 5
TOP_EXPENSES_NUMBER = 7

data_path = os.path.join("..", "data", "operations.xlsx")
if __name__ == '__main__':
    path_to_settings = os.path.join("..", "user_settings.json")
else:
    path_to_settings = os.path.join(".", "user_settings.json")

with open(path_to_settings, "r", encoding="utf-8") as f:
    user_settings = json.load(f)

utils_logger = logging.getLogger(__name__)
if __name__ == '__main__':
    file_handler = logging.FileHandler("../logs/utils.log", encoding="utf-8")
else:
    file_handler = logging.FileHandler("./logs/utils.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(funcName)s %(message)s")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)
utils_logger.addHandler(file_handler)
utils_logger.setLevel(logging.DEBUG)


def read_xlsx_transactions(path_to_data: str = data_path) -> list[dict]:
    """Преобразование указанного *.xlsx файла в список словарей"""

    df = pd.read_excel(path_to_data)
    df.fillna({"Кэшбэк": 0, "Категория": "", "Номер карты": "", "MCC": 0, "Описание": ""}, inplace=True)
    return [dict(df.iloc[i]) for i in range(df.shape[0])]


def create_dt_obj(date_time: str) -> datetime.datetime:
    """Создание объекта datetime"""

    return datetime.datetime.strptime(date_time, "%d.%m.%Y %H:%M:%S")


def reference_filter(data: list[dict], date_time: str, reference: str) -> list[dict]:
    """Выборка значений из data в указанном диапазоне reference ('ALL', 'M', 'Y', 'W') с датой date_time"""

    if reference == "ALL":
        return list(filter(lambda x: create_dt_obj(x["Дата операции"]) <= create_dt_obj(date_time), data))
    if reference == "M":
        return list(
            filter(
                lambda x: create_dt_obj(x["Дата операции"]).month == create_dt_obj(date_time).month
                and create_dt_obj(x["Дата операции"]).year == create_dt_obj(date_time).year,
                data,
            )
        )
    if reference == "Y":
        return list(filter(lambda x: create_dt_obj(x["Дата операции"]).year == create_dt_obj(date_time).year, data))
    if reference == "W":
        dt = create_dt_obj(date_time)
        dt_weekday_number = dt.weekday()  # 0..6
        dt_start = dt - datetime.timedelta(days=dt_weekday_number)
        dt_end = dt + datetime.timedelta(days=6) - datetime.timedelta(days=dt_weekday_number)
        return list(filter(lambda x: dt_start <= create_dt_obj(x["Дата операции"]) <= dt_end, data))
    return []


def greetings(date_time: str) -> str:
    """Приветствие в соответствии с временем суток в date_time"""

    dt = create_dt_obj(date_time)
    hours = dt.hour
    if 0 <= hours <= 5:
        utils_logger.info("Пользователь зашел ночью")
        return "Доброй ночи"
    if 6 <= hours <= 11:
        utils_logger.info("Пользователь зашел утром")
        return "Доброе утро"
    if 12 <= hours <= 17:
        utils_logger.info("Пользователь зашел днем")
        return "Добрый день"
    utils_logger.info("Пользователь зашел вечером")
    return "Добрый вечер"


def cards(data: list[dict]) -> list[dict]:
    """Вывод информации по картам на основе данных data"""

    card_dict: dict[str, Any] = dict()
    data_cards = list(filter(lambda x: isinstance(x["Номер карты"], str), data))
    for data_card in data_cards:
        if data_card["Статус"] == "OK" and data_card["Сумма платежа"] < 0:
            if data_card["Номер карты"] in card_dict:
                card_dict[data_card["Номер карты"]]["total_spent"] += data_card["Сумма платежа"] * (-1)
                card_dict[data_card["Номер карты"]]["cashback"] += data_card["Кэшбэк"]
            else:
                card_dict[data_card["Номер карты"]] = {
                    "total_spent": data_card["Сумма платежа"] * (-1),
                    "cashback": data_card["Кэшбэк"],
                }
    utils_logger.info("Получены данные по картам")
    return [
        {"last_digits": key[1:], "total_spent": value["total_spent"], "cashback": value["cashback"]}
        for key, value in card_dict.items()
    ]


def top_transactions(data: list[dict], date_time: str) -> list[dict]:
    """Топ транзакций в месяце с указанной датой из списка data"""

    dt = create_dt_obj(date_time)
    good_transactions = list(
        filter(
            lambda x: x["Статус"] == "OK"
            and create_dt_obj(x["Дата операции"]).year == dt.year
            and create_dt_obj(x["Дата операции"]).month == dt.month
            and create_dt_obj(x["Дата операции"]).day <= dt.day,
            data,
        )
    )
    if len(good_transactions) > TOP_TRANSACTION_NUMBER:
        utils_logger.info("Получено нужное количество топ-транзакций")
        return sorted(good_transactions, key=lambda x: abs(x["Сумма платежа"]), reverse=True)[:TOP_TRANSACTION_NUMBER]
    else:
        utils_logger.info("Получено малое количество топ-транзакций")
        return sorted(good_transactions, key=lambda x: abs(x["Сумма платежа"]), reverse=True)


def currency_rates(date_time: str) -> Union[list[dict], None]:
    """Курс валют в указанную дату в соответствии с user_settings.json"""

    dt = create_dt_obj(date_time)
    load_dotenv()

    try:
        api_key = os.getenv("APILAYER_API_KEY")
        utils_logger.debug("Успешно получен APILAYER_API_KEY из .env")
    except Exception as e:
        utils_logger.error(e)
        return None

    headers = {"apikey": api_key}
    result = list()
    try:
        for currency in user_settings["user_currencies"]:
            api_url = (
                f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&"
                f"from={currency}&"
                f"amount=1&"
                f"date={dt.strftime('%Y-%m-%d')}"
            )
            response_api = requests.request("GET", api_url, headers=headers)
            response = json.loads(response_api.text)
            result.append({"currency": currency, "rate": response["result"]})
        utils_logger.debug("Получен ответ API")
    except RequestException as e:
        utils_logger.error(e)
        return None

    return result


def stock_prices(date_time: str) -> Union[list[dict], None]:
    """Стоимость акций в указанную дату в соответствии с user_settings.json"""

    dt = create_dt_obj(date_time)
    dt_beg = create_dt_obj("01.01.2000 00:00:00")

    if dt < dt_beg:
        utils_logger.error("Дата вне диапазона alphavantage")
        return None

    load_dotenv()

    try:
        api_key = os.getenv("S&P500_API_KEY")
        utils_logger.debug("Успешно получен S&P500_API_KEY из .env")
    except Exception as e:
        utils_logger.error(e)
        return None

    result = list()
    try:
        for stock in user_settings["user_stocks"]:
            api_url = (
                f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&"
                f"symbol={stock}&outputsize=full&apikey={api_key}"
            )
            response_api = requests.request("GET", api_url)
            response = json.loads(response_api.text)
            day = dt.strftime("%Y-%m-%d")
            while day not in response["Time Series (Daily)"]:
                dt_day = datetime.datetime.strptime(day, "%Y-%m-%d")
                dt_day -= datetime.timedelta(days=1)
                day = dt_day.strftime("%Y-%m-%d")
            result.append({"stock": stock, "price": response["Time Series (Daily)"][day]["4. close"]})
        utils_logger.debug("Получен ответ API")
    except RequestException as e:
        utils_logger.error(e)
        return None

    return result


def calculate_finance(data: list[dict], date_time: str, reference: str = "M") -> tuple[dict, dict]:
    """Подсчет затрат и прибыли по категориям"""

    data_filtered_ref = reference_filter(data, date_time, reference)
    data_filtered: list[dict] = list(filter(lambda x: x["Статус"] == "OK", data_filtered_ref))
    total_amount_expenses = 0
    total_amount_income = 0
    expenses_dict: dict[str, Any] = dict()
    income_dict: dict[str, Any] = dict()
    for transaction in data_filtered:
        if transaction["Сумма операции"] < 0:
            if transaction["Категория"] in expenses_dict:
                expenses_dict[transaction["Категория"]] -= transaction["Сумма операции"]
            else:
                expenses_dict[transaction["Категория"]] = transaction["Сумма операции"] * (-1)
            total_amount_expenses -= transaction["Сумма операции"]
        else:
            if transaction["Категория"] in income_dict:
                income_dict[transaction["Категория"]] += transaction["Сумма операции"]
            else:
                income_dict[transaction["Категория"]] = transaction["Сумма операции"]
            total_amount_income += transaction["Сумма операции"]
    expenses_dict = {k: v for k, v in sorted(expenses_dict.items(), key=lambda x: x[1], reverse=True)}
    income_dict = {k: v for k, v in sorted(income_dict.items(), key=lambda x: x[1], reverse=True)}
    count = 0
    expenses_list_main = list()
    expenses_list_transfers_and_cash = list()
    for key, value in expenses_dict.items():
        if not (key == "Наличные" or key == "Переводы"):
            if count < TOP_EXPENSES_NUMBER:
                expenses_list_main.append({"category": key, "amount": value})
            elif count == TOP_EXPENSES_NUMBER:
                expenses_list_main.append({"category": "Остальное", "amount": value})
            else:
                expenses_list_main[-1]["amount"] += value
            count += 1
        else:
            expenses_list_transfers_and_cash.append({"category": key, "amount": value})
    income_list = [{"category": key, "amount": value} for key, value in income_dict.items()]
    return (
        {
            "total_amount": total_amount_expenses,
            "main": expenses_list_main,
            "transfers_and_cash": expenses_list_transfers_and_cash,
        },
        {"total_amount": total_amount_income, "main": income_list},
    )
