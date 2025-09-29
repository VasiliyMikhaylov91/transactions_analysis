import datetime, json, logging, os, requests
from typing import Union

import pandas as pd
from dotenv import load_dotenv
from requests import RequestException

TOP_TRANSACTION_NUMBER = 5
data_path = os.path.join('..', 'data', 'operations.xlsx')
path_to_settings = os.path.join('..', 'user_settings.json')

with open(path_to_settings, "r") as f:
    user_settings = json.load(f)

utils_logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("../logs/utils.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(funcName)s %(message)s")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)
utils_logger.addHandler(file_handler)
utils_logger.setLevel(logging.DEBUG)

def read_xlsx_transactions() -> list[dict]:
    """Преобразование указанного *.xlsx файла в список словарей"""

    df = pd.read_excel(data_path)
    df.fillna({"Кэшбэк": 0}, inplace=True)
    # df = df.dropna(subset=["Дата операции",
    #                        "Дата платежа",
    #                        "Номер карты",
    #                        "Статус",
    #                        "Сумма операции",
    #                        "Валюта операции",
    #                        "Сумма платежа",
    #                        "Валюта платежа",
    #                        "Кэшбэк",
    #                        "MCC",
    #                        "Описание",
    #                        "Бонусы (включая кэшбэк)",
    #                        "Округление на инвесткопилку",
    #                        "Сумма операции с округлением"])
    return [dict(df.iloc[i]) for i in range(df.shape[0])]


def create_dt_obj(date_time: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_time, '%d.%m.%Y %H:%M:%S')


def greetings(date_time: str) -> str:
    dt = create_dt_obj(date_time)
    hours = dt.hour
    if 0 <= hours <= 6:
        return 'Доброй ночи'
    if 6 <= hours <= 12:
        return 'Доброе утро'
    if 12 <= hours <= 18:
        return 'Добрый день'
    return 'Добрый вечер'


def cards(data: list[dict]) -> list[dict]:
    card_dict = dict()
    data_cards = list(filter(lambda x: isinstance(x["Номер карты"], str), data))
    for data_card in data_cards:
        if data_card["Номер карты"] in card_dict:
            card_dict[data_card["Номер карты"]]["total_spent"] += data_card["Сумма платежа"] *(-1)
            card_dict[data_card["Номер карты"]]["cashback"] += data_card["Кэшбэк"]
        else:
            card_dict[data_card["Номер карты"]] = {"total_spent": data_card["Сумма платежа"] * (-1),
                                                     "cashback": data_card["Кэшбэк"]}

    result = []
    for key, value in card_dict.items():
        result.append({"last_digits": key[1:],
                       "total_spent": value["total_spent"],
                       "cashback": value["cashback"]})

    return result


def top_transactions(data: list[dict]) -> list[dict]:
    good_transactions = list(filter(lambda x: x["Статус"] == "OK", data))
    return sorted(good_transactions, key=lambda x: abs(x["Сумма платежа"]), reverse=True)[:TOP_TRANSACTION_NUMBER]


def currency_rates(date_time: str) -> Union[list[dict], None]:
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
    dt = create_dt_obj(date_time)
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
            result.append({"stock": stock, "price": response["Time Series (Daily)"]
                                                            [dt.strftime('%Y-%m-%d')]
                                                            ["4. close"]})
        utils_logger.debug("Получен ответ API")
    except RequestException as e:
        utils_logger.error(e)
        return None

    return result


if __name__ == '__main__':
    print(stock_prices('20.03.2019 17:01:38'))
