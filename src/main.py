import os

import pandas as pd

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday
from src.services import name_search, phone_search, simple_search
from src.utils import read_xlsx_transactions
from src.views import events, main_page

path_to_data = os.path.join("..", "data", "operations.xlsx")

print("Состав файла для страницы Главная")
print(main_page("31.12.2021 16:42:04"))
print()
print("Состав файла для страницы События")
print(events("31.12.2021 16:42:04"))

if input("Поиск по слову в описании или категории 1-Да 0-Нет -> ") == "1":
    print(simple_search(read_xlsx_transactions(), input("Слово для поиска -> ")))
if input("Поиск по телефонным номерам в описании 1-Да 0-Нет -> ") == "1":
    print(phone_search(read_xlsx_transactions()))
if input("Поиск по переводам физ лицам в описании 1-Да 0-Нет -> ") == "1":
    print(name_search(read_xlsx_transactions()))
if input("Траты по категориям за 3 месяца 1-Да 0-Нет -> ") == "1":
    print(spending_by_category(pd.read_excel(path_to_data), input("Категория -> "), "31.12.2021 16:42:04"))
if input("Средние траты по дням недели за 3 месяца 1-Да 0-Нет -> ") == "1":
    print(spending_by_weekday(pd.read_excel(path_to_data), "31.12.2021 16:42:04"))
if input("Средние траты по рабочим/выходным дням за 3 месяца 1-Да 0-Нет -> ") == "1":
    print(spending_by_workday(pd.read_excel(path_to_data), "31.12.2021 16:42:04"))
