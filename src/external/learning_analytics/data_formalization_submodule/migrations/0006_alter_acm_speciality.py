# Generated by Django 5.1.6 on 2025-04-15 21:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_analytics_data_formalization_submodule', '0005_remove_speciality_education_duration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acm',
            name='speciality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='learning_analytics_data_formalization_submodule.curriculum', verbose_name='Специальность'),
        ),
    ]
