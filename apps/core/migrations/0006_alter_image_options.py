# Generated by Django 4.2 on 2024-03-04 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ('-created_at',), 'verbose_name': 'Image', 'verbose_name_plural': 'Images'},
        ),
    ]
