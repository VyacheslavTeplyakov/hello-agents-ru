"""
Модуль обработки данных
Для обработки и преобразования данных
"""

import pandas as pd
from typing import List, Dict, Any


def process_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Обработать исходные данные и вернуть DataFrame

    Args:
        data: Список исходных данных

    Returns:
        Обработанный DataFrame
    """
    # TODO: Добавить логику валидации данных
    df = pd.DataFrame(data)
    df = clean_data(df)
    df = transform_data(df)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Очистить данные от пустых и аномальных значений

    Args:
        df: Исходный DataFrame

    Returns:
        Очищенный DataFrame
    """
    # TODO: Реализовать более сложную логику очистки
    df = df.dropna()
    df = df.drop_duplicates()
    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Преобразовать формат данных

    Args:
        df: Входной DataFrame

    Returns:
        Преобразованный DataFrame
    """
    # TODO: Добавить больше правил преобразования
    df['processed_date'] = pd.to_datetime(df['date'])
    return df


def aggregate_data(df: pd.DataFrame, group_by: List[str]) -> pd.DataFrame:
    """
    Агрегировать данные

    Args:
        df: Входной DataFrame
        group_by: Список полей группировки

    Returns:
        Агрегированный DataFrame
    """
    return df.groupby(group_by).agg({
        'value': ['sum', 'mean', 'count']
    })


def export_data(df: pd.DataFrame, output_path: str) -> None:
    """
    Экспортировать данные в файл

    Args:
        df: DataFrame для экспорта
        output_path: Путь к выходному файлу
    """
    # TODO: Поддержать больше форматов вывода
    df.to_csv(output_path, index=False)
    print(f"Data exported to {output_path}")
