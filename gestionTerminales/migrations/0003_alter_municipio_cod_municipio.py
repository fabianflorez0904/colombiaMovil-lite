# Generated by Django 5.2.1 on 2025-05-13 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestionTerminales', '0002_alter_municipio_cod_departamento_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='municipio',
            name='cod_municipio',
            field=models.CharField(max_length=1000),
        ),
    ]
