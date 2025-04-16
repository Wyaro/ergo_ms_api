import json
import string

def get_specialities(speciality_id: int = None):
    """Получение данных о специальностях"""
    if speciality_id is not None:
        return (
            "SELECT * FROM la_df_speciality WHERE id = %s",
            (speciality_id,)
        )
    return ("SELECT * FROM la_df_speciality", ())

def get_curriculum(curriculum_id: int = None):
    """Получение данных о учебных планах"""
    if curriculum_id is not None:
        return (
            "SELECT * FROM la_df_curriculum WHERE id = %s",
            (curriculum_id,)
        )
    return ("SELECT * FROM la_df_curriculum", ())

def get_technologies(technology_id: int = None):
    """Получение данных о технологиях"""
    if technology_id is not None:
        return (
            "SELECT * FROM la_df_technology WHERE id = %s",
            (technology_id,)
        )
    return ("SELECT * FROM la_df_technology", ())

def get_competentions(competency_id: int = None):
    """Получение данных о компетенциях"""
    if competency_id is not None:
        return (
            "SELECT * FROM la_df_competency WHERE id = %s",
            (competency_id,)
        )
    return ("SELECT * FROM la_df_competency", ())

def get_base_disciplines(base_discipline_id: int = None):
    """Получение данных о базовых дисциплинах"""
    if base_discipline_id is not None:
        return (
            "SELECT * FROM la_df_base_discipline WHERE id = %s",
            (base_discipline_id,)
        )
    return ("SELECT * FROM la_df_base_discipline", ())

def get_disciplines(discipline_id: int = None):
    """Получение данных о дисциплинах"""
    if discipline_id is not None:
        return (
            "SELECT * FROM la_df_discipline WHERE id = %s",
            (discipline_id,)
        )
    return ("SELECT * FROM la_df_discipline", ())

def get_vacancies(vacancy_id: int = None):
    """Получение данных о вакансиях"""
    if vacancy_id is not None:
        return (
            "SELECT * FROM la_df_vacancy WHERE id = %s",
            (vacancy_id,)
        )
    return ("SELECT * FROM la_df_vacancy", ())

def get_academicCompetenceMatrix(matrix_id: int = None):
    """Получение данных о матрицах академических компетенций"""
    if matrix_id is not None:
        return (
            "SELECT * FROM la_df_academic_competence_matrix WHERE id = %s",
            (matrix_id,)
        )
    return ("SELECT * FROM la_df_academic_competence_matrix", ())

def get_competencyProfileOfVacancy(cp_id: int = None, employer_id: int = None):
    """Получение данных о профилях компетенций вакансий"""
    if cp_id is not None:
        return (
            "SELECT * FROM la_df_competency_profile_of_vacancy WHERE id = %s",
            (cp_id,)
        )
    elif employer_id is not None:
        return (
            "SELECT * FROM la_df_competency_profile_of_vacancy WHERE employer_id = %s",
            (employer_id,)
        )
    return ("SELECT * FROM la_df_competency_profile_of_vacancy", ())

def get_userCompetenceMatrix(matrix_id: int = None):
    """Получение данных о матрицах компетенций пользователей"""
    if matrix_id is not None:
        return (
            "SELECT * FROM la_df_user_competency_matrix WHERE id = %s",
            (matrix_id,)
        )
    return ("SELECT * FROM la_df_user_competency_matrix", ())