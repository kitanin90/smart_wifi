# Generated by Django 2.2.1 on 2019-05-12 12:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nas',
            name='faculty',
        ),
    ]