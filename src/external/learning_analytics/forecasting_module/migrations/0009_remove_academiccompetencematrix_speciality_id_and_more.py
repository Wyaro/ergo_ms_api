# Generated by Django 5.1.6 on 2025-03-14 12:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting_module', '0008_competencyprofileofvacancy_and_more'),
        ('learning_analytics', '0007_alter_technology_popularity_alter_technology_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='academiccompetencematrix',
            name='speciality_id',
        ),
        migrations.RemoveField(
            model_name='competencyprofileofvacancy',
            name='employer_id',
        ),
        migrations.AddField(
            model_name='academiccompetencematrix',
            name='speciality',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='forecasting_module.speciality', verbose_name='Специальность'),
        ),
        migrations.AddField(
            model_name='competencyprofileofvacancy',
            name='employer',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='learning_analytics.employer', verbose_name='ID работодателя'),
        ),
    ]
