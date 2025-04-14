# Импорт необходимых классов и модулей из Django REST Framework
from rest_framework.serializers import (
    ModelSerializer,            # Базовый класс для создания сериализаторов на основе моделей
    CharField,                  # Поле для строковых данных
    BooleanField,               # Поле для булевых значений
    ValidationError,            # Класс для обработки ошибок валидации
    Serializer                  # Базовый класс для создания кастомных сериализаторов
)

# Импорт модели Technology из приложения learning_analytics
from src.external.learning_analytics.data_formalization_submodule.models import (
    Technology,                 # Модель технологии
    Competency,                 # Модель компетенции
    Speciality,                 # Модель специальностией
    Discipline,                 # Модель дисциплины
    ACM,                        # Модель матрицы академических компетенций
    VCM,                        # Модель компетентностного профиля вакансии
    UCM,                        # Модель матрицы пользовательских компетенций
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

# Создание сериализатора для модели Speciality
class SpecialitySerializer(ModelSerializer):
    class Meta:
        # Указываем модель, с которой работает сериализатор
        model = Speciality
        # Указываем поля модели, которые будут сериализованы/десериализованы
        fields = ['code', 'name', 'specialization', 'department', 'faculty', 'education_duration', 'year_of_admission']

        # Метод для создания нового объекта Speciality
        def create(self, validated_data):
            """
            Создаёт новый объект Speciality на основе валидированных данных

            :param validated_data: Данные, прошедшие валидацию
            :return: Созданный объект Speciality
            """
            speciality = Speciality.objects.create(
                code=validated_data['code'],                             # Устанавливаем код специальности
                name=validated_data['name'],                             # Устанавливаем наименование специальности
                specialization=validated_data['specialization'],         # Устанавливаем специализацию специальности
                department=validated_data['department'],                 # Устанавливаем кафедру специальности
                faculty=validated_data['faculty'],                       # Устанавливаем факультет специальности
                education_duration=validated_data['education_duration'], # Устанавливаем продолжительность обучения по специальности
                year_of_admission=validated_data['year_of_admission'],   # Устанавливаем год поступления на специальность
            )

            return speciality # Возвращаем созданный объект

# Создание сериализатора для модели Discipline
class DisciplineSerializer(ModelSerializer):
    class Meta:
        # Указываем модель, с которой работает сериализатор
        model = Discipline
        # Указываем поля модели, которые будут сериализованы/десериализованы
        fields = ['code', 'name', 'semesters', 'contact_work_hours', 'independent_work_hours', 'control_work_hours', 'competencies']

        # Метод для создания нового объекта Speciality
        def create(self, validated_data):
            """
            Создаёт новый объект Discipline на основе валидированных данных

            :param validated_data: Данные, прошедшие валидацию
            :return: Созданный объект Discipline
            """
            discipline = Discipline.objects.create(
                code=validated_data['code'],                                        # Устанавливаем код дисциплины
                name=validated_data['name'],                                        # Устанавливаем наименование дисциплины
                semesters=validated_data['semesters'],                              # Устанавливаем период освоения дисциплины
                contact_work_hours=validated_data['contact_work_hours'],            # Устанавливаем продолжительность контактной работы
                independent_work_hours=validated_data['independent_work_hours'],    # Устанавливаем продолжительность самостоятельной работы
                control_work_hours=validated_data['control_work_hours'],          # Устанавливаем продолжительность контроля
                competencies=validated_data['competencies'],                        # Устанавливаем перечень осваиваемых компетенций
            )

            return discipline # Возвращаем созданный объект

# Создание сериализатора для модели AcademicCompetenceMatrix
class AcademicCompetenceMatrixSerializer(ModelSerializer):
    class Meta:
        # Указываем модель, с которой работает сериализатор
        model = ACM
        # Указываем поля модели, которые будут сериализованы/десериализованы
        fields = ['speciality_id', 'discipline_list', 'technology_stack']

        # Метод для создания нового объекта Speciality
        def create(self, validated_data):
            """
            Создаёт новый объект Discipline на основе валидированных данных

            :param validated_data: Данные, прошедшие валидацию
            :return: Созданный объект Discipline
            """

            AcademicCompetenceMatrix = AcademicCompetenceMatrix.objects.create(
                speciality_id=validated_data['speciality_id'],                      # Устанавливаем id специальности, для которой формируется матрица академических компетенций
                discipline_list=validated_data['discipline_list'],                  # Устанавливаем перечень осваиваемых дисциплин
                technology_stack=validated_data['technology_stack'],                # Устанавливаем перечень приобретаемых технологий
            )

            return AcademicCompetenceMatrix # Возвращаем созданный объект

# Создание сериализатора для модели CompetencyProfileOfVacancy
class CompetencyProfileOfVacancySerializer(ModelSerializer):
    class Meta:
        # Указываем модель, с которой будет работать сериализатор
        model = VCM
        # Указываем поля модели, которые будут серилаизованы/десериализованы
        fields = ['vacancy_name', 'employer_id', 'competencies_stack', 'technology_stack', 'description']

        # Метод для создания нового объекта CompetencyProfileOfVacancy
        def create(self, validated_data):
            """
            Создает новый объект CompetencyProfileOfVacancy на основе валидированных данных

            :param validated_data: Данные, прошедшие валидацию
            :return: Созданный объект CompetencyProfileOfVacancy
            """

            CompetencyProfileOfVacancy = CompetencyProfileOfVacancy.objects.create(
                vacancy_name = validated_data['vacancy_name'],
                employer_id = validated_data['employer_id'],
                competencies_stack = validated_data['competencies_stack'],
                technology_stack = validated_data['technology_stack'],
                description = validated_data['description'],
            )

            return CompetencyProfileOfVacancy # Возвращаем созданный объект

# Создание сериализатора для модели UserCompetenceMatrix
class UserCompetenceMatrixSerializer(ModelSerializer):
    class Meta:
        # Указываем модель, с которой будет работать сериализатор
        model = UCM
        # Указываем поля модели, которые будут сериализованы/десериализованы
        fields = ['user_id', 'competencies_stack', 'technology_stack']

        # Метод для создания нового объекта UserCompetenceMatrix
        def create(self, validated_data):
            """
            Создает новый объект UserCompetenceMatrix на основе валидированных данных

            :param validated_data: Данные, прошедшие валидацию
            :return: Созданный объект UserCompetenceMatrix
            """
            user_competence_matrix = UCM.objects.create(
                user_id=validated_data['user_id'],                      # Устанавливаем id пользователя
                competencies_stack=validated_data['competencies_stack'], # Устанавливаем стек компетенций пользователя
                technology_stack=validated_data['technology_stack'],     # Устанавливаем стек технологий пользователя    # Устанавливаем ссылки на портфолио
            )

            return user_competence_matrix # Возвращаем созданный объект

