# Generated by Django 5.1.6 on 2025-03-04 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting_module', '0003_alter_speciality_year_of_admission'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discpiline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True, verbose_name='Код дисциплины')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('semesters', models.CharField(max_length=12, verbose_name='Период освоения (семестры)')),
                ('contact_work_hours', models.PositiveIntegerField(verbose_name='Контактная работа, ч')),
                ('independent_work_hours', models.PositiveIntegerField(verbose_name='Самостоятельная работа, ч')),
                ('controle_work_hours', models.PositiveIntegerField(verbose_name='Контроль, ч')),
                ('competencies', models.JSONField(verbose_name='Осваиваемые компетенции')),
            ],
            options={
                'verbose_name': 'Дисциплина',
                'verbose_name_plural': 'Дисциплины',
            },
        ),
    ]
