# Generated by Django 5.1.6 on 2025-02-20 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_analytics', '0002_competention'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competention',
            name='code',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='competention',
            name='description',
            field=models.TextField(max_length=400),
        ),
        migrations.AlterField(
            model_name='competention',
            name='name',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='technology',
            name='description',
            field=models.TextField(max_length=400),
        ),
        migrations.AlterField(
            model_name='technology',
            name='name',
            field=models.CharField(max_length=60),
        ),
    ]
