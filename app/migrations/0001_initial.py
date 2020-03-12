# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('name', models.CharField(primary_key=True, max_length=255, serialize=False)),
                ('textValue', models.TextField(null=True)),
                ('value', models.CharField(max_length=255, null=True)),
                ('valueAttached', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'Config',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('submenu_id', models.BigIntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=60, blank=True, null=True)),
                ('type', models.CharField(max_length=100, blank=True, null=True)),
                ('key', models.CharField(max_length=128, blank=True, null=True)),
                ('url', models.TextField(blank=True, null=True)),
                ('media_id', models.CharField(max_length=255, blank=True, null=True)),
                ('appid', models.CharField(max_length=100, blank=True, null=True)),
                ('pagepath', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'menu',
            },
        ),
        migrations.CreateModel(
            name='UnconfirmUser',
            fields=[
                ('name', models.CharField(max_length=100, blank=True, null=True)),
                ('phone', models.CharField(max_length=100, blank=True, null=True)),
                ('address', models.CharField(max_length=255, blank=True, null=True)),
                ('openId', models.CharField(verbose_name='微信的openid', primary_key=True, max_length=255, serialize=False)),
            ],
            options={
                'db_table': 'unconfirmUser',
            },
        ),
        migrations.CreateModel(
            name='WxUser',
            fields=[
                ('openId', models.CharField(verbose_name='微信的openid', primary_key=True, max_length=255, serialize=False)),
                ('nickname', models.CharField(verbose_name='微信名字', max_length=255, blank=True, null=True)),
                ('sex', models.NullBooleanField()),
                ('city', models.CharField(verbose_name='所在城市', max_length=100, blank=True, null=True)),
                ('country', models.CharField(verbose_name='所在国家', max_length=100, blank=True, null=True)),
                ('subscribe_time', models.BigIntegerField()),
                ('subscribe', models.BooleanField()),
                ('subscribe_scene', models.CharField(max_length=50, blank=True, null=True)),
                ('ammeter_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'wxUser',
            },
        ),
    ]
