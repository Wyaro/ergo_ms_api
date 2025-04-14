"""
Views module for the data formalization submodule.

This module contains API views for managing:
- Competency Profiles of Vacancies (CPV)
- Specialties 
- Disciplines
- Academic Competence Matrices (ACM)
- User Competence Matrices (UCM)
- Competencies
- Technologies

Each resource supports standard CRUD operations through GET, POST, PUT, DELETE methods.
"""

# Standard imports
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Third party imports 
from drf_yasg.utils import swagger_auto_schema # type: ignore
from drf_yasg import openapi # type: ignore

# Local imports
from src.core.utils.methods import parse_errors_to_dict
from src.core.utils.base.base_views import BaseAPIView
from src.core.utils.database.main import OrderedDictQueryExecutor

# Models
from src.external.learning_analytics.data_formalization_submodule.models import(
    Technology,
    Competency, 
    Speciality,
    Discipline,
    ACM,
    VCM,
    UCM
)

# Serializers
from src.external.learning_analytics.data_formalization_submodule.serializers import(
    TechnologySerializer,
    CompetencySerializer,
    SpecialitySerializer, 
    DisciplineSerializer,
    AcademicCompetenceMatrixSerializer,
    CompetencyProfileOfVacancySerializer,
    UserCompetenceMatrixSerializer
)

# Database queries
from src.external.learning_analytics.data_formalization_submodule.scripts import(
    get_technologies,
    get_competentions,
    get_specialities,
    get_disciplines,
    get_academicCompetenceMatrix,
    get_competencyProfileOfVacancy
)

#######################
# Competency Profile Views
#######################

class CompetencyProfileOfVacancyGetView(BaseAPIView):
    """View for retrieving competency profiles of vacancies."""
    @swagger_auto_schema(
        operation_description="Получение информации о компетентностных профилях вакансий. Если указан параметр 'id', возвращается конкретный профиль. Если указан параметр 'employer_id', возвращаются профили для конкретного работодателя. Если ни один параметр не указан, возвращаются все профили.",
        manual_parameters=[
            openapi.Parameter(
                'id',  # Имя параметра
                openapi.IN_QUERY,  # Параметр передается в query-строке
                type=openapi.TYPE_INTEGER,  # Тип параметра (целочисленный)
                required=False,
                description="Идентификатор компетентностного профиля вакансии (опционально)",  # Описание параметра
            ),
            openapi.Parameter(
                'employer_id',  # Имя параметра
                openapi.IN_QUERY,  # Параметр передается в query-строке
                type=openapi.TYPE_INTEGER,  # Тип параметра (целочисленный)
                required=False,
                description="Идентификатор работодателя (опционально)",  # Описание параметра
            )
        ],
        responses={
            200: "Информация о компетентностных профилях вакансий",  # Успешный ответ
            404: "Профиль с указанным ID не найден",  # Ошибка 404
            400: "Ошибка"  # Ошибка
        }
    )
    def get(self, request):
        """
        Обработка GET-запроса для получения информации о компетентностных профилях вакансий.
        В случае передачи параметра 'id', возвращает данные о конкретном профиле.
        В случае передачи параметра 'employer_id', возвращает данные о профилях для конкретного работодателя.
        Если ни один параметр не передан - возвращаются все профили.
        """
        cp_id = request.query_params.get('id')  # Получаем параметр 'id' из query-строки
        employer_id = request.query_params.get('employer_id')  # Получаем параметр 'employer_id' из query-строки

        if cp_id:
            # Если передан 'id', получаем данные о конкретном профиле
            profile = OrderedDictQueryExecutor.fetchall(
                get_competencyProfileOfVacancy, cp_id=cp_id
            )
            if not profile:
                # Если профиль не обнаружен - возвращаем ошибку 404
                return Response(
                    {"message": "Компетентностный профиль вакансии с указанным ID не найден"},
                    status=status.HTTP_404_NOT_FOUND
                )
            # Формируем успешный ответ с данными о профиле
            response_data = {
                "data": profile,
                "message": "Компетентностный профиль вакансии получен успешно"
            }
        elif employer_id:
            # Если передан 'employer_id', получаем данные о профилях для конкретного работодателя
            profiles = OrderedDictQueryExecutor.fetchall(
                get_competencyProfileOfVacancy, employer_id=employer_id
            )
            if not profiles:
                # Если профили не обнаружены - возвращаем ошибку 404
                return Response(
                    {"message": "Компетентностные профили вакансий для указанного работодателя не найдены"},
                    status=status.HTTP_404_NOT_FOUND
                )
            # Формируем успешный ответ с данными о профилях
            response_data = {
                "data": profiles,
                "message": "Компетентностные профили вакансий для указанного работодателя получены успешно"
            }
        else:
            # Если ни один параметр не передан, получаем данные обо всех профилях
            profiles = OrderedDictQueryExecutor.fetchall(get_competencyProfileOfVacancy)
            # Формируем успешный ответ с данными обо всех профилях
            response_data = {
                "data": profiles,
                "message": "Все компетентностные профили вакансий получены успешно"
            }

        # Возвращаем ответ с данными и статусом 200
        return Response(response_data, status=status.HTTP_200_OK)

class CompetencyProfileOfVacancySendView(BaseAPIView):
    """View for creating one or multiple competency profiles of vacancies."""
    @swagger_auto_schema(
        operation_description="Создание одного или нескольких компетентностных профилей вакансий",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'vacancy_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'employer_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'competencies_stack': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'technology_stack': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                },
                required=['vacancy_name', 'employer_id', 'competencies_stack', 'technology_stack', 'description']
            )
        ),
        responses={
            201: "Профиль/профили вакансий успешно созданы",
            400: "Ошибка валидации данных"
        }
    )
    def post(self, request):
        """
        Обрабатывает POST-запрос для создания одного или нескольких профилей.
        Поддерживает как одиночные объекты, так и массивы.
        """
        data = request.data

        if isinstance(data, list):
            serializer = CompetencyProfileOfVacancySerializer(data=data, many=True)
        else:
            serializer = CompetencyProfileOfVacancySerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Профиль/профили вакансий сохранены успешно"},
                status=status.HTTP_201_CREATED
            )

        errors = parse_errors_to_dict(serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

class CompetencyProfileOfVacancyPutView(BaseAPIView):
    """View for updating competency profiles of vacancies."""
    @swagger_auto_schema(
        operation_description="Обновление информации о компетентностном профиле вакансии",
        request_body=CompetencyProfileOfVacancySerializer,
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор компетентностного профиля вакансии"
            )
        ],
        responses={
            200: "Информация о компетентностном профиле вакансии обновлена успешно",
            400: "Ошибка валидации данных",
            404: "Компетентностный профиль вакансии не найден"
        }
    )
    def put(self, request):
        """
        Обновление информации о компетентностном профиле вакансии (обработка PUT-запроса).
        """
        cp_id = request.query_params.get('id')
        if not cp_id:
            return Response(
                {"message": "Идентификатор компетентностного профиля вакансии не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cp = CompetencyProfileOfVacancy.objects.get(id=cp_id)
        except CompetencyProfileOfVacancy.DoesNotExist:
            return Response(
                {"message": "Компетентностный профиль вакансии с указанным ID не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompetencyProfileOfVacancySerializer(cp, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(
                {"message": "Ошибка валидации данных", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновляем данные компетентностного профиля вакансии
        serializer.save()
    
        # Получаем обновленные данные
        updated_competency_profile_of_vacancy = OrderedDictQueryExecutor.fetchall(
            get_competencyProfileOfVacancy, cp_id=cp_id
        )

        response_data = {
            "data": updated_competency_profile_of_vacancy,
            "message": "Информация о компетентностном профиле вакансии обновлена успешно"
        }

        return Response(response_data, status=status.HTTP_200_OK)

class CompetencyProfileOfVacancyDeleteView(BaseAPIView):
    """View for deleting competency profiles of vacancies."""
    @swagger_auto_schema(
        operation_description="Удаление компетентностного профиля вакансии по идентификатору",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор компетентностного профиля вакансии"
            )
        ],
        responses={
            204: "Компетентностный профиль вакансии успешно удален",  # Успешный ответ (без содержимого)
            400: "Идентификатор компетентностного профиля вакансии не указан",  # Ошибка
            404: "Компетентностный профиль вакансии не найден"  # Ошибка
        }
    )
    def delete(self, request):
        """
        Обработка DELETE-запроса для удаления компетентностного профиля вакансии.
        """
        cp_id = request.query_params.get('id')  # Получаем параметр 'id' из query-строки
        
        try:
            cp_id = int(cp_id) if cp_id else None
            if not cp_id:
                raise ValueError("ID is required")
        except (ValueError, TypeError):
            return Response(
                {"message": "Идентификатор компетентностного профиля вакансии не указан или имеет неверный формат"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cp = CompetencyProfileOfVacancy.objects.get(id=cp_id)  # Ищем компетенцию по ID
        except CompetencyProfileOfVacancy.DoesNotExist:
            return Response(
                {"message": "Компетентностный профиль вакансии с указанным ID не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        cp.delete()  # Удаляем компетенцию из базы данных

        return Response(
            {"message": "Компетентностный профиль вакансии успешно удален"},
            status=status.HTTP_204_NO_CONTENT
        )

#######################
# Specialty Views 
#######################

class SpecialityGetView(BaseAPIView):
    """View for retrieving specialties."""
    @swagger_auto_schema(
        operation_description="Получение информации о направлениях подготовки. Если указан параметр 'id', возвращается конкретное направление. Если параметр 'id' не указан, возвращаются все направления",
        manual_parameters=[
            openapi.Parameter(
                'id', # Имя параметра
                openapi.IN_QUERY, # Параметр передается в query-строке
                type = openapi.TYPE_INTEGER, # Тип параметра (целочисленный)
                required=False,
                description="Идентификатор направления подготовки (опционально)", # Описание параметра
            )
        ],
        responses={
            200: "Информация о направлениях подготовки", # Успешный ответ
            400: "Ошибка" # Ошибка
        }
    )
    def get(self, request):
        """
        Обработка GET-запроса для получения информации о направлениях подготовки.
        В случае передачи параметра 'id', возвращает данные о направлениях подготовки.
        Если параметр 'id' не передан - возвращаются все данные о направлениях подготовки.
        """
        speciality_id = request.query_params.get('id') # Получаем параметр 'id' из query-строки

        if speciality_id:
            # Если передан 'id', получаем данные о конкретной специальности
            speciality = OrderedDictQueryExecutor.fetchall(
                get_specialities, speciality_id = speciality_id
            )
            if not speciality:
                # Если специальность не обнаружена - возвращаем ошибку 404
                return Response(
                    {"message": "Направление подготовки (специальность) с указанным ID не найдена"},
                    status = status.HTTP_404_NOT_FOUND
                )
            # Формируем успешный ответ с данными о специальности
            response_data = {
                "data": speciality,
                "message": "Специальность получена успешно"
            }
        else:
            # Если 'id' не передан, получаем данные обо всех специальностях
            specialities = OrderedDictQueryExecutor.fetchall(get_specialities)
            # Формируем успешный ответ с данными обо всех специальностях
            response_data = {
                "data": specialities,
                "message": "Все специальности получены успешно"
            }

        # Возвращаем ответ с данными и статусом 200
        return Response(response_data, status=status.HTTP_200_OK)

class SpecialitySendView(BaseAPIView):
    """View for creating one or multiple specialties."""
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких специальностей",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'code': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Код специальности (например, 10.05.04)'
                        ),
                    'name': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Наименование'
                        ),
                    'specialization': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Специализация'
                        ),
                    'department': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Кафедра'
                        ),
                    'faculty': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Факультет'
                        ), 
                    'education_duration': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Длительность обучения'
                        ),
                    'year_of_admission': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Год поступления'
                        )
                },
                required=['code', 'name', 'specialization', 'department', 'faculty', 'education_duration', 'year_of_admission'],

                example={
                    "code": "09.03.01",
                    "name": "Информатика и вычислительная техника",
                    "specialization": "Программное обеспечение",  
                    "department": "Кафедра информатики",
                    "faculty": "Факультет информационных технологий",
                    "education_duration": 4,
                    "year_of_admission": "2023"
                }
            )
        ),
        responses={
            201: "Специальность/специальности успешно созданы",
            400: "Ошибка валидации данных"
        },
    )
    def post(self, request):
        """
        Обрабатывает POST-запрос для создания одной или нескольких специальностей.
        Поддерживает как одиночные объекты, так и массивы.
        """

        try:
            data = request.data
            serializer = SpecialitySerializer(
                data=data,
                many=isinstance(data, list)
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Специальность/специальности сохранены успешно"},
                    status = status.HTTP_201_CREATED
                )
            
            return Response(
                parse_errors_to_dict(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            return Response(
                {"message": f"Ошибка при создании специальности: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class SpecialityPutView(BaseAPIView):
    """View for updating specialties."""
    @swagger_auto_schema(
        operation_description="Обновление информации о специальности",
        request_body=SpecialitySerializer,
        responses={
            200: "Информация о специальности обновлена успешно",
            400: "Ошибка валидации данных",
            404: "Специальность не найдена"
        }
    )
    def put(self, request, pk):
        """
        Обновление информации о специальности (обработка PUT-запроса).
        """

        try:
            speciality_id = int(pk)
        except (TypeError, ValueError):
            return Response(
                {"message":"Неверный формат идентификатора специальности"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            speciality = Speciality.objects.get(id=speciality_id)
        except Speciality.DoesNotExist:
            return Response(
                {"message":"Компетенция с указанным ID не найдена"},
                status=status.HTTP_400_BAD_REQUEST
            )
       
        serializer = SpecialitySerializer(speciality, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(
                {
                    "message":"Ошибка валидации данных",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)



class SpecialityDeleteView(BaseAPIView):
    """View for deleting specialties."""
    @swagger_auto_schema(
        operation_description="Удаление специальности по идентификатору",
        responses={
            204: "Специальность успешно удалена",  # Успешный ответ (без содержимого)
            400: "Идентификатор специальности не указан",  # Ошибка
            404: "Специальность не найдена"  # Ошибка
        }
    )
    def delete(self, request, pk):
        """
        Обработка DELETE-запроса для удаления специальности.
        """
        try:
            speciality = Speciality.objects.get(id=pk)
            speciality.delete()

            return Response(
                {
                    "message": "Компетенция успешно удалена"
                },
                status=status.HTTP_200_OK
            )
        
        except Speciality.DoesNotExist:
            return Response(
                {
                    "message": "Компетенция не найдена"
                },
                status=status.HTTP_404_NOT_FOUND
            )

#######################
# Discipline Views
#######################

class DisciplineGetView(BaseAPIView):
    """View for retrieving disciplines."""
    @swagger_auto_schema(
        operation_description="Получение информации о дисциплинах",
        responses={
            200: "Информация о дисциплинах получена успешно",
            404: "Дисциплина не найдена"
        }
    )
    def get(self, request, pk=None):
        """
        Получение информации о дисциплинах.
        Если указан pk, возвращает конкретную дисциплину.
        Иначе возвращает список всех дисциплин.
        """
        try:
            if (pk):
                discipline = OrderedDictQueryExecutor.fetchall(
                    get_disciplines, discipline_id=pk
                )
                if not discipline:
                    return Response(
                        {"message": "Дисциплина не найдена"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                response_data = {
                    "data": discipline,
                    "message": "Дисциплина получена успешно"
                }
            else:
                disciplines = OrderedDictQueryExecutor.fetchall(get_disciplines)
                response_data = {
                    "data": disciplines,
                    "message": "Все дисциплины получены успешно"
                }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": f"Ошибка при получении дисциплин: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class DisciplineSendView(BaseAPIView):
    """View for creating disciplines."""
    @swagger_auto_schema(
        operation_description="Создание дисциплины",
        request_body = openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'code' : openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Код дисциплины (например, Б1.О.11)'
                    ),
                    'name': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Наименование'
                    ),
                    'semesters' : openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Семестры (3,4) - максимум 6'
                    ),
                    'contact_work_hours' : openapi.Schema(
                        type = openapi.TYPE_INTEGER,
                        description='Контактная работа, ч'
                    ),
                    'independent_work_hours' : openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Самостоятельная работа, ч'
                    ),
                    'control_work_hours' : openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Контроль, ч'
                    ),
                    'competencies' : openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'code': openapi.Schema(type=openapi.TYPE_STRING),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'description': openapi.Schema(type=openapi.TYPE_STRING),
                                'know_level': openapi.Schema(type=openapi.TYPE_STRING),
                                'can_level': openapi.Schema(type=openapi.TYPE_STRING),
                                'master_level': openapi.Schema(type=openapi.TYPE_STRING),
                                'blooms_level': openapi.Schema(type=openapi.TYPE_STRING),
                                'blooms_verbs': openapi.Schema(type=openapi.TYPE_STRING),
                                'complexity': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'demand': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        ),
                        description='Компетенции'
                    )
                },

                required=['code','name','semesters','contact_work_hours','independent_work_hours',
                'control_work_hours','competencies'],

                example={
                    'code': "Б1.О.45",
                    'name': "Формализованные модели и методы решения аналитических задач",
                    'semesters': "7,8",
                    'contact_work_hours': "192",
                    'independent_work_hours': "60",
                    'control_work_hours': "36",
                    'competencies': [
                        {
                            "code": "DATA012",
                            "name": "Анализ данных",
                            "description": "Методы обработки и анализа больших данных",
                            "know_level": "Знать методы анализа и визуализации данных",
                            "can_level": "Уметь применять статистические методы",
                            "master_level": "Владеть инструментами анализа данных",
                            "blooms_level": "ANALYZE",
                            "blooms_verbs": "анализировать, интерпретировать, визуализировать",
                            "complexity": 8,
                            "demand": 9
                        },
                        {
                            "code": "UI013",
                            "name": "UI/UX дизайн",
                            "description": "Проектирование пользовательских интерфейсов",
                            "know_level": "Знать принципы UI/UX дизайна",
                            "can_level": "Уметь создавать удобные интерфейсы",
                            "master_level": "Владеть инструментами прототипирования",
                            "blooms_level": "CREATE",
                            "blooms_verbs": "проектировать, создавать, улучшать",
                            "complexity": 6,
                            "demand": 7
                        }
                    ]
                }
            )
        ),
        responses={
            201: "Дисциплина успешно создана",
            400: "Ошибка валидации данных"
        }
    )
    def post(self, request):
        try:
            data = request.data
            serializer = DisciplineSerializer(
                data=data,
                many=isinstance(data, list)
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Дисциплина сохранена успешно"},
                    status=status.HTTP_201_CREATED
                )
            
            return Response(
                parse_errors_to_dict(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            return Response(
                {"message": f"Ошибка при создании дисциплины: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class DisciplinePutView(BaseAPIView):
    """View for updating disciplines."""
    @swagger_auto_schema(
        operation_description="Обновление информации о дисциплине",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'code': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Код дисциплины (например, Б1.О.11)'
                ),
                'name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Наименование'
                ),
                'semesters': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Семестры (3,4) - максимум 6'
                ),
                'contact_work_hours': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Контактная работа, ч'
                ),
                'independent_work_hours': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Самостоятельная работа, ч'
                ),
                'control_work_hours': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Контроль, ч'
                ),
                'competencies': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'code': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                            'know_level': openapi.Schema(type=openapi.TYPE_STRING),
                            'can_level': openapi.Schema(type=openapi.TYPE_STRING),
                            'master_level': openapi.Schema(type=openapi.TYPE_STRING),
                            'blooms_level': openapi.Schema(type=openapi.TYPE_STRING),
                            'blooms_verbs': openapi.Schema(type=openapi.TYPE_STRING),
                            'complexity': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'demand': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    ),
                    description='Компетенции'
                )
            },
            required=['code'],
            example={
                'code': "Б1.О.45",
                'name': "Формализованные модели и методы решения аналитических задач",
                'semesters': "7,8",
                'contact_work_hours': "192",
                'independent_work_hours': "60",
                'control_work_hours': "36",
                'competencies': [
                    {
                        "code": "DATA012",
                        "name": "Анализ данных",
                        "description": "Методы обработки и анализа больших данных",
                        "know_level": "Знать методы анализа и визуализации данных",
                        "can_level": "Уметь применять статистические методы",
                        "master_level": "Владеть инструментами анализа данных",
                        "blooms_level": "ANALYZE",
                        "blooms_verbs": "анализировать, интерпретировать, визуализировать",
                        "complexity": 8,
                        "demand": 9
                    }
                ]
            }
        ),
        responses={
            400: "Ошибка валидации данных",
            404: "Дисциплина не найдена"
        }
    )
    def put(self, request, pk):
        try:
            discipline_id = int(pk)
        except (TypeError, ValueError):
            return Response(
                {"message": "Неверный формат идентификатора дисциплины"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            discipline = Discipline.objects.get(id=discipline_id)
        except Discipline.DoesNotExist:
            return Response(
                {"message": "Дисциплина с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
       
        serializer = DisciplineSerializer(discipline, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Ошибка валидации данных",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class DisciplineDeleteView(BaseAPIView):
    """View for deleting disciplines."""
    @swagger_auto_schema(
        operation_description="Удаление дисциплины по ID",
        responses={
            204: "Дисциплина успешно удалена",
            404: "Дисциплина не найдена"
        }
    )
    def delete(self, request, pk):
        try:
            discipline = Discipline.objects.get(id=pk)
            discipline.delete()
            return Response(
                {"message": "Дисциплина успешно удалена"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Discipline.DoesNotExist:
            return Response(
                {"message": "Дисциплина не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

#######################
# Academic Competence Matrix Views
#######################

class AcademicCompetenceMatrixGetView(BaseAPIView):
    """View for retrieving academic competence matrices."""
    @swagger_auto_schema(
        operation_description="Получение информации об академической матрице компетенций. Если указан параметр 'id', возвращается конкретная матрица. Если параметр 'id' не указан, возвращаются все существующие матрицы.",
        manual_parameters=[
            openapi.Parameter(
                'id', # Имя параметра
                openapi.IN_QUERY, # Параметр передается в query-строке
                type = openapi.TYPE_INTEGER, # Тип параметра (целочисленынй)
                required=False,
                description="Идентификатор академической матрицы компетенций (опционально)", # Описание параметра
            )
        ],
        responses={
            200: "Информация о матрицах академических компетенций", # Успешный ответ
            400: "Ошибка" # Ошибка
        }
    )
    def get(self, request):
        """
        Обработка GET-запроса для получения информации о матрицах академических компетенций.
        В случае передачи параметра 'id', возвращает данные о матрицах академических компетенций.
        Если параметр 'id' не передан - возвращаются все данные о матрицах академических компетенций.
        """

        matrix_id = request.query_params.get('id') # Полчаем параметр 'id' из query-строки

        if matrix_id:
            # Если передан 'id', получаем данные о конкретной дисциплине
            matrix = OrderedDictQueryExecutor.fetchall(
                get_academicCompetenceMatrix, matrix_id = matrix_id
            )
            if not matrix:
                # Если дисциплина не обнаружена - возвращаем ошибку 404
                return Response(
                    {"message": "Матрица академических компетенций с указанным ID не найдена"},
                    status = status.HTTP_404_NOT_FOUND
                )
            response_data = {
                "data": matrix,
                "message": "Матрица академических компетенций получена успешно."
            }
        else:
            # Если 'id' не передан, получаем данные обо всех специальностях
            matrices = OrderedDictQueryExecutor.fetchall(get_academicCompetenceMatrix)
            # Формируем успешный ответ с данными обо всех специальностях
            response_data = {
                "data": matrices,
                "message": "Все матрицы академических компетенций получены успешно"
            }

        # Возвращаем ответ с данными и статусом 200
        return Response(response_data, status=status.HTTP_200_OK)

class AcademicCompetenceMatrixSendView(BaseAPIView):
    """View for creating academic competence matrices."""
    @swagger_auto_schema(
        operation_description="Проверка ввода матрицы академических компетенций",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'speciality_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'discipline_list': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'technology_stack': openapi.Schema(type=openapi.TYPE_OBJECT)
                },
                required=['speciality_id', 'discipline_list', 'technology_stack']
            )
        ),
        responses={
            201: "Матрица/матрицы успешно созданы",
            400: "Ошибка валидации данных"
        },
        examples={
            'single': {
                "value": {
                    "speciality_id": 1,
                    "discipline_list": [
                        {
                            "id": 1,
                            "name": "Программирование",
                            "semester": 1,
                            "competencies": ["ПК-1", "ПК-2"]
                        },
                        {
                            "id": 2,
                            "name": "Базы данных",
                            "semester": 2,
                            "competencies": ["ПК-3", "ПК-4"]
                        }
                    ],
                    "technology_stack": [
                        {
                            "id": 1,
                            "name": "Python",
                            "semester_start": 1,
                            "semester_end": 4
                        },
                        {
                            "id": 2,
                            "name": "PostgreSQL", 
                            "semester_start": 2,
                            "semester_end": 4
                        }
                    ]
                }
            },
            'multiple': {
                "value": [
                    {
                        "speciality_id": 1,
                        "discipline_list": [
                            {
                                "id": 1, 
                                "name": "Программирование",
                                "semester": 1,
                                "competencies": ["ПК-1", "ПК-2"]
                            }
                        ],
                        "technology_stack": [
                            {
                                "id": 1,
                                "name": "Python",
                                "semester_start": 1,
                                "semester_end": 4
                            }
                        ]
                    },
                    {
                        "speciality_id": 2,
                        "discipline_list": [
                            {
                                "id": 3,
                                "name": "Базы данных", 
                                "semester": 2,
                                "competencies": ["ПК-3", "ПК-4"]
                            }
                        ],
                        "technology_stack": [
                            {
                                "id": 2,
                                "name": "PostgreSQL",
                                "semester_start": 2, 
                                "semester_end": 4
                            }
                        ]
                    }
                ]
            }
        }
    )
    def post(self, request):
        data = request.data

        if isinstance(data, list):
            serializer = AcademicCompetenceMatrixSerializer(data=data, many=True)
        else:
            serializer = AcademicCompetenceMatrixSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Академическая матрица/матрицы компетенций сохранены успешно"},
                status=status.HTTP_201_CREATED
            )

        errors = parse_errors_to_dict(serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

class AcademicCompetenceMatrixPutView(BaseAPIView):
    """View for updating academic competence matrices."""
    @swagger_auto_schema(
        operation_description="Обновление информации о матрице академических компетенций",
        request_body=AcademicCompetenceMatrixSerializer,
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор матрицы академических компетенций"
            )
        ],
        responses={
            200: "Информация о матрице академических компетенций обновлена успешно",
            400: "Ошибка валидации данных",
            404: "Матрица академических компетенций не найдена"
        }
    )
    def put(self, request):
        """
        Обновление информации о матрице академических компетенций (обработка PUT-запроса).
        """
        matrix_id = request.query_params.get('id')
        if not matrix_id:
            return Response(
                {"message": "Идентификатор матрицы академических компетенций не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            matrix = AcademicCompetenceMatrix.objects.get(id=matrix_id)
        except AcademicCompetenceMatrix.DoesNotExist:
            return Response(
                {"message": "Матрица академических компетенций с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AcademicCompetenceMatrixSerializer(matrix, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(
                {"message": "Ошибка валидации данных", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновляем данные специальности
        serializer.save()
    
        # Получаем обновленные данные
        updated_matrix = OrderedDictQueryExecutor.fetchall(
            get_academicCompetenceMatrix, matrix_id=matrix_id
        )

        response_data = {
            "data": updated_matrix,
            "message": "Информация о матрице академических компетенций обновлена успешно"
        }

        return Response(response_data, status=status.HTTP_200_OK)

class AcademicCompetenceMatrixDeleteView(BaseAPIView):
    """View for deleting academic competence matrices."""
    @swagger_auto_schema(
        operation_description="Удаление матрицы академических компетенций по идентификатору",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор матрицы академических компетенций"
            )
        ],
        responses={
            204: "Специальность успешно удалена",  # Успешный ответ (без содержимого)
            400: "Идентификатор матрицы академических компетенций не указан",  # Ошибка
            404: "Матрица академических компетенций не найдена"  # Ошибка
        }
    )
    def delete(self, request):
        """
        Обработка DELETE-запроса для удаления матрицы академических компетенций.
        """
        matrix_id = request.query_params.get('id')  # Получаем параметр 'id' из query-строки

        if not matrix_id:
            return Response(
                {"message": "Идентификатор матрицы академических компетенций не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            matrix = AcademicCompetenceMatrix.objects.get(id=matrix_id)  # Ищем матрицу академических компетенций по ID
        except AcademicCompetenceMatrix.DoesNotExist:
            return Response(
                {"message": "Матрица академических компетенций с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        matrix.delete()  # Удаляем матрицу академических компетенций из базы данных

        return Response(
            {"message": "Матрица академических компетенций успешно удалена"},
            status=status.HTTP_204_NO_CONTENT
        )

#######################
# User Competence Matrix Views 
#######################

class UserCompetenceMatrixGetView(BaseAPIView):
    """View for retrieving user competence matrices."""
    @swagger_auto_schema(
        operation_description="Получение информации об пользовательской матрице компетенций. Если указан параметр 'id', возвращается конкретная матрица. Если параметр 'id' не указан, возвращаются все существующие матрицы.",
        manual_parameters=[
            openapi.Parameter(
                'id', # Имя параметра
                openapi.IN_QUERY, # Параметр передается в query-строке
                type = openapi.TYPE_INTEGER, # Тип параметра (целочисленынй)
                required=False,
                description="Идентификатор пользовательской матрицы компетенций (опционально)", # Описание параметра
            )
        ],
        responses={
            200: "Информация о матрицах пользовательских компетенций", # Успешный ответ
            400: "Ошибка" # Ошибка
        }
    )
    def get(self, request):
        """
        Обработка GET-запроса для получения информации о матрицах пользовательских компетенций.
        В случае передачи параметра 'id', возвращает данные о матрицах пользовательских компетенций.
        Если параметр 'id' не передан - возвращаются все данные о матрицах пользовательских компетенций.
        """

        matrix_id = request.query_params.get('id') # Полчаем параметр 'id' из query-строки

        if matrix_id:
            # Если передан 'id', получаем данные о конкретной дисциплине
            matrix = OrderedDictQueryExecutor.fetchall(
                get_userCompetenceMatrix, matrix_id = matrix_id
            )
            if not matrix:
                # Если дисциплина не обнаружена - возвращаем ошибку 404
                return Response(
                    {"message": "Матрица пользовательских компетенций с указанным ID не найдена"},
                    status = status.HTTP_404_NOT_FOUND
                )
            response_data = {
                "data": matrix,
                "message": "Матрица пользовательских компетенций получена успешно."
            }
        else:
            # Если 'id' не передан, получаем данные обо всех специальностях
            matrices = OrderedDictQueryExecutor.fetchall(get_userCompetenceMatrix)
            # Формируем успешный ответ с данными обо всех специальностях
            response_data = {
                "data": matrices,
                "message": "Все матрицы пользовательских компетенций получены успешно"
            }

        # Возвращаем ответ с данными и статусом 200
        return Response(response_data, status=status.HTTP_200_OK)

class UserCompetenceMatrixSendView(BaseAPIView):
    """View for creating user competence matrices."""
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких пользовательских матриц компетенций",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'competencies_stack': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'technology_stack': openapi.Schema(type=openapi.TYPE_OBJECT)
                },
                required=['user_id', 'competencies_stack', 'technology_stack']
            )
        ),
        responses={
            201: "Матрица/матрицы успешно созданы",
            400: "Ошибка валидации данных"
        }
    )
    def post(self, request):
        data = request.data

        if isinstance(data, list):
            serializer = UserCompetenceMatrixSerializer(data=data, many=True)
        else:
            serializer = UserCompetenceMatrixSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Матрица/матрицы компетенций пользователя сохранены успешно"},
                status=status.HTTP_201_CREATED
            )

        errors = parse_errors_to_dict(serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

class UserCompetenceMatrixPutView(BaseAPIView):
    """View for updating user competence matrices."""
    @swagger_auto_schema(
        operation_description="Обновление информации о матрице пользовательских компетенций",
        request_body=UserCompetenceMatrixSerializer,
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор матрицы пользовательских компетенций"
            )
        ],
        responses={
            200: "Информация о матрице пользовательских компетенций обновлена успешно",
            400: "Ошибка валидации данных",
            404: "Матрица пользовательских компетенций не найдена"
        }
    )
    def put(self, request):
        """
        Обновление информации о матрице пользовательских компетенций (обработка PUT-запроса).
        """
        matrix_id = request.query_params.get('id')
        if not matrix_id:
            return Response(
                {"message": "Идентификатор матрицы пользовательских компетенций не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            matrix = UCM.objects.get(id=matrix_id)
        except UCM.DoesNotExist:
            return Response(
                {"message": "Матрица пользовательских компетенций с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserCompetenceMatrixSerializer(matrix, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(
                {"message": "Ошибка валидации данных", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновляем данные специальности
        serializer.save()
    
        # Получаем обновленные данные
        updated_matrix = OrderedDictQueryExecutor.fetchall(
            get_userCompetenceMatrix, matrix_id=matrix_id
        )

        response_data = {
            "data": updated_matrix,
            "message": "Информация о матрице пользовательских компетенций обновлена успешно"
        }

        return Response(response_data, status=status.HTTP_200_OK)

class UserCompetenceMatrixDeleteView(BaseAPIView):
    """View for deleting user competence matrices."""
    @swagger_auto_schema(
        operation_description="Удаление матрицы пользовательских компетенций по идентификатору",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор матрицы пользовательских компетенций"
            )
        ],
        responses={
            204: "Матрица пользовательских компетенций успешно удалена",  # Успешный ответ (без содержимого)
            400: "Идентификатор матрицы пользовательских компетенций не указан",  # Ошибка
            404: "Матрица пользовательских компетенций не найдена"  # Ошибка
        }
    )
    def delete(self, request):
        """
        Обработка DELETE-запроса для удаления матрицы пользовательских компетенций.
        """
        matrix_id = request.query_params.get('id')  # Получаем параметр 'id' из query-строки

        if not matrix_id:
            return Response(
                {"message": "Идентификатор матрицы пользовательских компетенций не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            matrix = UCM.objects.get(id=matrix_id)  # Ищем матрицу пользовательских компетенций по ID
        except UCM.DoesNotExist:
            return Response(
                {"message": "Матрица пользовательских компетенций с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        matrix.delete()  # Удаляем матрицу пользовательских компетенций из базы данных

        return Response(
            {"message": "Матрица пользовательских компетенций успешно удалена"},
            status=status.HTTP_204_NO_CONTENT
        )

#######################
# Competency Views
#######################

class CompetencyDeleteView(BaseAPIView):
    """View for deleting competencies through path parameter (RESTful style)."""
    @swagger_auto_schema(
        operation_description="Удаление компетенции по ID из URL",
        responses={
            204: openapi.Response(description="Компетенция успешно удалена"), 
            404: openapi.Response(description="Компетенция не найдена")
        }
    )
    def delete(self, request, pk):
        """
        Обработка DELETE-запроса для удаления компетенции.
        Использует path-параметр pk вместо query-параметра для более RESTful подхода.
        """
        try:
            competency = Competency.objects.get(id=pk)
            competency.delete()
            return Response(
                {"message": "Компетенция успешно удалена"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Competency.DoesNotExist:
            return Response(
                {"message": "Компетенция не найдена"}, 
                status=status.HTTP_404_NOT_FOUND
            )


class CompetencyPutView(BaseAPIView):
    """View for updating competencies."""
    @swagger_auto_schema(
        operation_description="Обновление информации о компетенции",
        request_body=CompetencySerializer,
        responses={
            200: openapi.Response(
                description="Информация о компетенции обновлена успешно",
                schema=CompetencySerializer
            ),
            400: "Ошибка валидации данных",
            404: "Компетенция не найдена"
        }
    )
    def put(self, request, pk):  # Изменили параметр с id на pk
        """
        Обновление информации о компетенции (обработка PUT-запроса).
        """
        try:
            competency_id = int(pk)  # Используем pk вместо id
        except (TypeError, ValueError):
            return Response(
                {"message": "Неверный формат идентификатора компетенции"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            competency = Competency.objects.get(id=competency_id)
        except Competency.DoesNotExist:
            return Response(
                {"message": "Компетенция с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompetencySerializer(competency, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(
                {"message": "Ошибка валидации данных", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class CompetencyGetView(BaseAPIView):    # Исправлено с CompetentionGetView
    """View for retrieving competencies."""
    @swagger_auto_schema(
        operation_description="Получение информации о компетенциях. Если указан параметр 'id', возвращается конкретная компетенция. Если параметр 'id' не указан, возвращаются все компетенции",
        manual_parameters=[
            openapi.Parameter(
                'id', # Имя параметра
                openapi.IN_QUERY, # Параметр передается в query-строке
                type = openapi.TYPE_INTEGER, # Тип параметра (целочисленный)
                required=False,
                description="Идентификатор компетенции (опционально)", # Описание параметра
            )
        ],
        responses={
            200: "Информация о компетенциях", # Успешный ответ
            400: "Ошибка" # Ошибка
        }
    )
    def get(self, request):
        """
        Обработка GET-запроса для получения информации о компетенциях.
        В случае передачи параметра 'id', возвращает данные о конкретной компетенции.
        Если параметр 'id' не передан - возвращаются все данные о компетенциях.
        """
        competency_id = request.query_params.get('id') # Получаем параметр 'id' из query-строки

        if competency_id:
            # Если передан 'id', получаем данные о конкретной компетенции
            competency = OrderedDictQueryExecutor.fetchall(
                get_competentions, competency_id = competency_id
            )
            if not competency:
                # Если компетенция не обнаружена - возвращаем ошибку 404
                return Response(
                    {"message": "Компетенция с указанным ID не найдена"},
                    status = status.HTTP_404_NOT_FOUND
                )
            # Формируем успешный ответ с данными о компетенции
            response_data = {
                "data": competency,
                "message": "Компетенция получена успешно"
            }
        else:
            # Если 'id' не передан, получаем данные обо всех компетенциях
            competentions = OrderedDictQueryExecutor.fetchall(get_competentions)
            # Формируем успешный ответ с данными обо всех компетенциях
            response_data = {
                "data": competentions,
                "message": "Все компетенции получены успешно"
            }

        # Возвращаем ответ с данными и статусом 200
        return Response(response_data, status=status.HTTP_200_OK)

class CompetencySendView(BaseAPIView):
    """Представление для создания одной или нескольких компетенций."""
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких компетенций",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'code': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Код компетенции (например, ПК-1)'
                    ),
                    'name': openapi.Schema(
                        type=openapi.TYPE_STRING, 
                        description='Название компетенции'
                    ),
                    'description': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Подробное описание компетенции'
                    ),
                    'know_level': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Требования к уровню знаний'
                    ),
                    'can_level': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Требования к уровню умений'
                    ),
                    'master_level': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Требования к уровню владения'
                    ),
                    'blooms_level': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Уровень по таксономии Блума'
                    ),
                    'blooms_verbs': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Глаголы действия по таксономии Блума'
                    ),
                    'complexity': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Сложность компетенции (1-10)'
                    ),
                    'demand': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Востребованность на рынке (1-10)'
                    )
                },
                required=['code', 'name', 'description', 'know_level', 'can_level', 
                         'master_level', 'blooms_level', 'complexity', 'demand'],
                example={
                    "code": "ПК-1",
                    "name": "Проектирование и разработка ПО",
                    "description": "Способность проектировать и разрабатывать программное обеспечение",
                    "know_level": "Понимает принципы проектирования ПО",
                    "can_level": "Умеет применять паттерны проектирования",
                    "master_level": "Владеет разработкой сложных систем",
                    "blooms_level": "CREATE",
                    "blooms_verbs": "проектировать, разрабатывать, создавать",
                    "complexity": 8,
                    "demand": 9
                }
            )
        ),
        responses={
            201: "Компетенция/компетенции успешно созданы",
            400: "Ошибка валидации данных"
        }
    )
    def post(self, request):
        """
        Обработка POST-запроса для создания одной или нескольких компетенций.
        Поддерживает как одиночные объекты, так и массивы.
        
        Returns:
            Response: Ответ со статусом 201 при успехе или 400 при ошибке валидации
        """
        try:
            data = request.data
            serializer = CompetencySerializer(
                data=data, 
                many=isinstance(data, list)
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Компетенция/компетенции сохранены успешно"},
                    status=status.HTTP_201_CREATED
                )

            return Response(
                parse_errors_to_dict(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"message": f"Ошибка при создании компетенции: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

#######################
# Technology Views
#######################

class TechnologyDeleteView(BaseAPIView):
    """View for deleting technologies."""
    @swagger_auto_schema(
        operation_description="Удаление технологии по идентификатору",
        manual_parameters=[
            openapi.Parameter(
                'id',   
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор технологии"
            )
        ],
        responses={
            204: "Технология успешно удалена",  # Успешный ответ (без содержимого)
            400: "Идентификатор технологии не указан",  # Ошибка
            404: "Технология не найдена"  # Ошибка
        }
    )
    def delete(self, request):
        """
        Обработка DELETE-запроса для удаления технологии.
        """
        technology_id = request.query_params.get('id')  # Получаем параметр 'id' из query-строки

        if not technology_id:
            return Response(
                {"message": "Идентификатор технологии не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            technology = Technology.objects.get(id=technology_id)  # Ищем технологию по ID
        except Technology.DoesNotExist:
            return Response(
                {"message": "Технология с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        technology.delete()  # Удаляем технологию из базы данных

        return Response(
            {"message": "Технология успешно удалена"},
            status=status.HTTP_204_NO_CONTENT
        )

class TechnologyPutView(BaseAPIView):
    """View for updating technologies."""
    @swagger_auto_schema(
        operation_description="Обновление информации о технологии",
        request_body=TechnologySerializer,
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор технологии"
            )
        ],
        responses={
            200: "Информация о технологии обновлена успешно",
            400: "Ошибка валидации данных",
            404: "Технология не найдена"
        }
    )
    def put(self, request):
        """
        Обновление информации о технологии (обработка PUT-запроса).
        """
        technology_id = request.query_params.get('id')
        if not technology_id:
            return Response(
                {"message": "Идентификатор технологии не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            technology = Technology.objects.get(id=technology_id)
        except Technology.DoesNotExist:
            return Response(
                {"message": "Технология с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TechnologySerializer(technology, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(
                {"message": "Ошибка валидации данных", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновляем данные работодателя
        serializer.save()

        # Получаем обновленные данные
        updated_technology = OrderedDictQueryExecutor.fetchall(
            get_technologies, technology_id=technology_id
        )

        response_data = {
            "data": updated_technology,
            "message": "Информация о технологии обновлена успешно"
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class TechnologyGetView(BaseAPIView):
    """View for retrieving technologies."""
    @swagger_auto_schema(
        operation_description="Получение информации о технологиях. Если указан параметр 'id', возвращается конкретная технология. Если параметр 'id' не указан, возвращаются все технологии.",
        manual_parameters=[
            openapi.Parameter(
                'id',  # Имя параметра
                openapi.IN_QUERY,  # Параметр передается в query-строке
                type=openapi.TYPE_INTEGER,  # Тип параметра (целочисленный)
                required=False,  # Параметр не обязательный
                description="Идентификатор технологии (опционально)",  # Описание параметра
            )
        ],
        responses={
            200: "Информация о технологиях",  # Успешный ответ
            400: "Ошибка"  # Ошибка
        }
    )
    def get(self, request):
        """
        Обрабатывает GET-запрос для получения информации о технологиях.
        Если передан параметр 'id', возвращает данные о конкретной технологии.
        Если параметр 'id' не передан, возвращает данные обо всех технологиях.
        """
        technology_id = request.query_params.get('id')  # Получаем параметр 'id' из query-строки

        if technology_id:
            # Если передан 'id', получаем данные о конкретной технологии
            technologies = OrderedDictQueryExecutor.fetchall(
                get_technologies, technology_id=technology_id
            )
            if not technologies:
                # Если технология не найдена, возвращаем ошибку 404
                return Response(
                    {"message": "Технология с указанным ID не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )
            # Формируем успешный ответ с данными о технологии
            response_data = {
                "data": technologies,
                "message": "Технология получена успешно"
            }
        else:
            # Если 'id' не передан, получаем данные обо всех технологиях
            technologies = OrderedDictQueryExecutor.fetchall(get_technologies)
            # Формируем успешный ответ с данными обо всех технологиях
            response_data = {
                "data": technologies,
                "message": "Все технологии получены успешно"
            }

        # Возвращаем ответ с данными и статусом 200
        return Response(response_data, status=status.HTTP_200_OK)

class TechnologySendView(APIView):
    """
    Представление для создания одной или нескольких технологий.
    Поддерживает как одиночные объекты, так и массивы объектов.
    """
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких технологий",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,  # Указываем, что это массив
            items=openapi.Schema(  # Описываем элементы массива
                type=openapi.TYPE_OBJECT,
                properties={
                    'name': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Название технологии'
                    ),
                    'description': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Описание технологии'
                    ),
                    'popularity': openapi.Schema(
                        type=openapi.TYPE_NUMBER,
                        description='Популярность технологии (вещественное число)'
                    ),
                    'rating': openapi.Schema(
                        type=openapi.TYPE_NUMBER,
                        description='Рейтинг технологии (вещественное число)'
                    ),
                },
                required=['name', 'description', 'popularity', 'rating'],  # Обязательные поля
                example={
                    "name": "Python",
                    "description": "Python — это высокоуровневый язык программирования общего назначения, который широко используется для разработки веб-приложений, анализа данных, искусственного интеллекта и др.",
                    "popularity": 95.83,
                    "rating": 4.95
                }
            ),
        ),
        responses={
            201: openapi.Response(
                description="Технология/технологии успешно сохранены",
                examples={
                    "application/json": {
                        "message": "Технология/технологии сохранены успешно"
                    }
                }
            ),
            400: openapi.Response(
                description="Ошибка валидации",
                examples={
                    "application/json": {
                        "name": ["Это поле обязательно."],
                        "popularity": ["Это поле должно быть числом."]
                    }
                }
            )
        },
    )
    def post(self, request):
        """
        Обрабатывает POST-запрос для создания одной или нескольких технологий.
        Проверяет валидность данных и сохраняет технологии в базе данных.
        
        Пример запроса для одной технологии:
        {
            "name": "Python",
            "description": "Python — это высокоуровневый язык программирования общего назначения...",
            "popularity": 95.83,
            "rating": 4.95
        }

        Пример запроса для нескольких технологий:
        [
            {
                "name": "Python",
                "description": "Python — это высокоуровневый язык программирования общего назначения...",
                "popularity": 95.83,
                "rating": 4.95
            },
            {
                "name": "Django",
                "description": "Django — это мощный веб-фреймворк для Python...",
                "popularity": 90.12,
                "rating": 4.85
            }
        ]
        """
        data = request.data  # Получаем данные из запроса

        # Проверяем, является ли data списком
        if isinstance(data, list):
            # Если это список, обрабатываем каждый элемент
            serializer = TechnologySerializer(data=data, many=True)  # Указываем many=True для списка
        else:
            # Если это одиночный объект, обрабатываем его
            serializer = TechnologySerializer(data=data)

        if serializer.is_valid():
            # Если данные валидны, сохраняем технологии
            serializer.save()
            # Возвращаем успешный ответ
            return Response(
                {"message": "Технология/технологии сохранены успешно"},
                status=status.HTTP_201_CREATED
            )

        # Если данные не валидны, преобразуем ошибки в словарь и возвращаем ошибку 400
        errors = parse_errors_to_dict(serializer.errors)
        return Response(
            errors,
            status=status.HTTP_400_BAD_REQUEST
        )

