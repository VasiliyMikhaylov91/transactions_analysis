import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import create_dt_obj

MONTH_PERIOD = relativedelta(months=3)


def filter_by_month_period(
    data: pd.DataFrame, date_end: Optional[str] = None
) -> tuple[pd.DataFrame, datetime.datetime]:
    """Выборка данных из data за MONTH_PERIOD до указаной даты date_end"""

    if not date_end:
        date = datetime.datetime.now()
    else:
        date = create_dt_obj(date_end)
    date_start = date - MONTH_PERIOD
    result_data = data.drop(data[date_start <= data["Дата операции"] <= date].index)
    return result_data, date_start


def file_record(file_name: str = "record.txt") -> Any:
    """Запись результатов выполнения функции в указанный файл"""

    def record_func(func: Callable[..., Any]) -> Callable[..., Any] | None:
        @wraps(func)
        def wrap(*args: Any, **kwargs: Any) -> Any:
            with open(file_name, "w") as file:
                result = func(*args, **kwargs)
                file.write(result)
            return result

        return wrap

    return record_func


@file_record()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)."""

    filtered_by_date, start_date = filter_by_month_period(transactions, date)
    filtered_by_category = filtered_by_date.query(f'Категория == "{category}"')
    return pd.DataFrame(
        {
            "category": [category],
            "sum": [filtered_by_category["Сумма операции"].sum()],
            "start_date": [start_date],
            "end_date": [date],
        }
    )


@file_record()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты)."""

    filtered_by_date, start_date = filter_by_month_period(transactions, date)
    filtered_by_date["weekday"] = filtered_by_date["Дата операции"].weekday()
    return pd.DataFrame(
        {
            "monday": [filtered_by_date.query("weekday == 0")["Сумма операции"].mean()],
            "tuesday": [filtered_by_date.query("weekday == 1")["Сумма операции"].mean()],
            "wednesday": [filtered_by_date.query("weekday == 2")["Сумма операции"].mean()],
            "thursday": [filtered_by_date.query("weekday == 3")["Сумма операции"].mean()],
            "friday": [filtered_by_date.query("weekday == 4")["Сумма операции"].mean()],
            "saturday": [filtered_by_date.query("weekday == 5")["Сумма операции"].mean()],
            "sunday": [filtered_by_date.query("weekday == 6")["Сумма операции"].mean()],
            "start_date": [start_date],
            "end_date": [date],
        }
    )


@file_record()
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция выводит средние траты в рабочий и в выходной день за последние три месяца (от переданной даты)."""

    filtered_by_date, start_date = filter_by_month_period(transactions, date)
    filtered_by_date["weekday"] = filtered_by_date["Дата операции"].weekday()
    return pd.DataFrame(
        {
            "workday": [filtered_by_date.query("weekday < 5")["Сумма операции"].mean()],
            "weekend": [filtered_by_date.query("weekday > 4")["Сумма операции"].mean()],
            "start_date": [start_date],
            "end_date": [date],
        }
    )
