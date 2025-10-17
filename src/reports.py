import datetime
import logging
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import create_dt_obj

reports_logger = logging.getLogger(__name__)
if __name__ == '__main__':
    file_handler = logging.FileHandler("../logs/reports.log", encoding="utf-8")
else:
    file_handler = logging.FileHandler("./logs/reports.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(funcName)s %(message)s")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)
reports_logger.addHandler(file_handler)
reports_logger.setLevel(logging.DEBUG)

MONTH_PERIOD = relativedelta(months=3)


def filter_by_month_period(data: pd.DataFrame, date_end: Optional[str] = None) -> tuple[list[dict], datetime.datetime]:
    """Выборка данных из data за MONTH_PERIOD до указаной даты date_end"""

    if not date_end:
        date = datetime.datetime.now()
        reports_logger.info("Принята текущая дата для окончания отчета")
    else:
        date = create_dt_obj(date_end)
        reports_logger.info(f"Принята дата {date_end} для окончания отчета")
    date_start = date - MONTH_PERIOD
    data_list = [
        dict(data.iloc[i])
        for i in range(data.shape[0])
        if date_start <= create_dt_obj(dict(data.iloc[i])["Дата операции"]) <= date
    ]
    return data_list, date_start


def file_record(file_name: str = "record.txt") -> Any:
    """Запись результатов выполнения функции в указанный файл"""

    def record_func(func: Callable[..., Any]) -> Callable[..., Any] | None:
        @wraps(func)
        def wrap(*args: Any, **kwargs: Any) -> Any:
            with open(file_name, "w") as file:
                result = func(*args, **kwargs)
                file.write(str(result))
                reports_logger.info(f"Результат выполнения {func.__name__} записан в {file_name}")
            return result

        return wrap

    return record_func


@file_record()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)."""

    filtered_by_date, start_date = filter_by_month_period(transactions, date)
    filtered_by_category = list(filter(lambda x: x["Категория"] == category, filtered_by_date))
    reports_logger.info(f"Получено {len(filtered_by_category)} в результате поиска по категории")
    return pd.DataFrame(
        {
            "category": [category],
            "sum": sum([x["Сумма операции"] for x in filtered_by_category]),
            "start_date": [start_date.strftime("%d.%m.%Y %H:%M:%S")],
            "end_date": [date],
        }
    )


@file_record()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты)."""

    filtered_by_date, start_date = filter_by_month_period(transactions, date)

    def calculate_average(weekday_number: int) -> float | Any:
        filtered_by_weekday = list(
            filter(lambda x: create_dt_obj(x["Дата операции"]).weekday() == weekday_number, filtered_by_date)
        )
        length = len(filtered_by_weekday)
        reports_logger.info(f"Получено {length} значений для дня недели с номером {weekday_number}")
        if length:
            return round(sum([x["Сумма операции"] for x in filtered_by_weekday]) / len(filtered_by_weekday), 2)
        return 0.0

    return pd.DataFrame(
        {
            "monday": [calculate_average(0)],
            "tuesday": [calculate_average(1)],
            "wednesday": [calculate_average(2)],
            "thursday": [calculate_average(3)],
            "friday": [calculate_average(4)],
            "saturday": [calculate_average(5)],
            "sunday": [calculate_average(6)],
            "start_date": [start_date.strftime("%d.%m.%Y %H:%M:%S")],
            "end_date": [date],
        }
    )


@file_record()
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция выводит средние траты в рабочий и в выходной день за последние три месяца (от переданной даты)."""

    filtered_by_date, start_date = filter_by_month_period(transactions, date)

    def calculate_average(workday: bool = True) -> float | Any:
        if workday:
            filtered_by_weekday = list(
                filter(lambda x: create_dt_obj(x["Дата операции"]).weekday() < 5, filtered_by_date)
            )
        else:
            filtered_by_weekday = list(
                filter(lambda x: create_dt_obj(x["Дата операции"]).weekday() > 4, filtered_by_date)
            )
        length = len(filtered_by_weekday)
        reports_logger.info(f"Получено {length} значений для {"будних" if workday else "выходных"} дней")
        if length:
            return round(sum([x["Сумма операции"] for x in filtered_by_weekday]) / length, 2)
        return 0.0

    return pd.DataFrame(
        {
            "workday": [calculate_average()],
            "weekend": [calculate_average(False)],
            "start_date": [start_date.strftime("%d.%m.%Y %H:%M:%S")],
            "end_date": [date],
        }
    )
