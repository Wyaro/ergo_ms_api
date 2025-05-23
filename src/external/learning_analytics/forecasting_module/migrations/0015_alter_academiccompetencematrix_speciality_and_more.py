# Generated by Django 5.1.6 on 2025-03-14 15:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting_module', '0014_alter_competencyprofileofvacancy_employer'),
        ('learning_analytics', '0007_alter_technology_popularity_alter_technology_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academiccompetencematrix',
            name='speciality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forecasting_module.speciality', verbose_name='Специальность'),
        ),
        migrations.AlterField(
            model_name='competencyprofileofvacancy',
            name='employer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='learning_analytics.employer', verbose_name='ID работодателя'),
        ),
    ]
