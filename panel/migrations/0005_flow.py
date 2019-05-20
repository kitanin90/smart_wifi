# Generated by Django 2.2.1 on 2019-05-20 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0004_nas_mac'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unix_secs', models.IntegerField(default=0)),
                ('unix_nsecs', models.IntegerField(default=0)),
                ('sysuptime', models.IntegerField(default=0)),
                ('exaddr', models.CharField(default='0', max_length=45)),
                ('dflows', models.IntegerField(default=0)),
                ('dpkts', models.IntegerField(default=0)),
                ('doctets', models.IntegerField(default=0)),
                ('first', models.IntegerField(default=0)),
                ('last', models.IntegerField(default=0)),
                ('engine_type', models.IntegerField(default=0)),
                ('engine_id', models.IntegerField(default=0)),
                ('srcaddr', models.CharField(default='0', max_length=45)),
                ('dstaddr', models.CharField(default='0', max_length=45)),
                ('nexthop', models.CharField(default='0', max_length=45)),
                ('input', models.IntegerField(default=0)),
                ('output', models.IntegerField(default=0)),
                ('srcport', models.IntegerField(default=0)),
                ('dstport', models.IntegerField(default=0)),
                ('prot', models.IntegerField(default=0)),
                ('tos', models.IntegerField(default=0)),
                ('tcp_flags', models.IntegerField(default=0)),
                ('src_mask', models.IntegerField(default=0)),
                ('dst_mask', models.IntegerField(default=0)),
            ],
        ),
    ]