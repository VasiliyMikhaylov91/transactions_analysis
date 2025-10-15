import os
import pandas as pd

from src.reports import file_record, spending_by_category, spending_by_weekday, spending_by_workday


def test_file_record():
    """
    Тестирование декоратора file_record:
    - Без параметра
    - С параметром
    """

    @file_record()
    def file_record_test():
        return "test"

    @file_record("test.txt")
    def file_record_test2():
        return "test2"

    file_record_test()
    with open("record.txt", "r", encoding="utf-8") as f:
        assert f.read() == "test"
    os.remove("record.txt")

    file_record_test2()
    with open("test.txt", "r", encoding="utf-8") as f:
        assert f.read() == "test2"
    os.remove("test.txt")


def test_spending_by_category(test_df):
    """Тестирование функции spending_by_category"""

    assert (spending_by_category(test_df, "Супермаркеты", "31.12.2021 16:44:00").equals
            (pd.DataFrame({"category":["Супермаркеты"],
                  "sum":[-160.89],
                  "start_date":["30.09.2021 16:44:00"],
                  "end_date":["31.12.2021 16:44:00"]})))
    os.remove("record.txt")


def test_spending_by_weekday(test_df):
    """Тестирование функции spending_by_weekday"""

    assert (spending_by_weekday(test_df, "31.12.2021 16:44:00").equals
            (pd.DataFrame({"monday":[-123.0],
                  "tuesday":[-210.0],
                  "wednesday":[-1411.4],
                  "thursday":[-7.07],
                  "friday":[-160.89],
                  "saturday":[-290.0],
                  "sunday":[-228.0],
                  "start_date":["30.09.2021 16:44:00"],
                  "end_date":["31.12.2021 16:44:00"]})))
    os.remove("record.txt")


def test_spending_by_workday(test_df):
    """Тестирование функции spending_by_workday"""

    assert (spending_by_workday(test_df, "31.12.2021 16:44:00").equals
            (pd.DataFrame({"workday": [-382.47],
                           "weekend": [-259.0],
                           "start_date": ["30.09.2021 16:44:00"],
                           "end_date": ["31.12.2021 16:44:00"]})))
    os.remove("record.txt")
