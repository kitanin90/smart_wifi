# Generated by Django 2.2.1 on 2019-06-12 03:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0007_auto_20190520_0406'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='authlog',
            options={'verbose_name': 'Лог авторизации', 'verbose_name_plural': 'Логи авторизации'},
        ),
        migrations.AlterModelOptions(
            name='building',
            options={'verbose_name': 'Корпус', 'verbose_name_plural': 'Корпусы'},
        ),
        migrations.AlterModelOptions(
            name='client',
            options={'verbose_name': 'Клиент', 'verbose_name_plural': 'Клиенты'},
        ),
        migrations.AlterModelOptions(
            name='clientparameter',
            options={'verbose_name': 'Параметры клиента', 'verbose_name_plural': 'Параметры клиентов'},
        ),
        migrations.AlterModelOptions(
            name='clientreply',
            options={'verbose_name': 'Настройки клиента', 'verbose_name_plural': 'Настройки клиентов'},
        ),
        migrations.AlterModelOptions(
            name='faculty',
            options={'verbose_name': 'Факультет', 'verbose_name_plural': 'Факультеты'},
        ),
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Группа', 'verbose_name_plural': 'Группы'},
        ),
        migrations.AlterModelOptions(
            name='groupparameter',
            options={'verbose_name': 'Параметры группы', 'verbose_name_plural': 'Параметры групп'},
        ),
        migrations.AlterModelOptions(
            name='groupreply',
            options={'verbose_name': 'Настройки группы', 'verbose_name_plural': 'Настройки групп'},
        ),
        migrations.AlterModelOptions(
            name='nas',
            options={'verbose_name': 'Роутер', 'verbose_name_plural': 'Роутеры'},
        ),
        migrations.AlterModelOptions(
            name='session',
            options={'verbose_name': 'Сессия', 'verbose_name_plural': 'Сессии'},
        ),
        migrations.AlterModelOptions(
            name='usergroup',
            options={'verbose_name': 'Группа клиента', 'verbose_name_plural': 'Группы клиентов'},
        ),
        migrations.AlterField(
            model_name='building',
            name='address',
            field=models.CharField(max_length=255, verbose_name='Адрес'),
        ),
        migrations.AlterField(
            model_name='building',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='client',
            name='faculty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='panel.Faculty', verbose_name='Факультет'),
        ),
        migrations.AlterField(
            model_name='client',
            name='firstname',
            field=models.CharField(max_length=255, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='client',
            name='lastname',
            field=models.CharField(max_length=255, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='client',
            name='patronymic',
            field=models.CharField(max_length=255, verbose_name='Отчество'),
        ),
        migrations.AlterField(
            model_name='client',
            name='status',
            field=models.CharField(max_length=255, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='client',
            name='telephone',
            field=models.CharField(max_length=255, verbose_name='Телефон'),
        ),
        migrations.AlterField(
            model_name='faculty',
            name='building',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='panel.Building', verbose_name='Корпус'),
        ),
        migrations.AlterField(
            model_name='faculty',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='nas',
            name='building',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='panel.Building', verbose_name='Корпус'),
        ),
        migrations.AlterField(
            model_name='nas',
            name='ip',
            field=models.CharField(max_length=15, verbose_name='IP'),
        ),
        migrations.AlterField(
            model_name='nas',
            name='mac',
            field=models.CharField(max_length=50, verbose_name='MAC'),
        ),
        migrations.AlterField(
            model_name='nas',
            name='name',
            field=models.CharField(max_length=32, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='nas',
            name='ports',
            field=models.IntegerField(null=True, verbose_name='Порт'),
        ),
        migrations.AlterField(
            model_name='nas',
            name='secret',
            field=models.CharField(max_length=60, verbose_name='Токен'),
        ),
        migrations.AlterField(
            model_name='nas',
            name='server',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Сервер'),
        ),
        migrations.AlterField(
            model_name='nas',
            name='type',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Тип'),
        ),
    ]