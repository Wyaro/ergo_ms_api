import json
import string

def get_technologies(technology_id: int = None):
    """
    Возвращает SQL-запрос и параметры для получения данных о технологиях.

    Args:
        technology_id (int, optional): ID технологии. Если не указан, возвращает запрос для всех технологий.

    Returns:
        tuple: Кортеж, содержащий SQL-запрос и параметры для выполнения запроса.
               - SQL-запрос (str): Запрос для выборки данных о технологиях.
               - Параметры (tuple): Кортеж с параметрами для запроса (technology_id, если указан).
    """
    if technology_id is not None:
        return (
            """
            select
                id,
                name,
                description,
                popularity,
                rating
            from
                learning_analytics_data_formalization_submodule_technology
            where id = %s
            """,
            (technology_id,),  # Параметр для подстановки в SQL-запрос
        )
    else:
        return (
            """
            select
                *
            from
                learning_analytics_data_formalization_submodule_technology
            """,
            (),  # Пустой кортеж параметров, так как запрос не требует параметров
        )
        
def get_competentions(competency_id: int = None):
    """
    Возвращает SQL-запрос и параметры для получения данных о компетенциях.

    Args:
        competency_id (int, optional): ID компетенции. Если не указан, возвращает запрос для всех компетенций.

    Returns:
        tuple: Кортеж, содержащий SQL-запрос и параметры для выполнения запроса.
               - SQL-запрос (str): Запрос для выборки данных о компетенциях.
               - Параметры (tuple): Кортеж с параметрами для запроса (competency_id, если указан).
    """
    if competency_id is not None:
        return (
            """
            select
                id,
                code,
                name,
                description
            from
                learning_analytics_data_formalization_submodule_competency
            where id = %s
            """,
            (competency_id,),  # Параметр для подстановки в SQL-запрос
        )
    else:
        return (
            """
            select
                *
            from
                learning_analytics_data_formalization_submodule_competency
            """,
            (),  # Пустой кортеж параметров, так как запрос не требует параметров
        )


# SQL-запрос для получения информации о специальностях
def get_specialities(speciality_id: int = None):
    """
    Возвращает SQL-запрос и параметры для получения данных о специальностях.

    Args:
        speciality_id (int, optional): ID специальности. Если не указан, возвращает запрос для всех специальностей.

    Returns:
        tuple: Кортеж, содержащий SQL-запрос и параметры для выполнения запроса.
               - SQL-запрос (str): Запрос для выборки данных о специальностях.
               - Параметры (tuple): Кортеж с параметрами для запроса (speciality_id, если указан).
    """
    if speciality_id is not None:
        return (
            """
            select
                id,
                code,
                name,
                specialization,
                department,
                faculty,
                education_duration,
                year_of_admission
            from
                learning_analytics_data_formalization_submodule_speciality
            where id = %s
            """,
            (speciality_id,),  # Параметр для подстановки в SQL-запрос
        )
    else:
        return (
            """
            select
                *
            from
                learning_analytics_data_formalization_submodule_speciality
            """,
            (),  # Пустой кортеж параметров, так как запрос не требует параметров
        )

# SQL-запрос для получения информации о дисциплинах
def get_disciplines(discipline_id: int = None):
    """
    Возвращает SQL-запрос и параметры для получения данных о дисциплинах.

    Args:
        discipline_id (int, optional): ID дисциплины. Если не указан, возвращает запрос для всех дисциплин.

    Returns:
        tuple: Кортеж, содержащий SQL-запрос и параметры для выполнения запроса.
               - SQL-запрос (str): Запрос для выборки данных о дисциплинах.
               - Параметры (tuple): Кортеж с параметрами для запроса (discipline_id, если указан).
    """
    if discipline_id is not None:
        return (
            """
            select
                id,
                code,
                name,
                semesters,
                contact_work_hours,
                independent_work_hours,
                controle_work_hours,
                competencies
            from
                learning_analytics_data_formalization_submodule_discipline
            where id = %s
            """,
            (discipline_id,),  # Параметр для подстановки в SQL-запрос
        )
    else:
        return (
            """
            select
                *
            from
                learning_analytics_data_formalization_submodule_discipline
            """,
            (),  # Пустой кортеж параметров, так как запрос не требует параметров
        )

# SQL-запрос для получения информации о матрице компетенций
def get_academicCompetenceMatrix(matrix_id: int = None):
    """
    Возвращает SQL-запрос и параметры для получения данных о матрице компетенций.

    Args:
        matrix_id (int, optional): ID матрицы. Если не указан, возвращает запрос для всех матриц.

    Returns:
        tuple: Кортеж, содержащий SQL-запрос и параметры для выполнения запроса.
               - SQL-запрос (str): Запрос для выборки данных о матрицах компетенций.
               - Параметры (tuple): Кортеж с параметрами для запроса (matrix_id, если указан).
    """
    if matrix_id is not None:
        return (
            """
            select
                id,
                speciality_id,
                discipline_list,
                technology_stack
            from
                learning_analytics_data_formalization_submodule_acm
            where id = %s
            """,
            (matrix_id,),  # Параметр для подстановки в SQL-запрос
        )
    else:
        return (
            """
            select
                *
            from
                learning_analytics_data_formalization_submodule_acm
            """,
            (),  # Пустой кортеж параметров, так как запрос не требует параметров
        )

# SQL-запрос для получения информации о компетентностном профиле вакансии
def get_competencyProfileOfVacancy(cp_id: int = None, employer_id: int = None):
    """
    Возвращает SQL-запрос и параметры для получения данных о компетентностном профиле вакансии.

    Args:
        cp_id (int, optional): ID профиля вакансии. Если не указан, возвращает запрос для всех профилей.
        employer_id (int, optional): ID работодателя. Если не указан, возвращает запрос для всех работодателей.

    Returns:
        tuple: Кортеж, содержащий SQL-запрос и параметры для выполнения запроса.
               - SQL-запрос (str): Запрос для выборки данных о профилях вакансий.
               - Параметры (tuple): Кортеж с параметрами для запроса.
    """
    if cp_id is not None:
        return (
            """
            select
                id,
                vacancy_name,
                employer_id,
                competencies_stack,
                technology_stack,
                descr
            from
                learning_analytics_data_formalization_submodule_vcm
            where id = %s
            """,
            (cp_id,),
        )
    elif employer_id is not None:
        return (
            """
            select
                id,
                vacancy_name,
                employer_id,
                competencies_stack,
                technology_stack,
                descr
            from
                learning_analytics_data_formalization_submodule_vcm
            where employer_id = %s
            """,
            (employer_id,),
        )
    else:
        return (
            """
            select
                *
            from
                learning_analytics_data_formalization_submodule_vcm
            """,
            (),
        )


# SQL-запрос для получения информации о пользовательской матрице компетенций
def get_userCompetenceMatrix(matrix_id: int = None):
    """
    Возвращает SQL-запрос и параметры для получения данных о пользовательской матрице компетенций.

    Args:
        matrix_id (int, optional): ID матрицы. Если не указан, возвращает запрос для всех матриц.

    Returns:
        tuple: Кортеж, содержащий SQL-запрос и параметры для выполнения запроса.
               - SQL-запрос (str): Запрос для выборки данных о матрицах компетенций.
               - Параметры (tuple): Кортеж с параметрами для запроса (matrix_id, если указан).
    """
    if matrix_id is not None:
        return (
            """
            select
                id,
                user_id,
                competencies_stack,
                technology_stack
            from
                learning_analytics_data_formalization_submodule_ucm
            where id = %s
            """,
            (matrix_id,),  # Параметр для подстановки в SQL-запрос
        )
    else:
        return (
            """
            select
                *
            from
                learning_analytics_data_formalization_submodule_ucm
            """,
            (),  # Пустой кортеж параметров, так как запрос не требует параметров
        )