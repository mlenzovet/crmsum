"""
Module for finding date ranges in text using regular expressions and date utilities.
"""
#  As LLM+Langchain are not implemented yet, it is plausible to utilize regex for dates filtering

import re
from datetime import datetime, timedelta
from typing import Tuple, List


def get_re_dates(raw_text: str) -> List:
    """
    Использует регулярные выражения для поиска всех дат в формате YYYY-MM-DD.

    Аргументы:
      raw_text (str): Текст в свободной форме, в котором нужно найти диапазон дат.
                  Например: "расскажи, что Ева делала с 2023-04-28 по 2023-05-05."

    Возвращает:
      dates (list): Список всех найденных в тексте дат в формате YYYY-MM-DD.
    """
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    dates = sorted(re.findall(date_pattern, raw_text))  # sorting might be unnecessary
    return dates


def get_current_date() -> str:
    """
    Возвращает текущую дату.
    Возвращает:
      dates (list): текущая дата в текстовом формате YYYY-MM-DD.
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_next_week_date() -> str:
    """
    Возвращает дату через неделю от текущей.
    Возвращает:
      dates (list): дата через неделю от текущей в текстовом формате YYYY-MM-DD.
    """
    return (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")


def find_date_range(text: str) -> Tuple[str, str]:
    """
    Находит диапазон дат в тексте.
    Аргументы:
    text (str): Текст в свободной форме, в котором нужно найти диапазон дат. Например: "расскажи, что Ева
                делала с 2023-04-28 по 2023-05-05."

    Возвращает:
    start_date (str): Начальная дата диапазона в формате 'YYYY-MM-DD' или текущая дата, если дата не найдена.
    end_date (str): Конечная дата диапазона в формате 'YYYY-MM-DD' или дата через неделю от текущей,
                    если дата не найдена.
    """
    # Edge cases: Unsorted date, single date, different format.
    dates = get_re_dates(text)

    if len(dates) >= 2:
        start_date = dates[0]
        end_date = dates[-1]
    elif len(dates) == 1:
        start_date = dates[0]
        end_date = get_next_week_date()  # if no end date
    else:
        start_date = get_current_date()
        end_date = get_next_week_date()

    return start_date, end_date


if __name__ == '__main__':

    texts = ("расскажи, что Ева делала с 2023-04-28 по 2023-05-05",
             "расскажи, что Ева делала с 2024-04-28 по 2023-05-05",
             "расскажи, что Ева делала 2023-04-28",
             "расскажи, что Ева делала")
    for entry in texts:
        result = find_date_range(entry)
        print(f"Ввод: {entry}:\nРезультат: {result}\n")
