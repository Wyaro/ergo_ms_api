from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from src.core.utils.methods import parse_errors_to_dict
from src.core.utils.base.base_views import BaseAPIView
from src.core.utils.database.main import OrderedDictQueryExecutor
from drf_yasg.utils import swagger_auto_schema # type: ignore
from drf_yasg import openapi # type: ignore

from src.external.learning_analytics.data_formalization_submodule.models import(
    Speciality,
    Discipline,
    ACM,
    VCM,
    UCM  
)

from src.external.learning_analytics.data_formalization_submodule.serializers import(
    SpecialitySerializer,
    DisciplineSerializer,
    AcademicCompetenceMatrixSerializer,
    CompetencyProfileOfVacancySerializer,
    UserCompetenceMatrixSerializer
)

from src.external.learning_analytics.data_formalization_submodule.scripts import(
    get_specialities,
    get_disciplines,
    get_academicCompetenceMatrix,
    get_competencyProfileOfVacancy
)

# Представление данных для получения (GET) компетентностных профилях вакансий
class CompetencyProfileOfVacancyGetView(BaseAPIView):
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

# Представление данных для создания (POST) компетентностного профиля вакансии
class CompetencyProfileOfVacancySendView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Проверка ввода компетентностного профиля вакансий",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,  # Тип тела запроса (объект JSON)
            properties={
                'vacancy_name': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Наименование специальности'  # Описание поля
                ),
                'employer_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,  # Тип поля (строка)
                    description='ID работодателя'  # Описание поля
                ),
                'competencies_stack': openapi.Schema(
                    type=openapi.TYPE_OBJECT,  # Тип поля (строка)
                    description='Перечень компетенций'  # Описание поля
                ),
                'technology_stack': openapi.Schema(
                    type=openapi.TYPE_OBJECT,  # Тип поля (строка)
                    description='Перечень технологий'  # Описание поля
                ),
                'description': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Описание компетентностного профиля вакансии'  # Описание поля
                ),
            },
            required=['vacancy_name', 'employer_id', 'competencies_stack', 'technology_stack', 'description'],  # Обязательные поля
            example = {
                "vacancy_name": "Python Developer",
                "employer_id": 123,
                "competencies_stack": [
                    {
                        "id": 1,
                        "code": "ОПК-1",
                        "name": "Способность разрабатывать алгоритмы",
                        "description": "Умение разрабатывать и анализировать алгоритмы."
                    },
                    {
                        "id": 2,
                        "code": "ОПК-2",
                        "name": "Способность работать с базами данных",
                        "description": "Умение проектировать и использовать базы данных."
                    }
                ],
                "technology_stack": [
                    {
                        "id": 1,
                        "name": "Python",
                        "description": "Высокоуровневый язык программирования.",
                        "popularity": 95,
                        "rating": 5
                    },
                    {
                        "id": 2,
                        "name": "Django",
                        "description": "Фреймворк для веб-разработки на Python.",
                        "popularity": 85,
                        "rating": 4
                    },
                    {
                        "id": 3,
                        "name": "PostgreSQL",
                        "description": "Реляционная система управления базами данных.",
                        "popularity": 90,
                        "rating": 5
                    }
                ],
                "description": "Ищем опытного Python-разработчика с навыками работы с базами данных и веб-фреймворками."
            }
        ),
        responses={
            201: "Специальность успешно сохранена",  # Успешный ответ
            400: "Произошла ошибка"  # Ошибка
        },
    )
    def post(self, request):
        """
        Обрабатывает POST-запрос для создания нового компетентностного профиля вакансии.
        Проверяет валидность данных и сохраняет КПВ в базе данных.
        """
        serializer = CompetencyProfileOfVacancySerializer(data=request.data)  # Создаем сериализатор с данными из запроса

        if serializer.is_valid():
            # Если данные валидны, сохраняем специальность
            serializer.save()
            # Возвращаем успешный ответ
            successful_response = Response(
                {"message": "Компетентностный профиль вакансии сохранен успешно"},
                status=status.HTTP_200_OK
            )
            return successful_response

        # Если данные не валидны, преобразуем ошибки в словарь и возвращаем ошибку 400
        errors = parse_errors_to_dict(serializer.errors)
        return Response(
            errors,
            status=status.HTTP_400_BAD_REQUEST
        )

# Представление данных для обновления (PUT) компетентностного профиля вакансии
class CompetencyProfileOfVacancyPutView(BaseAPIView):
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

# Представление данных для удаления (DELETE) компетентностного профиля вакансии
class CompetencyProfileOfVacancyDeleteView(BaseAPIView):
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

        if not cp_id:
            return Response(
                {"message": "Идентификатор компетентностного профиля вакансии не указан"},
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

# Представление данных для получения (GET) специальностей
class SpecialityGetView(BaseAPIView):
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

# Представление данных для создания (POST) специальностей
class SpecialitySendView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Проверка ввода специальности",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,  # Тип тела запроса (объект JSON)
            properties={
                'code': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Код специальности'  # Описание поля
                ),
                'name': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Наименование специальности'  # Описание поля
                ),
                'specialization': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Специализация'  # Описание поля
                ),
                'department': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Кафедра'  # Описание поля
                ),
                'faculty': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Факультет'  # Описание поля
                ),
                'education_duration': openapi.Schema(
                    type=openapi.TYPE_INTEGER,  # Тип поля (целое число)
                    description='Срок получения образования (в месяцах)'  # Описание поля
                ),
                'year_of_admission': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (целое число)
                    description='Год поступления'  # Описание поля
                ),
            },
            required=['code', 'name', 'specialization', 'department', 'faculty', 'education_duration', 'year_of_admission'],  # Обязательные поля
            example={
                "code": "10.05.04",
                "name": "Информационно-аналитические системы безопасности",
                "specialization": "Автоматизация информационно-аналитической деятельности",
                "department": "Компьютерные технологии и системы",
                "faculty": "Факультет информационных технологий",
                "education_duration": 66,  # 5 лет и 6 месяцев = 66 месяцев
                "year_of_admission": "2021"
            }
        ),
        responses={
            201: "Специальность успешно сохранена",  # Успешный ответ
            400: "Произошла ошибка"  # Ошибка
        },
    )
    def post(self, request):
        """
        Обрабатывает POST-запрос для создания новой специальности.
        Проверяет валидность данных и сохраняет специальность в базе данных.
        """
        serializer = SpecialitySerializer(data=request.data)  # Создаем сериализатор с данными из запроса

        if serializer.is_valid():
            # Если данные валидны, сохраняем специальность
            serializer.save()
            # Возвращаем успешный ответ
            successful_response = Response(
                {"message": "Специальность сохранена успешно"},
                status=status.HTTP_200_OK
            )
            return successful_response

        # Если данные не валидны, преобразуем ошибки в словарь и возвращаем ошибку 400
        errors = parse_errors_to_dict(serializer.errors)
        return Response(
            errors,
            status=status.HTTP_400_BAD_REQUEST
        )

# Представление данных для обновления (PUT) специальностей
class SpecialityPutView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Обновление информации о специальности",
        request_body=SpecialitySerializer,
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор специальности"
            )
        ],
        responses={
            200: "Информация о специальности обновлена успешно",
            400: "Ошибка валидации данных",
            404: "Специальность не найдена"
        }
    )
    def put(self, request):
        """
        Обновление информации о специальности (обработка PUT-запроса).
        """
        speciality_id = request.query_params.get('id')
        if not speciality_id:
            return Response(
                {"message": "Идентификатор специальности не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            speciality = Speciality.objects.get(id=speciality_id)
        except Speciality.DoesNotExist:
            return Response(
                {"message": "Специальность с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SpecialitySerializer(speciality, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(
                {"message": "Ошибка валидации данных", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновляем данные специальности
        serializer.save()
    
        # Получаем обновленные данные
        updated_speciality = OrderedDictQueryExecutor.fetchall(
            get_speciality, speciality_id=speciality_id
        )

        response_data = {
            "data": updated_speciality,
            "message": "Информация о специальности обновлена успешно"
        }

        return Response(response_data, status=status.HTTP_200_OK)

# Представление данных для удаления (DELETE) специальностей
class SpecialityDeleteView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Удаление специальности по идентификатору",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор специальности"
            )
        ],
        responses={
            204: "Специальность успешно удалена",  # Успешный ответ (без содержимого)
            400: "Идентификатор специальности не указан",  # Ошибка
            404: "Специальность не найдена"  # Ошибка
        }
    )
    def delete(self, request):
        """
        Обработка DELETE-запроса для удаления специальности.
        """
        speciality_id = request.query_params.get('id')  # Получаем параметр 'id' из query-строки

        if not speciality_id:
            return Response(
                {"message": "Идентификатор специальности не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            speciality = Speciality.objects.get(id=speciality_id)  # Ищем специальность по ID
        except Speciality.DoesNotExist:
            return Response(
                {"message": "Специальность с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        speciality.delete()  # Удаляем специальность из базы данных

        return Response(
            {"message": "Специальность успешно удалена"},
            status=status.HTTP_204_NO_CONTENT
        )

# Представление данных для получения информации о дисциплинах
class DisciplineGetView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Получение информации о дисциплинах. Если указан параметр 'id', возвращается конкретная дисциплина. Если параметр 'id' не указан, возвращаются все существующие дисциплины.",
        manual_parameters=[
            openapi.Parameter(
                'id', # Имя параметра
                openapi.IN_QUERY, # Параметр передается в query-строке
                type = openapi.TYPE_INTEGER, # Тип параметра (целочисленынй)
                required=False,
                description="Идентификатор дисциплины (опционально)", # Описание параметра
            )
        ],
        responses={
            200: "Информация о дисциплинах", # Успешный ответ
            400: "Ошибка" # Ошибка
        }
    )
    def get(self, request):
        """
        Обработка GET-запроса для получения информации о дисциплинах.
        В случае передачи параметра 'id', возвращает данные о дисциплинах.
        Если параметр 'id' не передан - возвращаются все данные о дисциплинах.
        """

        discipline_id = request.query_params.get('id') # Полчаем параметр 'id' из query-строки

        if discipline_id:
            # Если передан 'id', получаем данные о конкретной дисциплине
            discipline = OrderedDictQueryExecutor.fetchall(
                get_disciplines, discipline_id = discipline_id
            )
            if not discipline:
                # Если дисциплина не обнаружена - возвращаем ошибку 404
                return Response(
                    {"message": "Дисциплина с указанным ID не найдена"},
                    status = status.HTTP_404_NOT_FOUND
                )
            response_data = {
                "data": discipline,
                "message": "Дисциплина получена успешно."
            }
        else:
            # Если 'id' не передан, получаем данные обо всех специальностях
            disciplines = OrderedDictQueryExecutor.fetchall(get_disciplines)
            # Формируем успешный ответ с данными обо всех специальностях
            response_data = {
                "data": disciplines,
                "message": "Все дисциплины получены успешно"
            }

        # Возвращаем ответ с данными и статусом 200
        return Response(response_data, status=status.HTTP_200_OK)

# Представление данных для создания (POST) дисциплины
class DisciplineSendView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Проверка ввода дисциплины",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, # Тип тела запроса (объект JSON)
            properties={
                'code': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Код специальности'  # Описание поля
                ),
                'name': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Наименование специальности'  # Описание поля
                ),
                'semesters': openapi.Schema(
                    type=openapi.TYPE_STRING, # Тип поля (строка)
                    description='Период освоения дисциплины (номера семестров через запятую)' # Описание поля
                ),
                'contact_work_hours': openapi.Schema(
                    type=openapi.TYPE_INTEGER, # Тип поля (целочисленный)
                    description='Продолжительность контактной работы, ч' # Описание поля
                ),
                'independent_work_hours': openapi.Schema(
                    type=openapi.TYPE_INTEGER, # Тип поля (целочисленный)
                    description='Продолжительность самостоятельной работы, ч' # Описание поля
                ),
                'controle_work_hours': openapi.Schema(
                    type=openapi.TYPE_INTEGER, # Тип поля (целочисленный)
                    description='Продолжительность контроля, ч' # Описание поля
                ),
                'competencies': openapi.Schema(
                    type=openapi.TYPE_OBJECT, # Тип поля (объект)
                    description='Перечень приобретаемых компетенций' # Описание поля
                ),
            },
            required=['code', 'name', 'semesters', 'contact_work_hours', 'independent_work_hours', 'controle_work_hours'], # Обязательные поля
            example={
                'code': 'Б1.О.45',
                'name': 'Формализованные модели и методы решения аналитических задач',
                'semesters': '7,8',
                'contact_work_hours': 192,
                'independent_work_hours': 60,
                'controle_work_hours': 36,
                'competencies': {
                    'code': 'ОПК-1.2',
                    'name': '. Способен оценивать роль информации, информационных технологий и информационной безопасности в современном обществе.'
                }
            }
        ),
            responses={
                201: "Дисциплина успешно сохранена", # Успешный ответ
                400: "Произошла ошибка" # Ошибка
            },
        )
    def post(self, request):
            """
            Обрабатывает POST-запрос для создания новой дисциплины.
            Проверяет валидность данных и сохраняет дисциплину в базе данных.
            """

            serializer = DisciplineSerializer(data=request.data) # Создаем сериализатор с данными из запроса

            if serializer.is_valid():
                # Если данные валидны, сохраняем дисциплину
                serializer.save()
                # Возвращаем успешным ответ
                successful_response = Response(
                    {"message": "Специальность сохранена успешно"},
                    status= status.HTTP_200_OK
                )
                return successful_response
            
            # Если данные не валидны, преобразуем ошибки в словарь и возвращаем ошибку 400
            errors = parse_errors_to_dict(serializer.errors)
            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST
            ) 

# Представление данных для обновления (PUT) дисциплины
class DisciplinePutView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Обновление информации о дисциплине",
        request_body=DisciplineSerializer,
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор дисциплины"
            )
        ],
        responses={
            200: "Информация о дисциплине обновлена успешно",
            400: "Ошибка валидации данных",
            404: "Дисциплина не найдена"
        }
    )
    def put(self, request):
        """
        Обновление информации о дисциплине (обработка PUT-запроса).
        """
        discipline_id = request.query_params.get('id')
        if not discipline_id:
            return Response(
                {"message": "Идентификатор дисциплины не указан"},
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
                {"message": "Ошибка валидации данных", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновляем данные специальности
        serializer.save()
    
        # Получаем обновленные данные
        updated_discipline = OrderedDictQueryExecutor.fetchall(
            get_discipline, discipline_id=discipline_id
        )

        response_data = {
            "data": updated_discipline,
            "message": "Информация о дисциплине обновлена успешно"
        }

        return Response(response_data, status=status.HTTP_200_OK)

# Представление данных для удаления (DELETE) дисциплины
class DisciplineDeleteView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Удаление дисциплины по идентификатору",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор дисциплины"
            )
        ],
        responses={
            204: "Специальность успешно удалена",  # Успешный ответ (без содержимого)
            400: "Идентификатор дисциплины не указан",  # Ошибка
            404: "Дисциплина не найдена"  # Ошибка
        }
    )
    def delete(self, request):
        """
        Обработка DELETE-запроса для удаления дисциплины.
        """
        discipline_id = request.query_params.get('id')  # Получаем параметр 'id' из query-строки

        if not discipline_id:
            return Response(
                {"message": "Идентификатор дисциплины не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            discipline = Discipline.objects.get(id=discipline_id)  # Ищем дисциплину по ID
        except Discipline.DoesNotExist:
            return Response(
                {"message": "Дисциплина с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        discipline.delete()  # Удаляем дисциплину из базы данных

        return Response(
            {"message": "Дисциплина успешно удалена"},
            status=status.HTTP_204_NO_CONTENT
        )

# Представление данных для получения информации об академических матрицах компетенций
class AcademicCompetenceMatrixGetView(BaseAPIView):
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

# Представление данных для создания (POST) матрицы академических компетенций
class AcademicCompetenceMatrixSendView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Проверка ввода матрицы академических компетенций",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, # Тип тела запроса (объект JSON)
            properties={
                'speciality_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,  # Тип поля (целочисленный)
                    description='Код специальности'  # Описание поля
                ),
                'discipline_list': openapi.Schema(
                    type=openapi.TYPE_OBJECT,  # Тип поля (объект)
                    description='Перечень изучаемых дисциплин'  # Описание поля
                ),
                'technology_stack': openapi.Schema(
                    type=openapi.TYPE_OBJECT, # Тип поля (строка)
                    description='Перечень изучаемых технологий в течение времени' # Описание поля
                ),                
            },
            required=['speciality_id', 'discipline_list', 'technology_stack'], # Обязательные поля
            example={
                'speciality_id': 1,
                'discipline_list': {
                    'code': 'Б1.О.45',
                    'name': 'Формализованные модели и методы решения аналитических задач',
                    'semesters': '7,8',
                    'contact_work_hours': 192,
                    'independent_work_hours': 60,
                    'controle_work_hours': 36,
                    'competencies': {
                        'code': 'ОПК-1.2',
                        'name': '. Способен оценивать роль информации, информационных технологий и информационной безопасности в современном обществе.'
                    }
                },
                'technology_stack': {
                    "name": "Python",
                    "description": "Python — это высокоуровневый язык программирования общего назначения, который широко используется для разработки веб-приложений, анализа данных, искусственного интеллекта и др.",
                    "popularity": 95,
                    "rating": 5
                }
            }
        ),
            responses={
                201: "Матрица академических компетенций успешно сохранена", # Успешный ответ
                400: "Произошла ошибка" # Ошибка
            },
        )
    def post(self, request):
            """
            Обрабатывает POST-запрос для создания новой матрицы академических компетенций.
            Проверяет валидность данных и сохраняет матрицы академических компетенций в базе данных.
            """

            serializer = AcademicCompetenceMatrixSerializer(data=request.data) # Создаем сериализатор с данными из запроса

            if serializer.is_valid():
                # Если данные валидны, сохраняем дисциплину
                serializer.save()
                # Возвращаем успешным ответ
                successful_response = Response(
                    {"message": "Матрица академических компетенций сохранена успешно"},
                    status= status.HTTP_200_OK
                )
                return successful_response
            
            # Если данные не валидны, преобразуем ошибки в словарь и возвращаем ошибку 400
            errors = parse_errors_to_dict(serializer.errors)
            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST
            ) 

# Представление данных для обновления (PUT) матрицы академических компетенций
class AcademicCompetenceMatrixPutView(BaseAPIView):
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

# Представление данных для удаления (DELETE) матрицы академических компетенций
class AcademicCompetenceMatrixDeleteView(BaseAPIView):
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



# Представление данных для получения информации об пользовательских матрицах компетенций
class UserCompetenceMatrixGetView(BaseAPIView):
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

# Представление данных для создания (POST) матрицы пользовательских компетенций
class UserCompetenceMatrixSendView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Проверка ввода матрицы пользовательских компетенций",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, # Тип тела запроса (объект JSON)
            properties={
                'user_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,  # Тип поля (целочисленный)
                    description='Код специальности'  # Описание поля
                ),
                'competencies_stack': openapi.Schema(
                    type=openapi.TYPE_OBJECT,  # Тип поля (объект)
                    description='Перечень изучаемых дисциплин'  # Описание поля
                ),
                'technology_stack': openapi.Schema(
                    type=openapi.TYPE_OBJECT, # Тип поля (строка)
                    description='Перечень изучаемых технологий в течение времени' # Описание поля
                ),                
            },
            required=['user_id', 'competencies_stack', 'technology_stack'], # Обязательные поля
            example={
                "code": "ПК-3.2",
                "name": "Разработка программного обеспечения",
                "description": "Способность разрабатывать компоненты программных комплексов и баз данных, использовать современные инструменты программирования."
                }
        ),
            responses={
                201: "Матрица пользовательских компетенций успешно сохранена", # Успешный ответ
                400: "Произошла ошибка" # Ошибка
            },
        )
    def post(self, request):
            """
            Обрабатывает POST-запрос для создания новой матрицы академических компетенций.
            Проверяет валидность данных и сохраняет матрицы академических компетенций в базе данных.
            """

            serializer = UserCompetenceMatrixSerializer(data=request.data) # Создаем сериализатор с данными из запроса

            if serializer.is_valid():
                # Если данные валидны, сохраняем дисциплину
                serializer.save()
                # Возвращаем успешным ответ
                successful_response = Response(
                    {"message": "Матрица пользовательских компетенций сохранена успешно"},
                    status= status.HTTP_200_OK
                )
                return successful_response
            
            # Если данные не валидны, преобразуем ошибки в словарь и возвращаем ошибку 400
            errors = parse_errors_to_dict(serializer.errors)
            return Response(
                errors,
                status=status.HTTP_400_BAD_REQUEST
            ) 

# Представление данных для обновления (PUT) матрицы пользовательских компетенций
class UserCompetenceMatrixPutView(BaseAPIView):
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

# Представление данных для удаления (DELETE) матрицы пользовательских компетенций
class UserCompetenceMatrixDeleteView(BaseAPIView):
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