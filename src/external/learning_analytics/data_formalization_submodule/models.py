from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from src.external.learning_analytics.models import (
    Employer
)

# Модель Technology представляет ту или иную технологию, осваиваемую в процессе изучения дисциплин.
class Technology(models.Model):
    """
    Модель Technology представляет ту или иную технологию, осваиваемую в процессе изучения дисциплин.

    Attributes:
        name (CharField): Название технологии. Максимальная длина — 60 символов.
        description (TextField): Описание технологии. Максимальная длина — 400 символов.
        popularity (DecimalField): Уровень популярности технологии от 0 до 100, %.
        rating (DecimalField): Рейтинг технологии от 0 до 5.
    """
    name = models.CharField(max_length=60)
    description = models.TextField(max_length=400)
    popularity = models.DecimalField(max_digits=4, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.description}"

    class Meta:
        verbose_name = "Технология"
        verbose_name_plural = "Технологии"

# Модель Competency представляет компетенции 
class Competency(models.Model):
    """
    Модель Competency представляет компетенции.

    Attributes:
        code (CharField): Уникальный код компетенции. Максимальная длина — 10 символов.
        name (CharField): Название компетенции. Максимальная длина — 200 символов.
        description (TextField): Описание компетенции. Максимальная длина — 400 символов.
        know_level (TextField): Уровень освоения компетенции по метрике "Знать".
        can_level (TextField): Уровень освоения компетенции по метрике "Уметь".
        master_level (TextField): Уровень освоения компетенции по метрике "Владеть".
        blooms_level (CharField): Уровень по таксономии Блума.
        blooms_verbs (CharField): Глаголы действий для оценки уровня.
        complexity (PositiveIntegerField): Сложность компетенции (1-10).
        demand (PositiveIntegerField): Востребованность компетенции (1-10).
    """
    BLOOMS_LEVELS = [
        ('KNOW', 'Знание'),
        ('UNDERSTAND', 'Понимание'),
        ('APPLY', 'Применение'),
        ('ANALYZE', 'Анализ'),
        ('EVALUATE', 'Синтез'),
        ('CREATE', 'Оценка'),
    ]


    code = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=400)

    # Уровни освоения компетенции
    know_level = models.TextField(verbose_name="Знать", help_text="Теоретические знания")
    can_level = models.TextField(verbose_name="Уметь", help_text="Практические навыки")
    master_level = models.TextField(verbose_name="Владеть", help_text="Способность к выполнению задач")

    # Таксономия Блума
    blooms_level = models.CharField(
        choices=BLOOMS_LEVELS,
        default='KNOW',
        verbose_name="Уровень таксономии Блума"
    )
    blooms_verbs = models.CharField(
        max_length=255,
        verbose_name="Глаголы для оценки таксономии Блума",
        help_text="Через запятую: анализировать, оценивать, создавать и т.д."
    )
    
    complexity = models.PositiveIntegerField(
        verbose_name="Сложность",
        help_text="Сложность компетенции от 1 до 10",
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    demand = models.PositiveIntegerField(
        verbose_name="Востребованность",
        help_text="Востребованность компетенции от 1 до 10",
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    class Meta:
        verbose_name = "Компетенция"
        verbose_name_plural = "Компетенции"


    def __str__(self):
        return f"{self.code} ({self.name})"
        
# Модель специальности
class Speciality(models.Model):
    """
    Модель Speciality представляет собой информацию о специальности (направлении подготовки).

    Attributes:
        code (CharField): Код специальности. Максимальная длина — 20 символов.
        name (CharField): Наименование специальности. Максимальная длина — 255 символов.
        specialization (CharField): Наименование специализации. Максимальная длина - 255 символов.
        department (CharField): Кафедра, выпускающая специальность. Максимальная длина - 255 символов.
        faculty (CharField): Факультет. Максимальная длина - 255 символов.
        education_duration (SmallAutoField): Срок получения образования. Подразумевается измерение в количестве месяцев. 
        year_of_admission (CharField): Год поступления (для учета различий в УП)
    """
    code = models.CharField(max_length=20, unique=True, verbose_name="Код специальности")
    name = models.CharField(max_length=255, verbose_name="Специальность")
    specialization = models.CharField(max_length=255, verbose_name="Специализация")
    department = models.CharField(max_length=255, verbose_name="Кафедра")
    faculty = models.CharField(max_length=255, verbose_name="Факультет")
    education_duration = models.PositiveSmallIntegerField(verbose_name="Срок получения образования")
    year_of_admission = models.CharField(max_length=4, verbose_name="Год поступления")

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"

# Модель дисциплины
class Discipline(models.Model):
    """
    Модель Discipline представляет собой информацию о дисциплине.
    
    Attributes:
        code (CharField): Код дисциплины. Максимальна длина - 10 символов.
        name (CharField): Наименование дисциплины. Максимальная длина - 255 символов.
        semesters (CharField): Период освоения дисциплины (номера семестров через ','). Максимальная длина - 12 символов.
        contact_work_hours (SmallAutoField): Длительность контактной работы, часы. 
        independent_work_hours (SmallAutoField): Длительность самостоятельной работы, часы.
        control_work_hours (SmallAutoField): Длительность контроля, часы
        competencies (JSONField): Перечень осваиваемых компетенций
    """
    code = models.CharField(max_length=10, unique=True, verbose_name="Код дисциплины")
    name = models.CharField(max_length=255, verbose_name="Наименование")
    # Подразумевается максимум 6 семестров
    semesters = models.CharField(max_length=12, verbose_name="Период освоения (семестры)")
    contact_work_hours = models.PositiveSmallIntegerField(verbose_name="Контактная работа, ч")
    independent_work_hours = models.PositiveSmallIntegerField(verbose_name="Самостоятельная работа, ч")
    control_work_hours = models.PositiveSmallIntegerField(verbose_name="Контроль, ч")
    competencies = models.JSONField(verbose_name="Осваиваемые компетенции")

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"

# Модель матрицы академических компетенций
class ACM(models.Model):
    """
    Модель AcademicCompetenceMatrix - модель, представляющая матрицу академических компетенций, на основании
    которой в дальнейшем будет формироваться основной вектор индивидуальной траектории обучения.

    Attributes:
        speciality (ForeignKey): Внешний ключ, связывающий матрицу с моделью специальности
        discipline_list  (JSONField): Перечень осваиваемых дисциплин (хранит указатели на дисциплины)
        technology_stack  (JSONField): Изучаемый стек технологий (подразумевается дублирование для дальнейшего приоритета и распределения)
    """


    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.SET_NULL,
        verbose_name="Специальность",
        blank = True,
        null = True)  
    discipline_list = models.JSONField(verbose_name="Перечень изучаемых дисциплин")
    technology_stack  = models.JSONField(verbose_name="Перечень изучаемых технологий в течение времени")

    def __str__(self):
        return f"Матрица академических компетенций для {self.speciality}"

    class Meta:
        verbose_name = "Матрица академических компетенций"
        verbose_name_plural = "Матрицы академических компетенций"

# Модель компетентностного профиля вакансии
class VCM(models.Model):
    """
    Модель CompetencyProfileOfVacancy - модель, представляющая компетентностный профиль вакансии, на основании
    которой в дальнейшем будет формироваться дополнительный вектор индивидуальных траекторий обучения, соотевтствующий
    запросам работодателей.

    Attributes:
        vacancy_name (CharField): Название вакансии, отражающее содержание компетентностного профиля
        employer  (ForeignKey): Внешний ключ, связывающий компетентностный профиль вакансии с моделью работодателя
        competencies_stack  (JSONField): Перечень запрашиваемых компетенций работодателем
        technology_stack (JSONField): Перечень технологий, запрашиваемых работодателем
        descr (TextField): Описание вакансии (исходное)
    """

    vacancy_name = models.CharField(max_length=255, verbose_name="Название вакансии")
    employer = models.ForeignKey(
        Employer, 
        on_delete=models.SET_NULL,
        verbose_name="ID работодателя",
        blank = True,
        null = True)
    competencies_stack = models.JSONField(verbose_name="Перечень требующихся компетенций")
    technology_stack = models.JSONField(verbose_name="Стек требуемых технологий")
    description = models.TextField(max_length=400, verbose_name="Описание вакансии")

    def __str__(self):
        return f"Компетентностный профиль вакансии {self.vacancy_name}"
    
    class Meta:
        verbose_name = "Компетентностный профиль вакансии"
        verbose_name_plural = "Компетентностные профили вакансии"

class UCM(models.Model):
    """
    Модель UserCompentencyMatrix - модель, представляющая матрицу компетенций пользователя, на основании
    которой в дальнейшем будет формироваться индивидуальная траектория обучения.
    """

    user_id = models.PositiveSmallIntegerField(verbose_name="ID пользователя")
    competencies_stack = models.JSONField(verbose_name="Перечень имеющихся компетенций")
    technology_stack = models.JSONField(verbose_name="Стек изучаемых технологий")

    def __str__(self):
        return f"Матрица компетенций пользователя {self.user}"
    
    class Meta:
        verbose_name = "Матрица компетенций пользователя"
        verbose_name_plural = "Матрицы компетенций пользователей"