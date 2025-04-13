# Импорт необходимых классов и модулей из Django REST Framework
from rest_framework.serializers import (
    ModelSerializer,  # Базовый класс для создания сериализаторов на основе моделей
    CharField,       # Поле для строковых данных
    BooleanField,    # Поле для булевых значений
    ValidationError, # Класс для обработки ошибок валидации
    Serializer       # Базовый класс для создания кастомных сериализаторов
)

# Импорт необходимых моделей
from src.external.learning_analytics.models import (
    Technology,     # Модель технологии
    Competency,     # Исправленное имя модели
    Employer        # Модель работодателя
)

# Создание сериализатора для модели Technology
class TechnologySerializer(ModelSerializer):
    class Meta:
        # Указываем модель, с которой работает сериализатор
        model = Technology
        # Указываем поля модели, которые будут сериализованы/десериализованы
        fields = ['name', 'description', 'popularity', 'rating']

        # Метод для создания нового объекта Technology
        def create(self, validated_data):
            """
            Создает новый объект Technology на основе валидированных данных.
            
            :param validated_data: Данные, прошедшие валидацию
            :return: Созданный объект Technology
            """
            technology = Technology.objects.create(
                name=validated_data['name'],          # Устанавливаем имя технологии
                description=validated_data['description'],  # Устанавливаем описание
                popularity=validated_data['popularity'],  # Устанавливаем популярность
                rating=validated_data['rating'],      # Устанавливаем рейтинг
            )
            return technology  # Возвращаем созданный объект

# Создание сериализатора для модели Competency
class CompetencySerializer(ModelSerializer):
    class Meta:
        # Указываем модель, с которой работает сериализатор
        model = Competency
        # Указываем поля модели, которые будут сериализованы/десериализованы
        fields = [
            'code', 'name', 'description',
            'know_level', 'can_level', 'master_level',
            'blooms_level', 'blooms_verbs',
            'complexity', 'demand'
        ]

    def create(self, validated_data):
        """
        Создает новый объект Competency на основе валидированных данных.

        :param validated_data: Данные, прошедшие валидацию
        :return: Созданный объект Competency
        """ 
        return Competency.objects.create(**validated_data)

# Создание сериализатора для модели Employer
class EmployerSerializer(ModelSerializer):
    class Meta:
        model = Employer
        fields = ['id', 'company_name', 'description', 'email', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']  # Указываем, что эти поля только для чтения

    def create(self, validated_data):
        """
        Создает новый объект Employer на основе валидированных данных.
        """
        employer = Employer.objects.create(
            company_name=validated_data['company_name'],
            description=validated_data['description'],
            email=validated_data['email'],
            rating=validated_data['rating']
        )
        return employer

    def validate_rating(self, value):
        """
        Проверяет, что рейтинг находится в диапазоне от 1 до 5.
        """
        if value < 0 or value > 5:
            raise Serializer.ValidationError("Рейтинг должен быть от 1 до 5.")
        return value