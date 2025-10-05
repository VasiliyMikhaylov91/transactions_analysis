import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, Callable, Any

from functools import wraps

from utils import create_dt_obj

import pandas as pd


MONTH_PERIOD = relativedelta(months=3)


def file_record(file_name: str = "record.txt") -> Any:
    def record_func(func: Callable[..., Any]) -> Callable[..., Any] or None:
        @wraps(func)
        def wrap(*args: Any, **kwargs: Any) -> Any:
            with open(file_name, 'a') as file:
                result = func(*args, **kwargs)
                file.write(result)
            return result
        return wrap
    return record_func


@file_record()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    if not date:
        date = datetime.datetime.now()
    else:
        date = create_dt_obj(date)
    start_date = date - MONTH_PERIOD
    filtered_transactions = transactions.drop(transactions.drop(transactions
                                    [date < create_dt_obj(transactions['Дата операции']) <= start_date and
                                    transactions['Категория'] == category].index))
    return pd.DataFrame({'category': [category], 'sum': [filtered_transactions['Сумма операции'].sum()],
                         'start_date': [start_date], 'end_date': [date]})


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    pass


def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    pass