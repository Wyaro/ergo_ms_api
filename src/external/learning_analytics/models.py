from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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

# Модель Employer представляет работодателя
class Employer(models.Model):
    """
    Модель Employer представляет работодателя

    Attributes:
        company_name (CharField): Название компании (работодателя). Максимальная длина - 255 символов.
        description (TextField): Описание компании, её предметной области и сферы деятельности в целом.
        email (EmailField): Электронная почта компании для связи.
        created_at (DateTimeField): Дата и время появления первичного упоминания работодателя.
        updated_at (DateTimeField): Дата и время последней редакции информации о работодателе.
        rating (DecimalField): Рейтинг работодателя от 1 до 5. Вещественное число с ограничением в два знака после запятой.
    """

    company_name = models.CharField(max_length=255, verbose_name="Название компании")
    description = models.TextField(verbose_name="Описание компании")
    email = models.EmailField(verbose_name="Контактный email", unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата создания записи")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    rating = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return f"{self.company_name}"
    
    class Meta:
        verbose_name = "Работодатель"
        verbose_name_plural = "Работодатели"


