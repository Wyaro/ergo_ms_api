import json
import string
import random

def get_employers(employer_id: int = None):
    """
    Возвращает SQL-запрос и параметры для получения данных о работодателях.

    Args:
        employer_id (int, optional): ID работодателя. Если не указан, возвращает запрос для всех существующих работодателей.

    Returns:
        tuple: Кортеж, содержащий SQL-запрос и параметры для выполнения запроса.
               - SQL-запрос (str): Запрос для выборки данных о работодателях.
               - Параметры (tuple): Кортеж с параметрами для запроса (employer_id, если указан).
    """
    if employer_id is not None:
        return (
            """
            select
                id,
                company_name,
                description,
                email,
                created_at,
                updated_at,
                rating
            from
                learning_analytics_employer
            where id = %s
            """,
            (employer_id,),  # Параметр для подстановки в SQL-запрос
        )
    else:
        return (
            """
            select
                *
            from
                learning_analytics_employer
            """,
            (),  # Пустой кортеж параметров, так как запрос не требует параметров
        )