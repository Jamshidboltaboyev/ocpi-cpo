# Generated by Django 4.2 on 2024-03-04 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('credentials', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='businessdetails',
            options={'ordering': ('name',), 'verbose_name': 'Business Detail', 'verbose_name_plural': 'Business Details'},
        ),
        migrations.AlterModelOptions(
            name='credentials',
            options={'ordering': ['-updated_at'], 'verbose_name': 'Credentials', 'verbose_name_plural': 'Credentials'},
        ),
    ]
