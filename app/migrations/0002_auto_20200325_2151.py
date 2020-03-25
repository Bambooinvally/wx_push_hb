# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PushHistory',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('touser', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=100)),
                ('massage', models.CharField(max_length=512)),
                ('pushtime', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'publishhistory',
            },
        ),
        migrations.AlterField(
            model_name='confirmeduser',
            name='createTime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='confirmeduser',
            name='openId',
            field=models.CharField(verbose_name='微信的openid', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='superuser',
            name='createTime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='superuser',
            name='domain',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='superuser',
            name='openId',
            field=models.CharField(verbose_name='微信的openid', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='superuser',
            name='source_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='unconfirmuser',
            name='createTime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='unconfirmuser',
            name='openId',
            field=models.CharField(verbose_name='微信的openid', max_length=255, unique=True),
        ),
    ]
