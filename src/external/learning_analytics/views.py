from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from src.external.learning_analytics.models import (
    Technology,
    Competency,    # Исправлено с Competention
    Employer
)
from src.external.learning_analytics.serializers import (
    TechnologySerializer,
    CompetencySerializer,    # Исправлено с CompetentionSerializer
    EmployerSerializer
)
from src.core.utils.methods import parse_errors_to_dict
from src.core.utils.base.base_views import BaseAPIView
from src.external.learning_analytics.scripts import (
    get_technologies,
    get_competentions,
    get_employers
)

from src.external.learning_analytics.methods import (
    get_tables_info, 
    handle_db_errors,
    get_table_info,
    check_table_exists,
    clear_analytics_tables
)

from src.core.utils.database.main import OrderedDictQueryExecutor
from drf_yasg.utils import swagger_auto_schema # type: ignore
from drf_yasg import openapi # type: ignore
from django.db import connection
from django.core.cache import cache
from django.db.models import Count
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def handle_db_errors(func):
    """Декоратор для обработки ошибок БД"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper

# Представление данных для удаления (DELETE) работодателей
class EmployerDeleteView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Удаление работодателя по идентификатору",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор работодателя"
            )
        ],
        responses={
            204: "Работодатель успешно удален",  # Успешный ответ (без содержимого)
            400: "Идентификатор работодателя не указан",  # Ошибка
            404: "Работодатель не найден"  # Ошибка
        }
    )
    def delete(self, request):
        """
        Обработка DELETE-запроса для удаления работодателя.
        """
        employer_id = request.query_params.get('id')  # Получаем параметр 'id' из query-строки

        if not employer_id:
            return Response(
                {"message": "Идентификатор работодателя не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            employer = Employer.objects.get(id=employer_id)  # Ищем работодателя по ID
        except Employer.DoesNotExist:
            return Response(
                {"message": "Работодатель с указанным ID не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        employer.delete()  # Удаляем работодателя из базы данных

        return Response(
            {"message": "Работодатель успешно удален"},
            status=status.HTTP_204_NO_CONTENT
        )

# Представление данных для обновления (PUT) работодателей
class EmployerPutView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Обновление информации о работодателе",
        request_body=EmployerSerializer,
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор работодателя"
            )
        ],
        responses={
            200: "Информация о работодателе обновлена успешно",
            400: "Ошибка валидации данных",
            404: "Работодатель не найден"
        }
    )
    def put(self, request):
        """
        Обновление информации о работодателе (обработка PUT-запроса).
        """
        employer_id = request.query_params.get('id')
        if not employer_id:
            return Response(
                {"message": "Идентификатор работодателя не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            employer = Employer.objects.get(id=employer_id)
        except Employer.DoesNotExist:
            return Response(
                {"message": "Работодатель с указанным ID не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EmployerSerializer(employer, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(
                {"message": "Ошибка валидации данных", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновляем данные работодателя
        serializer.save()

        # Получаем обновленные данные
        updated_employer = OrderedDictQueryExecutor.fetchall(
            get_employers, employer_id=employer_id
        )

        response_data = {
            "data": updated_employer,
            "message": "Информация о работодателе обновлена успешно"
        }

        return Response(response_data, status=status.HTTP_200_OK)

# Представление данных для получения (GET) работодателей
class EmployerGetView(BaseAPIView):
    @swagger_auto_schema(
        operation_description="Получение информации о работодателях. Если указан параметр 'id', возвращается конкретный работодатель. Если параметр 'id' не указан, возвращаются все работодатели",
        manual_parameters=[
            openapi.Parameter(
                'id', # Имя параметра
                openapi.IN_QUERY, # Параметр передается в query-строке
                type = openapi.TYPE_INTEGER, # Тип параметра (целочисленный)
                required=False,
                description="Идентификатор работодателя (опционально)", # Описание параметра
            )
        ],
        responses={
            200: "Информация о работодателях", # Успешный ответ
            400: "Ошибка" # Ошибка
        }
    )
    def get(self, request):
        """
        Обработка GET-запроса для получения информации о работодателях
        В случае передачи параметра 'id', возвращает данные о конкретном работодателе.
        Если параметр 'id' не передан - возвращаются все данные о работодателях.
        """
        employer_id = request.query_params.get('id') # Получаем параметр 'id' из query-строки

        if employer_id:
            # Если передан 'id', получаем данные о конкретном работодателе
            employer = OrderedDictQueryExecutor.fetchall(
                get_employers, employer_id = employer_id
            )
            if not employer:
                # Если работодатель не обнаружена - возвращаем ошибку 404
                return Response(
                    {"message": "Работодатель с указанным ID не найден"},
                    status = status.HTTP_404_NOT_FOUND
                )
            # Формируем успешный ответ с данными о работодателе
            response_data = {
                "data": employer,
                "message": "Компетенция получена успешно"
            }
        else:
            # Если 'id' не передан, получаем данные обо всех технологиях
            employers = OrderedDictQueryExecutor.fetchall(get_employers)
            # Формируем успешный ответ с данными обо всех технологиях
            response_data = {
                "data": employers,
                "message": "Все работодатели получены успешно"
            }

        # Возвращаем ответ с данными и статусом 200
        return Response(response_data, status=status.HTTP_200_OK)
    
# Представление данных для создания (POST) работодателей
class EmployerSendView(APIView):
    @swagger_auto_schema(
        operation_description="Создание нового работодателя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,  # Тип тела запроса (объект JSON)
            properties={
                'company_name': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Название компании',  # Описание поля
                ),
                'description': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Описание компании',  # Описание поля
                ),
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    format=openapi.FORMAT_EMAIL,  # Указываем формат email
                    description='Контактный email компании',  # Описание поля
                ),
                'rating': openapi.Schema(
                    type=openapi.TYPE_NUMBER,  # Тип поля (число)
                    format=openapi.FORMAT_DECIMAL,  # Указываем формат числа с плавающей точкой
                    description='Рейтинг компании от 0 до 5',  # Описание поля
                ),
            },
            required=['company_name', 'description', 'email', 'rating'],  # Обязательные поля
            example={
                "company_name": "Tech Innovations Inc.",
                "description": "Компания, специализирующаяся на разработке инновационных технологий в области искусственного интеллекта и машинного обучения.",
                "email": "info@techinnovations.com",
                "rating": 4.75
            }
        ),
        responses={
            201: "Работодатель успешно создан",  # Успешный ответ
            400: "Произошла ошибка"  # Ошибка
        },
    )
    def post(self, request):
        """
        Обрабатывает POST-запрос для создания нового работодателя.
        Проверяет валидность данных и сохраняет работодателя в базе данных.
        """
        serializer = EmployerSerializer(data=request.data)  # Создаем сериализатор с данными из запроса

        if serializer.is_valid():
            # Если данные валидны, сохраняем работодателя
            serializer.save()
            # Возвращаем успешный ответ
            return Response(
                {"message": "Работодатель успешно создан"},
                status=status.HTTP_201_CREATED
            )

        # Если данные не валидны, возвращаем ошибку 400
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

# Представление данных для удаления (DELETE) компетенций
class CompetencyDeleteView(BaseAPIView):    # Исправлено с CompetentionDeleteView
    @swagger_auto_schema(
        operation_description="Удаление компетенции по идентификатору",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор компетенции"
            )
        ],
        responses={
            204: "Компетенция успешно удален",  # Успешный ответ (без содержимого)
            400: "Идентификатор компетенции не указан",  # Ошибка
            404: "Компетенция не найдена"  # Ошибка
        }
    )
    def delete(self, request):
        """
        Обработка DELETE-запроса для удаления компетенции.
        """
        competention_id = request.query_params.get('id')  # Получаем параметр 'id' из query-строки

        if not competention_id:
            return Response(
                {"message": "Идентификатор компетенции не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            competention = Competency.objects.get(id=competention_id)  # Исправлено
        except Competency.DoesNotExist:    # Исправлено
            return Response(
                {"message": "Компетенция с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        competention.delete()  # Удаляем компетенцию из базы данных

        return Response(
            {"message": "Компетенция успешно удалена"},
            status=status.HTTP_204_NO_CONTENT
        )

# Представление данных для обновления (PUT) компетенций
class CompetencyPutView(BaseAPIView):    # Исправлено с CompetentionPutView
    @swagger_auto_schema(
        operation_description="Обновление информации о компетенции",
        request_body=CompetencySerializer,    # Исправлено
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Идентификатор компетенции"
            )
        ],
        responses={
            200: "Информация о компетенции обновлена успешно",
            400: "Ошибка валидации данных",
            404: "Компетенция не найдена"
        }
    )
    def put(self, request):
        """
        Обновление информации о компетенции (обработка PUT-запроса).
        """
        competention_id = request.query_params.get('id')
        if not competention_id:
            return Response(
                {"message": "Идентификатор компетенции не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            competency = Competency.objects.get(id=competention_id)    # Исправлено
        except Competency.DoesNotExist:    # Исправлено
            return Response(
                {"message": "Компетенция с указанным ID не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompetencySerializer(competency, data=request.data, partial=False)    # Исправлено
        if not serializer.is_valid():
            return Response(
                {"message": "Ошибка валидации данных", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновляем данные работодателя
        serializer.save()

        # Получаем обновленные данные
        updated_competention = OrderedDictQueryExecutor.fetchall(
            get_competentions, competention_id=competention_id
        )

        response_data = {
            "data": updated_competention,
            "message": "Информация о компетенции обновлена успешно"
        }

        return Response(response_data, status=status.HTTP_200_OK)

# Представление данных для получения (GET) компетенций
class CompetencyGetView(BaseAPIView):    # Исправлено с CompetentionGetView
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
        В случае передачи параметра 'id', возвращает данные о конкретной компетенциях.
        Если параметр 'id' не передан - возвращаются все данные о компетенциях.
        """
        competency_id = request.query_params.get('id') # Получаем параметр 'id' из query-строки

        if competency_id:
            # Если передан 'id', получаем данные о конкретной технологии
            competention = OrderedDictQueryExecutor.fetchall(
                get_competentions, competency_id = competency_id
            )
            if not competention:
                # Если компетенция не обнаружена - возвращаем ошибку 404
                return Response(
                    {"message": "Компетенция с указанным ID не найдена"},
                    status = status.HTTP_404_NOT_FOUND
                )
            # Формируем успешный ответ с данными о технологии
            response_data = {
                "data": competentions,
                "message": "Компетенция получена успешно"
            }
        else:
            # Если 'id' не передан, получаем данные обо всех технологиях
            competentions = OrderedDictQueryExecutor.fetchall(get_competentions)
            # Формируем успешный ответ с данными обо всех технологиях
            response_data = {
                "data": competentions,
                "message": "Все компетенции получены успешно"
            }

        # Возвращаем ответ с данными и статусом 200
        return Response(response_data, status=status.HTTP_200_OK)

# Представление данных для создания (POST) компетенций
class CompetencySendView(BaseAPIView):    # Исправлено с CompetentionSendView
    @swagger_auto_schema(
        operation_description="Проверка ввода компетенции",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,  # Тип тела запроса (объект JSON)
            properties={
                'code': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (целое число)
                    description='Код'  # Описание поля
                ),
                'name': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Наименование'  # Описание поля
                ),
                'description': openapi.Schema(
                    type=openapi.TYPE_STRING,  # Тип поля (строка)
                    description='Описание'  # Описание поля
                ),
                'know_level': openapi.Schema(type=openapi.TYPE_STRING, description='Уровень знаний'),
                'can_level': openapi.Schema(type=openapi.TYPE_STRING, description='Уровень умений'),
                'master_level': openapi.Schema(type=openapi.TYPE_STRING, description='Уровень владения'),
                'blooms_level': openapi.Schema(type=openapi.TYPE_STRING, description='Уровень по таксономии Блума', enum=['KNOW', 'UNDERSTAND', 'APPLY', 'ANALYZE', 'EVALUATE', 'CREATE']),
                'blooms_verbs': openapi.Schema(type=openapi.TYPE_STRING, description='Глаголы действий'),
                'complexity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Сложность компетенции (1-10)'),
                'demand': openapi.Schema(type=openapi.TYPE_INTEGER, description='Востребованность компетенции (1-10)')
            },
            required=['code', 'name', 'description', 'know_level', 'can_level', 'master_level', 'blooms_level', 'complexity', 'demand'],
            example={
                "code": "ОПК-8",
                "name": "Способен применять методы научных исследований...",
                "description": "В этом случае компетенции соответствуют умения...",
                "know_level": "Знает методы научных исследований...",
                "can_level": "Умеет применять методы...",
                "master_level": "Владеет навыками применения...",
                "blooms_level": "APPLY",
                "blooms_verbs": "применять, использовать, демонстрировать",
                "complexity": 7,
                "demand": 8
            }
        ),
        responses={
            201: openapi.Response(description="Компетенция успешно создана"),
            400: openapi.Response(description="Ошибка валидации данных")
        }
    )
    def post(self, request):
        """
        Обрабатывает POST-запрос для создания новой компетенции.
        Проверяет валидность данных и сохраняет компетенцию в базе данных.
        """
        serializer = CompetencySerializer(data=request.data)    # Исправлено

        if serializer.is_valid():
            # Если данные валидны, сохраняем технологию
            serializer.save()
            # Возвращаем успешный ответ
            successful_response = Response(
                {"message": "Компетенция сохранена успешно"},
                status=status.HTTP_200_OK
            )
            return successful_response

        # Если данные не валидны, преобразуем ошибки в словарь и возвращаем ошибку 400
        errors = parse_errors_to_dict(serializer.errors)
        return Response(
            errors,
            status=status.HTTP_400_BAD_REQUEST
        ) 

#Представление данных для удаления (DELETE) технологий
class TechnologyDeleteView(BaseAPIView):
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

# Представление данных для обновления (PUT) технологий
class TechnologyPutView(BaseAPIView):
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
    
# Представление данных для получения (GET) технологий 
class TechnologyGetView(BaseAPIView):
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

# Представление данных для создания (POST) технологий
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
            example=[  # Пример массива объектов
                {
                    "name": "Python",
                    "description": "Python — это высокоуровневый язык программирования общего назначения, который широко используется для разработки веб-приложений, анализа данных, искусственного интеллекта и др.",
                    "popularity": 95.83,
                    "rating": 4.95
                },
                {
                    "name": "Django",
                    "description": "Django — это мощный веб-фреймворк для Python, который позволяет быстро создавать безопасные и масштабируемые веб-приложения.",
                    "popularity": 90.12,
                    "rating": 4.85
                }
            ]
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


class DatabaseTablesView(APIView):
    CACHE_TIMEOUT = 60 * 5  # 5 минут

    @swagger_auto_schema(
        operation_description="Получение списка таблиц базы данных или данных конкретной таблицы",
        manual_parameters=[
            openapi.Parameter(
                'table',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="Имя таблицы (опционально)"
            )
        ],
        responses={
            200: "Успешное получение данных",
            400: "Неверное имя таблицы",
            500: "Ошибка базы данных"
        }
    )
    @handle_db_errors
    def get(self, request):
        table_name = request.query_params.get('table')

        if table_name:
            cache_key = f'table_data_{table_name}'
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)

        try:
            with connection.cursor() as cursor:
                if table_name:
                    if not check_table_exists(cursor, table_name):
                        return Response(
                            {'error': 'Table not found'},
                            status=status.HTTP_404_NOT_FOUND
                        )

                    columns_info = get_table_info(cursor, table_name)
                    
                    cursor.execute(f'SELECT * FROM "{table_name}"')
                    rows = cursor.fetchall()
                    
                    columns = [
                        {
                            'name': col[0],
                            'type': col[1],
                            'nullable': col[2] == 'YES'
                        } for col in columns_info
                    ]
                    
                    formatted_rows = [
                        dict(zip([col['name'] for col in columns], row))
                        for row in rows
                    ]

                    response_data = {
                        'table_name': table_name,
                        'columns': columns,
                        'rows': formatted_rows
                    }
                    cache.set(cache_key, response_data, self.CACHE_TIMEOUT)
                    return Response(response_data)
                else:
                    tables_data = get_tables_info(cursor)
                    return Response({'tables': tables_data})
        except Exception as e:
            logger.error(f"Error fetching table data: {str(e)}")
            raise

class ClearTablesView(APIView):
    @swagger_auto_schema(
        operation_description="Очистка всех таблиц аналитического модуля",
        responses={
            200: "Таблицы успешно очищены",
            500: "Ошибка при очистке таблиц"
        }
    )
    @handle_db_errors
    def post(self, request):
        try:
            with connection.cursor() as cursor:
                clear_analytics_tables(cursor)
                return Response({
                    'message': 'Все таблицы успешно очищены'
                }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error clearing tables: {str(e)}")
            raise


