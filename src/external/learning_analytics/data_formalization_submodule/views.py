"""
Этот модуль содержит представления (views) для работы с данными в рамках модуля формализации данных.
- Специальности (Speciality)
- Учебные планы (Curriculum)
- Технологии (Technology)
- Компетенции (Competency)
- Базовые дисциплины (BaseDiscipline)
- Дисциплины (Discipline)
- Вакансии (Vacancy)
- Матрицы академических компетенций (ACM)
- Профили компетенций вакансии (VCM)
- Матрицы компетенций пользователя (UCM)
"""

# --- Импорты стандартных, сторонних и локальных библиотек ---
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema # type: ignore
from drf_yasg import openapi # type: ignore 

from src.core.utils.methods import parse_errors_to_dict
from src.core.utils.base.base_views import BaseAPIView
from src.core.utils.database.main import OrderedDictQueryExecutor

# --- Импорт моделей и сериализаторов ---
from src.external.learning_analytics.data_formalization_submodule.models import(
    Speciality,
    Curriculum, 
    Technology,
    Competency,
    BaseDiscipline,
    Discipline,
    Vacancy, 
    ACM,
    VCM,
    UCM
)

from src.external.learning_analytics.data_formalization_submodule.serializers import(
    SpecialitySerializer,
    CurriculumSerializer,
    TechnologySerializer,
    CompetencySerializer,
    BaseDisciplineSerializer,
    DisciplineSerializer, 
    VacancySerializer,
    ACMSerializer,
    VCMSerializer,
    UCMSerializer
)

# --- Импорт скриптов для работы с БД ---
from src.external.learning_analytics.data_formalization_submodule.scripts import(
    get_specialities,
    get_curriculum,
    get_technologies,
    get_competentions,
    get_base_disciplines,
    get_disciplines,
    get_vacancies,
    get_academicCompetenceMatrix,
    get_competencyProfileOfVacancy,
    get_userCompetenceMatrix
)

#######################
# Specialty Views 
#######################

class SpecialityGetView(BaseAPIView):
    """
    Представление для получения информации о специальностях.
    Позволяет получить либо все специальности, либо одну по id (через query-параметр).
    """
    @swagger_auto_schema(
        operation_description="Получение информации о направлениях подготовки. Если указан параметр 'id', возвращается конкретное направление. Если параметр 'id' не указан, возвращаются все направления",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Идентификатор направления подготовки (опционально)",
            )
        ],
        responses={
            200: "Информация о направлениях подготовки",
            400: "Ошибка"
        }
    )
    def get(self, request):
        """
        Обработка GET-запроса для получения информации о направлениях подготовки.
        Если передан параметр 'id', возвращается конкретная специальность.
        Если параметр не передан — возвращаются все специальности.
        """
        speciality_id = request.query_params.get('id')
        if speciality_id:
            # Получение специальности по id
            speciality = OrderedDictQueryExecutor.fetchall(
                get_specialities, speciality_id=speciality_id
            )
            if not speciality:
                # Если не найдено — возвращаем 404
                return Response(
                    {"message": "Направление подготовки (специальность) с указанным ID не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )
            response_data = {
                "data": speciality,
                "message": "Специальность получена успешно"
            }
        else:
            # Получение всех специальностей
            specialities = OrderedDictQueryExecutor.fetchall(get_specialities)
            response_data = {
                "data": specialities,
                "message": "Все специальности получены успешно"
            }
        return Response(response_data, status=status.HTTP_200_OK)


class SpecialitySendView(BaseAPIView):
    """
    Представление для создания одной или нескольких специальностей.
    Поддерживает как одиночные объекты, так и массивы объектов.
    """
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких специальностей",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'code': openapi.Schema(type=openapi.TYPE_STRING, description='Код специальности (например, 10.05.04)'),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='Наименование'),
                    'specialization': openapi.Schema(type=openapi.TYPE_STRING, description='Специализация'),
                    'department': openapi.Schema(type=openapi.TYPE_STRING, description='Кафедра'),
                    'faculty': openapi.Schema(type=openapi.TYPE_STRING, description='Факультет')
                },
                required=['code', 'name', 'specialization', 'department', 'faculty'],
                example={
                    "code": "09.03.01",
                    "name": "Информатика и вычислительная техника",
                    "specialization": "Программное обеспечение",
                    "department": "Кафедра информатики",
                    "faculty": "Факультет информационных технологий"
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
        Обработка POST-запроса для создания специальностей.
        Добавляет только те объекты, которых нет в БД (по code), дубликаты пропускает.
        Возвращает списки добавленных и пропущенных.
        """
        try:
            data = request.data
            is_many = isinstance(data, list)
            if not is_many:
                data = [data]
            # Получаем все существующие code из БД
            existing_codes = set(Speciality.objects.filter(code__in=[item.get('code') for item in data]).values_list('code', flat=True))
            to_create = [item for item in data if item.get('code') not in existing_codes]
            skipped = [item for item in data if item.get('code') in existing_codes]
            if not to_create:
                return Response({
                    "added": [],
                    "skipped": skipped,
                    "message": "Все объекты уже существуют в базе, ничего не добавлено"
                }, status=status.HTTP_200_OK)
            serializer = SpecialitySerializer(data=to_create, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "added": serializer.data,
                    "skipped": skipped,
                    "message": f"Добавлено: {len(serializer.data)}, пропущено (дубликаты): {len(skipped)}"
                }, status=status.HTTP_201_CREATED)
            errors = serializer.errors
            if isinstance(errors, list):
                errors = {str(i): err for i, err in enumerate(errors)}
            return Response(parse_errors_to_dict(errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Ошибка при создании специальности: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class SpecialityPutView(BaseAPIView):
    """
    Представление для обновления информации о специальности.
    Ожидает идентификатор специальности в url и новые данные в теле запроса.
    """
    @swagger_auto_schema(
        operation_description="Обновление информации о специальности",
        request_body=SpecialitySerializer,
        responses={
            200: "Информация о специальности обновлена успешно",
            400: "Ошибка валидации данных",
            404: "Специальность не найдена"
        }
    )
    def put(self, request, pk: int):
        """
        Обработка PUT-запроса для обновления специальности.
        """
        try:
            speciality_id = int(pk)
        except (TypeError, ValueError):
            # Если id некорректный — возвращаем ошибку
            return Response(
                {"message":"Неверный формат идентификатора специальности"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем объект или возвращаем 404
        speciality = get_object_or_404(Speciality, id=speciality_id)
        serializer = SpecialitySerializer(speciality, data=request.data, partial=False)
        if not serializer.is_valid():
            # Если данные невалидны — возвращаем ошибки
            return Response(
                {
                    "message":"Ошибка валидации данных",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(
            {
                "data": serializer.data,
                "message": "Информация о специальности обновлена успешно"
            },
            status=status.HTTP_200_OK
        )


class SpecialityDeleteView(BaseAPIView):
    """
    Представление для удаления специальности по идентификатору.
    """
    @swagger_auto_schema(
        operation_description="Удаление специальности по идентификатору",
        responses={
            204: "Специальность успешно удалена",  # Успешный ответ (без содержимого)
            400: "Идентификатор специальности не указан",  # Ошибка
            404: "Специальность не найдена"  # Ошибка
        }
    )
    def delete(self, request, pk: int):
        """
        Обработка DELETE-запроса для удаления специальности.
        """
        # Пытаемся найти специальность по id
        speciality = Speciality.objects.filter(id=pk).first()
        if not speciality:
            # Если не найдено — возвращаем 404
            return Response(
                {
                    "message": "Специальность не найдена"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        # Удаляем объект
        speciality.delete()
        return Response(
            {
                "message": "Специальность успешно удалена"
            },
            status=status.HTTP_204_NO_CONTENT
        )

#######################
# Curriculum Views
#######################

class CurriculumGetView(BaseAPIView):
    """
    Получение учебных планов (одного или всех).
    """
    @swagger_auto_schema(
        operation_description="Получение информации об учебных планах. Если указан параметр 'id', возвращается конкретный учебный план.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Идентификатор учебного плана (опционально)",
            )
        ],
        responses={200: CurriculumSerializer(many=True), 400: "Ошибка"}
    )
    def get(self, request):
        curriculum_id = request.query_params.get('id')
        if curriculum_id:
            curriculum = OrderedDictQueryExecutor.fetchall(
                get_curriculum, curriculum_id=curriculum_id
            )
            if not curriculum:
                return Response(
                    {"message": "Учебный план с указанным ID не найден"},
                    status=status.HTTP_404_NOT_FOUND
                )
            response_data = {"data": curriculum, "message": "Учебный план получен успешно"}
        else:
            curriculums = OrderedDictQueryExecutor.fetchall(get_curriculum)
            response_data = {"data": curriculums, "message": "Все учебные планы получены успешно"}
        return Response(response_data, status=status.HTTP_200_OK)

class CurriculumSendView(BaseAPIView):
    """
    Создание одного или нескольких учебных планов.
    """
    @swagger_auto_schema(
        operation_description="Создание одного или нескольких учебных планов",
        request_body=CurriculumSerializer(many=True),
        responses={201: CurriculumSerializer(many=True), 400: "Ошибка валидации данных"},
    )
    def post(self, request):
        try:
            data = request.data
            is_many = isinstance(data, list)
            serializer = CurriculumSerializer(data=data, many=is_many)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "Учебный(е) план(ы) сохранены успешно"},
                    status=status.HTTP_201_CREATED
                )
            return Response(parse_errors_to_dict(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Ошибка при создании учебного плана: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class CurriculumPutView(BaseAPIView):
    """
    Обновление учебного плана.
    """
    @swagger_auto_schema(
        operation_description="Обновление информации об учебном плане",
        request_body=CurriculumSerializer,
        responses={200: CurriculumSerializer, 400: "Ошибка валидации данных", 404: "Учебный план не найден"}
    )
    def put(self, request, pk: int):
        try:
            curriculum_id = int(pk)
        except (TypeError, ValueError):
            return Response({"message": "Неверный формат идентификатора учебного плана"}, status=status.HTTP_400_BAD_REQUEST)
        curriculum = get_object_or_404(Curriculum, id=curriculum_id)
        serializer = CurriculumSerializer(curriculum, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response({"message": "Ошибка валидации данных", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"data": serializer.data, "message": "Информация об учебном плане обновлена успешно"}, status=status.HTTP_200_OK)

class CurriculumDeleteView(BaseAPIView):
    """
    Удаление учебного плана.
    """
    @swagger_auto_schema(
        operation_description="Удаление учебного плана по идентификатору",
        responses={204: openapi.Response(description="Учебный план успешно удален"), 400: "Идентификатор не указан", 404: "Учебный план не найден"}
    )
    def delete(self, request, pk: int):
        curriculum = Curriculum.objects.filter(id=pk).first()
        if not curriculum:
            return Response({"message": "Учебный план не найден"}, status=status.HTTP_404_NOT_FOUND)
        curriculum.delete()
        return Response({"message": "Учебный план успешно удален"}, status=status.HTTP_204_NO_CONTENT)

#######################
# Technology Views
#######################

class TechnologyGetView(BaseAPIView):
    """
    Получение технологий (одной или всех).
    """
    @swagger_auto_schema(
        operation_description="Получение информации о технологиях. Если указан параметр 'id', возвращается конкретная технология.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Идентификатор технологии (опционально)",
            )
        ],
        responses={200: TechnologySerializer(many=True), 400: "Ошибка"}
    )
    def get(self, request):
        technology_id = request.query_params.get('id')
        if technology_id:
            technology = OrderedDictQueryExecutor.fetchall(
                get_technologies, technology_id=technology_id
            )
            if not technology:
                return Response(
                    {"message": "Технология с указанным ID не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )
            response_data = {"data": technology, "message": "Технология получена успешно"}
        else:
            technologies = OrderedDictQueryExecutor.fetchall(get_technologies)
            response_data = {"data": technologies, "message": "Все технологии получены успешно"}
        return Response(response_data, status=status.HTTP_200_OK)

class TechnologySendView(BaseAPIView):
    """
    Создание одной или нескольких технологий.
    """
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких технологий",
        request_body=TechnologySerializer(many=True),
        responses={201: TechnologySerializer(many=True), 400: "Ошибка валидации данных"},
    )
    def post(self, request):
        try:
            data = request.data
            is_many = isinstance(data, list)
            serializer = TechnologySerializer(data=data, many=is_many)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "Технология(и) сохранены успешно"},
                    status=status.HTTP_201_CREATED
                )
            return Response(parse_errors_to_dict(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Ошибка при создании технологии: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class TechnologyPutView(BaseAPIView):
    """
    Обновление технологии.
    """
    @swagger_auto_schema(
        operation_description="Обновление информации о технологии",
        request_body=TechnologySerializer,
        responses={200: TechnologySerializer, 400: "Ошибка валидации данных", 404: "Технология не найдена"}
    )
    def put(self, request, pk: int):
        try:
            technology_id = int(pk)
        except (TypeError, ValueError):
            return Response({"message": "Неверный формат идентификатора технологии"}, status=status.HTTP_400_BAD_REQUEST)
        technology = get_object_or_404(Technology, id=technology_id)
        serializer = TechnologySerializer(technology, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response({"message": "Ошибка валидации данных", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"data": serializer.data, "message": "Информация о технологии обновлена успешно"}, status=status.HTTP_200_OK)

class TechnologyDeleteView(BaseAPIView):
    """
    Удаление технологии.
    """
    @swagger_auto_schema(
        operation_description="Удаление технологии по идентификатору",
        responses={204: openapi.Response(description="Технология успешно удалена"), 400: "Идентификатор не указан", 404: "Технология не найдена"}
    )
    def delete(self, request, pk: int):
        technology = Technology.objects.filter(id=pk).first()
        if not technology:
            return Response({"message": "Технология не найдена"}, status=status.HTTP_404_NOT_FOUND)
        technology.delete()
        return Response({"message": "Технология успешно удалена"}, status=status.HTTP_204_NO_CONTENT)

#######################
# Competency Views
#######################

class CompetencyGetView(BaseAPIView):
    """
    Получение компетенций (одной или всех).
    """
    @swagger_auto_schema(
        operation_description="Получение информации о компетенциях. Если указан параметр 'id', возвращается конкретная компетенция.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Идентификатор компетенции (опционально)",
            )
        ],
        responses={200: CompetencySerializer(many=True), 400: "Ошибка"}
    )
    def get(self, request):
        competency_id = request.query_params.get('id')
        if competency_id:
            competency = OrderedDictQueryExecutor.fetchall(
                get_competentions, competency_id=competency_id
            )
            if not competency:
                return Response(
                    {"message": "Компетенция с указанным ID не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )
            response_data = {"data": competency, "message": "Компетенция получена успешно"}
        else:
            competencies = OrderedDictQueryExecutor.fetchall(get_competentions)
            response_data = {"data": competencies, "message": "Все компетенции получены успешно"}
        return Response(response_data, status=status.HTTP_200_OK)

class CompetencySendView(BaseAPIView):
    """
    Создание одной или нескольких компетенций.
    """
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких компетенций",
        request_body=CompetencySerializer(many=True),
        responses={201: CompetencySerializer(many=True), 400: "Ошибка валидации данных"},
    )
    def post(self, request):
        try:
            data = request.data
            is_many = isinstance(data, list)
            serializer = CompetencySerializer(data=data, many=is_many)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "Компетенция(и) сохранены успешно"},
                    status=status.HTTP_201_CREATED
                )
            return Response(parse_errors_to_dict(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Ошибка при создании компетенции: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class CompetencyPutView(BaseAPIView):
    """
    Обновление компетенции.
    """
    @swagger_auto_schema(
        operation_description="Обновление информации о компетенции",
        request_body=CompetencySerializer,
        responses={200: CompetencySerializer, 400: "Ошибка валидации данных", 404: "Компетенция не найдена"}
    )
    def put(self, request, pk: int):
        try:
            competency_id = int(pk)
        except (TypeError, ValueError):
            return Response({"message": "Неверный формат идентификатора компетенции"}, status=status.HTTP_400_BAD_REQUEST)
        competency = get_object_or_404(Competency, id=competency_id)
        serializer = CompetencySerializer(competency, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response({"message": "Ошибка валидации данных", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"data": serializer.data, "message": "Информация о компетенции обновлена успешно"}, status=status.HTTP_200_OK)

class CompetencyDeleteView(BaseAPIView):
    """
    Удаление компетенции.
    """
    @swagger_auto_schema(
        operation_description="Удаление компетенции по идентификатору",
        responses={204: openapi.Response(description="Компетенция успешно удалена"), 400: "Идентификатор не указан", 404: "Компетенция не найдена"}
    )
    def delete(self, request, pk: int):
        competency = Competency.objects.filter(id=pk).first()
        if not competency:
            return Response({"message": "Компетенция не найдена"}, status=status.HTTP_404_NOT_FOUND)
        competency.delete()
        return Response({"message": "Компетенция успешно удалена"}, status=status.HTTP_204_NO_CONTENT)

#######################
# BaseDiscipline Views
#######################

class BaseDisciplineGetView(BaseAPIView):
    """
    Получение базовых дисциплин (одной или всех).
    """
    @swagger_auto_schema(
        operation_description="Получение информации о базовых дисциплинах. Если указан параметр 'id', возвращается конкретная дисциплина.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Идентификатор базовой дисциплины (опционально)",
            )
        ],
        responses={200: BaseDisciplineSerializer(many=True), 400: "Ошибка"}
    )
    def get(self, request):
        base_discipline_id = request.query_params.get('id')
        if base_discipline_id:
            base_discipline = OrderedDictQueryExecutor.fetchall(
                get_base_disciplines, base_discipline_id=base_discipline_id
            )
            if not base_discipline:
                return Response(
                    {"message": "Базовая дисциплина с указанным ID не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )
            response_data = {"data": base_discipline, "message": "Базовая дисциплина получена успешно"}
        else:
            base_disciplines = OrderedDictQueryExecutor.fetchall(get_base_disciplines)
            response_data = {"data": base_disciplines, "message": "Все базовые дисциплины получены успешно"}
        return Response(response_data, status=status.HTTP_200_OK)

class BaseDisciplineSendView(BaseAPIView):
    """
    Создание одной или нескольких базовых дисциплин.
    """
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких базовых дисциплин",
        request_body=BaseDisciplineSerializer(many=True),
        responses={201: BaseDisciplineSerializer(many=True), 400: "Ошибка валидации данных"},
    )
    def post(self, request):
        try:
            data = request.data
            is_many = isinstance(data, list)
            serializer = BaseDisciplineSerializer(data=data, many=is_many)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "Базовая дисциплина(ы) сохранены успешно"},
                    status=status.HTTP_201_CREATED
                )
            return Response(parse_errors_to_dict(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Ошибка при создании базовой дисциплины: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class BaseDisciplinePutView(BaseAPIView):
    """
    Обновление базовой дисциплины.
    """
    @swagger_auto_schema(
        operation_description="Обновление информации о базовой дисциплине",
        request_body=BaseDisciplineSerializer,
        responses={200: BaseDisciplineSerializer, 400: "Ошибка валидации данных", 404: "Базовая дисциплина не найдена"}
    )
    def put(self, request, pk: int):
        try:
            base_discipline_id = int(pk)
        except (TypeError, ValueError):
            return Response({"message": "Неверный формат идентификатора базовой дисциплины"}, status=status.HTTP_400_BAD_REQUEST)
        base_discipline = get_object_or_404(BaseDiscipline, id=base_discipline_id)
        serializer = BaseDisciplineSerializer(base_discipline, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response({"message": "Ошибка валидации данных", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"data": serializer.data, "message": "Информация о базовой дисциплине обновлена успешно"}, status=status.HTTP_200_OK)

class BaseDisciplineDeleteView(BaseAPIView):
    """
    Удаление базовой дисциплины.
    """
    @swagger_auto_schema(
        operation_description="Удаление базовой дисциплины по идентификатору",
        responses={204: openapi.Response(description="Базовая дисциплина успешно удалена"), 400: "Идентификатор не указан", 404: "Базовая дисциплина не найдена"}
    )
    def delete(self, request, pk: int):
        base_discipline = BaseDiscipline.objects.filter(id=pk).first()
        if not base_discipline:
            return Response({"message": "Базовая дисциплина не найдена"}, status=status.HTTP_404_NOT_FOUND)
        base_discipline.delete()
        return Response({"message": "Базовая дисциплина успешно удалена"}, status=status.HTTP_204_NO_CONTENT)

#######################
# Discipline Views
#######################

class DisciplineGetView(BaseAPIView):
    """
    Получение дисциплин (одной или всех).
    """
    @swagger_auto_schema(
        operation_description="Получение информации о дисциплинах. Если указан параметр 'id', возвращается конкретная дисциплина.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Идентификатор дисциплины (опционально)",
            )
        ],
        responses={200: DisciplineSerializer(many=True), 400: "Ошибка"}
    )
    def get(self, request):
        discipline_id = request.query_params.get('id')
        if discipline_id:
            discipline = OrderedDictQueryExecutor.fetchall(
                get_disciplines, discipline_id=discipline_id
            )
            if not discipline:
                return Response(
                    {"message": "Дисциплина с указанным ID не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )
            response_data = {"data": discipline, "message": "Дисциплина получена успешно"}
        else:
            disciplines = OrderedDictQueryExecutor.fetchall(get_disciplines)
            response_data = {"data": disciplines, "message": "Все дисциплины получены успешно"}
        return Response(response_data, status=status.HTTP_200_OK)

class DisciplineSendView(BaseAPIView):
    """
    Создание одной или нескольких дисциплин.
    """
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких дисциплин",
        request_body=DisciplineSerializer(many=True),
        responses={201: DisciplineSerializer(many=True), 400: "Ошибка валидации данных"},
    )
    def post(self, request):
        try:
            data = request.data
            is_many = isinstance(data, list)
            serializer = DisciplineSerializer(data=data, many=is_many)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "Дисциплина(ы) сохранены успешно"},
                    status=status.HTTP_201_CREATED
                )
            return Response(parse_errors_to_dict(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Ошибка при создании дисциплины: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class DisciplinePutView(BaseAPIView):
    """
    Обновление дисциплины.
    """
    @swagger_auto_schema(
        operation_description="Обновление информации о дисциплине",
        request_body=DisciplineSerializer,
        responses={200: DisciplineSerializer, 400: "Ошибка валидации данных", 404: "Дисциплина не найдена"}
    )
    def put(self, request, pk: int):
        try:
            discipline_id = int(pk)
        except (TypeError, ValueError):
            return Response({"message": "Неверный формат идентификатора дисциплины"}, status=status.HTTP_400_BAD_REQUEST)
        discipline = get_object_or_404(Discipline, id=discipline_id)
        serializer = DisciplineSerializer(discipline, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response({"message": "Ошибка валидации данных", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"data": serializer.data, "message": "Информация о дисциплине обновлена успешно"}, status=status.HTTP_200_OK)

class DisciplineDeleteView(BaseAPIView):
    """
    Удаление дисциплины.
    """
    @swagger_auto_schema(
        operation_description="Удаление дисциплины по идентификатору",
        responses={204: openapi.Response(description="Дисциплина успешно удалена"), 400: "Идентификатор не указан", 404: "Дисциплина не найдена"}
    )
    def delete(self, request, pk: int):
        discipline = Discipline.objects.filter(id=pk).first()
        if not discipline:
            return Response({"message": "Дисциплина не найдена"}, status=status.HTTP_404_NOT_FOUND)
        discipline.delete()
        return Response({"message": "Дисциплина успешно удалена"}, status=status.HTTP_204_NO_CONTENT)

#######################
# Vacancy Views
#######################

class VacancyGetView(BaseAPIView):
    """
    Получение вакансий (одной или всех).
    """
    @swagger_auto_schema(
        operation_description="Получение информации о вакансиях. Если указан параметр 'id', возвращается конкретная вакансия.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Идентификатор вакансии (опционально)",
            )
        ],
        responses={200: VacancySerializer(many=True), 400: "Ошибка"}
    )
    def get(self, request):
        vacancy_id = request.query_params.get('id')
        if vacancy_id:
            vacancy = OrderedDictQueryExecutor.fetchall(
                get_vacancies, vacancy_id=vacancy_id
            )
            if not vacancy:
                return Response(
                    {"message": "Вакансия с указанным ID не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )
            response_data = {"data": vacancy, "message": "Вакансия получена успешно"}
        else:
            vacancies = OrderedDictQueryExecutor.fetchall(get_vacancies)
            response_data = {"data": vacancies, "message": "Все вакансии получены успешно"}
        return Response(response_data, status=status.HTTP_200_OK)

class VacancySendView(BaseAPIView):
    """
    Создание одной или нескольких вакансий.
    """
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких вакансий",
        request_body=VacancySerializer(many=True),
        responses={201: VacancySerializer(many=True), 400: "Ошибка валидации данных"},
    )
    def post(self, request):
        try:
            data = request.data
            is_many = isinstance(data, list)
            serializer = VacancySerializer(data=data, many=is_many)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "Вакансия(и) сохранены успешно"},
                    status=status.HTTP_201_CREATED
                )
            return Response(parse_errors_to_dict(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Ошибка при создании вакансии: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class VacancyPutView(BaseAPIView):
    """
    Обновление вакансии.
    """
    @swagger_auto_schema(
        operation_description="Обновление информации о вакансии",
        request_body=VacancySerializer,
        responses={200: VacancySerializer, 400: "Ошибка валидации данных", 404: "Вакансия не найдена"}
    )
    def put(self, request, pk: int):
        try:
            vacancy_id = int(pk)
        except (TypeError, ValueError):
            return Response({"message": "Неверный формат идентификатора вакансии"}, status=status.HTTP_400_BAD_REQUEST)
        vacancy = get_object_or_404(Vacancy, id=vacancy_id)
        serializer = VacancySerializer(vacancy, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response({"message": "Ошибка валидации данных", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"data": serializer.data, "message": "Информация о вакансии обновлена успешно"}, status=status.HTTP_200_OK)

class VacancyDeleteView(BaseAPIView):
    """
    Удаление вакансии.
    """
    @swagger_auto_schema(
        operation_description="Удаление вакансии по идентификатору",
        responses={204: openapi.Response(description="Вакансия успешно удалена"), 400: "Идентификатор не указан", 404: "Вакансия не найдена"}
    )
    def delete(self, request, pk: int):
        vacancy = Vacancy.objects.filter(id=pk).first()
        if not vacancy:
            return Response({"message": "Вакансия не найдена"}, status=status.HTTP_404_NOT_FOUND)
        vacancy.delete()
        return Response({"message": "Вакансия успешно удалена"}, status=status.HTTP_204_NO_CONTENT)

#######################
# ACM Views
#######################

class ACMGetView(BaseAPIView):
    """
    Получение матриц академических компетенций (одной или всех).
    """
    @swagger_auto_schema(
        operation_description="Получение информации о матрицах академических компетенций. Если указан параметр 'id', возвращается конкретная матрица.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Идентификатор матрицы (опционально)",
            )
        ],
        responses={200: ACMSerializer(many=True), 400: "Ошибка"}
    )
    def get(self, request):
        matrix_id = request.query_params.get('id')
        if matrix_id:
            matrix = OrderedDictQueryExecutor.fetchall(
                get_academicCompetenceMatrix, matrix_id=matrix_id
            )
            if not matrix:
                return Response(
                    {"message": "Матрица с указанным ID не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )
            response_data = {"data": matrix, "message": "Матрица получена успешно"}
        else:
            matrices = OrderedDictQueryExecutor.fetchall(get_academicCompetenceMatrix)
            response_data = {"data": matrices, "message": "Все матрицы получены успешно"}
        return Response(response_data, status=status.HTTP_200_OK)

class ACMSendView(BaseAPIView):
    """
    Создание одной или нескольких матриц академических компетенций.
    """
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких матриц академических компетенций",
        request_body=ACMSerializer(many=True),
        responses={201: ACMSerializer(many=True), 400: "Ошибка валидации данных"},
    )
    def post(self, request):
        try:
            data = request.data
            is_many = isinstance(data, list)
            serializer = ACMSerializer(data=data, many=is_many)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "Матрица(ы) сохранены успешно"},
                    status=status.HTTP_201_CREATED
                )
            return Response(parse_errors_to_dict(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Ошибка при создании матрицы: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class ACMPutView(BaseAPIView):
    """
    Обновление матрицы академических компетенций.
    """
    @swagger_auto_schema(
        operation_description="Обновление информации о матрице академических компетенций",
        request_body=ACMSerializer,
        responses={200: ACMSerializer, 400: "Ошибка валидации данных", 404: "Матрица не найдена"}
    )
    def put(self, request, pk: int):
        try:
            matrix_id = int(pk)
        except (TypeError, ValueError):
            return Response({"message": "Неверный формат идентификатора матрицы"}, status=status.HTTP_400_BAD_REQUEST)
        matrix = get_object_or_404(ACM, id=matrix_id)
        serializer = ACMSerializer(matrix, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response({"message": "Ошибка валидации данных", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"data": serializer.data, "message": "Информация о матрице обновлена успешно"}, status=status.HTTP_200_OK)

class ACMDeleteView(BaseAPIView):
    """
    Удаление матрицы академических компетенций.
    """
    @swagger_auto_schema(
        operation_description="Удаление матрицы по идентификатору",
        responses={204: openapi.Response(description="Матрица успешно удалена"), 400: "Идентификатор не указан", 404: "Матрица не найдена"}
    )
    def delete(self, request, pk: int):
        matrix = ACM.objects.filter(id=pk).first()
        if not matrix:
            return Response({"message": "Матрица не найдена"}, status=status.HTTP_404_NOT_FOUND)
        matrix.delete()
        return Response({"message": "Матрица успешно удалена"}, status=status.HTTP_204_NO_CONTENT)

#######################
# VCM Views
#######################

class VCMGetView(BaseAPIView):
    """
    Получение профилей компетенций вакансии (одного или всех).
    """
    @swagger_auto_schema(
        operation_description="Получение информации о профилях компетенций вакансии. Если указан параметр 'id', возвращается конкретный профиль.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Идентификатор профиля (опционально)",
            )
        ],
        responses={200: VCMSerializer(many=True), 400: "Ошибка"}
    )
    def get(self, request):
        cp_id = request.query_params.get('id')
        if cp_id:
            vcm = OrderedDictQueryExecutor.fetchall(
                get_competencyProfileOfVacancy, cp_id=cp_id
            )
            if not vcm:
                return Response(
                    {"message": "Профиль с указанным ID не найден"},
                    status=status.HTTP_404_NOT_FOUND
                )
            response_data = {"data": vcm, "message": "Профиль получен успешно"}
        else:
            vcms = OrderedDictQueryExecutor.fetchall(get_competencyProfileOfVacancy)
            response_data = {"data": vcms, "message": "Все профили получены успешно"}
        return Response(response_data, status=status.HTTP_200_OK)

class VCMSendView(BaseAPIView):
    """
    Создание одного или нескольких профилей компетенций вакансии.
    """
    @swagger_auto_schema(
        operation_description="Создание одного или нескольких профилей компетенций вакансии",
        request_body=VCMSerializer(many=True),
        responses={201: VCMSerializer(many=True), 400: "Ошибка валидации данных"},
    )
    def post(self, request):
        try:
            data = request.data
            is_many = isinstance(data, list)
            serializer = VCMSerializer(data=data, many=is_many)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "Профиль(и) сохранены успешно"},
                    status=status.HTTP_201_CREATED
                )
            return Response(parse_errors_to_dict(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Ошибка при создании профиля: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class VCMPutView(BaseAPIView):
    """
    Обновление профиля компетенций вакансии.
    """
    @swagger_auto_schema(
        operation_description="Обновление информации о профиле компетенций вакансии",
        request_body=VCMSerializer,
        responses={200: VCMSerializer, 400: "Ошибка валидации данных", 404: "Профиль не найден"}
    )
    def put(self, request, pk: int):
        try:
            vcm_id = int(pk)
        except (TypeError, ValueError):
            return Response({"message": "Неверный формат идентификатора профиля"}, status=status.HTTP_400_BAD_REQUEST)
        vcm = get_object_or_404(VCM, id=vcm_id)
        serializer = VCMSerializer(vcm, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response({"message": "Ошибка валидации данных", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"data": serializer.data, "message": "Информация о профиле обновлена успешно"}, status=status.HTTP_200_OK)

class VCMDeleteView(BaseAPIView):
    """
    Удаление профиля компетенций вакансии.
    """
    @swagger_auto_schema(
        operation_description="Удаление профиля по идентификатору",
        responses={204: openapi.Response(description="Профиль успешно удален"), 400: "Идентификатор не указан", 404: "Профиль не найден"}
    )
    def delete(self, request, pk: int):
        vcm = VCM.objects.filter(id=pk).first()
        if not vcm:
            return Response({"message": "Профиль не найден"}, status=status.HTTP_404_NOT_FOUND)
        vcm.delete()
        return Response({"message": "Профиль успешно удален"}, status=status.HTTP_204_NO_CONTENT)

#######################
# UCM Views
#######################

class UCMGetView(BaseAPIView):
    """
    Получение матриц компетенций пользователя (одной или всех).
    """
    @swagger_auto_schema(
        operation_description="Получение информации о матрицах компетенций пользователя. Если указан параметр 'id', возвращается конкретная матрица.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Идентификатор матрицы (опционально)",
            )
        ],
        responses={200: UCMSerializer(many=True), 400: "Ошибка"}
    )
    def get(self, request):
        matrix_id = request.query_params.get('id')
        if matrix_id:
            matrix = OrderedDictQueryExecutor.fetchall(
                get_userCompetenceMatrix, matrix_id=matrix_id
            )
            if not matrix:
                return Response(
                    {"message": "Матрица с указанным ID не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )
            response_data = {"data": matrix, "message": "Матрица получена успешно"}
        else:
            matrices = OrderedDictQueryExecutor.fetchall(get_userCompetenceMatrix)
            response_data = {"data": matrices, "message": "Все матрицы получены успешно"}
        return Response(response_data, status=status.HTTP_200_OK)

class UCMSendView(BaseAPIView):
    """
    Создание одной или нескольких матриц компетенций пользователя.
    """
    @swagger_auto_schema(
        operation_description="Создание одной или нескольких матриц компетенций пользователя",
        request_body=UCMSerializer(many=True),
        responses={201: UCMSerializer(many=True), 400: "Ошибка валидации данных"},
    )
    def post(self, request):
        try:
            data = request.data
            is_many = isinstance(data, list)
            serializer = UCMSerializer(data=data, many=is_many)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "Матрица(ы) сохранены успешно"},
                    status=status.HTTP_201_CREATED
                )
            return Response(parse_errors_to_dict(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Ошибка при создании матрицы: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class UCMPutView(BaseAPIView):
    """
    Обновление матрицы компетенций пользователя.
    """
    @swagger_auto_schema(
        operation_description="Обновление информации о матрице компетенций пользователя",
        request_body=UCMSerializer,
        responses={200: UCMSerializer, 400: "Ошибка валидации данных", 404: "Матрица не найдена"}
    )
    def put(self, request, pk: int):
        try:
            matrix_id = int(pk)
        except (TypeError, ValueError):
            return Response({"message": "Неверный формат идентификатора матрицы"}, status=status.HTTP_400_BAD_REQUEST)
        matrix = get_object_or_404(UCM, id=matrix_id)
        serializer = UCMSerializer(matrix, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response({"message": "Ошибка валидации данных", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"data": serializer.data, "message": "Информация о матрице обновлена успешно"}, status=status.HTTP_200_OK)

class UCMDeleteView(BaseAPIView):
    """
    Удаление матрицы компетенций пользователя.
    """
    @swagger_auto_schema(
        operation_description="Удаление матрицы по идентификатору",
        responses={204: openapi.Response(description="Матрица успешно удалена"), 400: "Идентификатор не указан", 404: "Матрица не найдена"}
    )
    def delete(self, request, pk: int):
        matrix = UCM.objects.filter(id=pk).first()
        if not matrix:
            return Response({"message": "Матрица не найдена"}, status=status.HTTP_404_NOT_FOUND)
        matrix.delete()
        return Response({"message": "Матрица успешно удалена"}, status=status.HTTP_204_NO_CONTENT)




