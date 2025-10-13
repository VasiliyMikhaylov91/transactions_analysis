import json

import src.utils



def main_page(date_and_time: str) -> str:
    """Подготовка данных для страницы Главная"""

    data = src.utils.read_xlsx_transactions()
    res = {
        "greeting": src.utils.greetings(date_and_time),
        "cards": src.utils.cards(data),
        "top_transactions": src.utils.top_transactions(data, date_and_time),
        "currency_rates": src.utils.currency_rates(date_and_time),
        "stock_prices": src.utils.stock_prices(date_and_time),
    }
    return json.dumps(res)


def events(date_and_time: str) -> str:
    """Подготовка данных для страницы События"""

    data = src.utils.read_xlsx_transactions()
    expenses, income = src.utils.calculate_finance(data, date_and_time)
    res = {
        "expenses": expenses,
        "income": income,
        "currency_rates": src.utils.currency_rates(date_and_time),
        "stock_prices": src.utils.stock_prices(date_and_time),
    }
    return json.dumps(res)


if __name__ == "__main__":
    print(main_page("31.12.2021 16:42:04"))
