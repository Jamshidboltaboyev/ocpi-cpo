# Generated by Django 4.2 on 2024-03-04 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_alter_connector_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connector',
            name='name',
            field=models.CharField(max_length=40, null=True, verbose_name='Name'),
        ),
    ]
