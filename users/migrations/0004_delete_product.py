# Generated by Django 5.1.6 on 2025-05-25 23:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_customuser_is_active_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Product',
        ),
    ]
