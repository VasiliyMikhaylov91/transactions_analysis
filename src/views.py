import json
from utils import calculate_finance, cards, currency_rates,  greetings, read_xlsx_transactions, stock_prices, top_transactions


def main_page(date_and_time: str) -> str:
    """Подготовка данных для страницы Главная"""

    data = read_xlsx_transactions()
    res = {"greeting": greetings(date_and_time),
           "cards": cards(data),
           "top_transactions": top_transactions(data, date_and_time),
           "currency_rates": currency_rates(date_and_time),
           "stock_prices": stock_prices(date_and_time)}
    return json.dumps(res)


def events(date_and_time: str) -> str:
    """Подготовка данных для страницы События"""

    data = read_xlsx_transactions()
    expenses, income = calculate_finance(data, date_and_time)
    res = {"expenses": expenses,
           "income": income,
           "currency_rates": currency_rates(date_and_time),
           "stock_prices": stock_prices(date_and_time)}
    return json.dumps(res)


if __name__ == "__main__":
    print(events(date_and_time="10.10.2020 00:00:00"))