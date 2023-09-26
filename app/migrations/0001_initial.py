# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ammeters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('domain', models.CharField(max_length=100, default=0)),
                ('ammeter_addr', models.CharField(max_length=255)),
                ('coordinate', models.CharField(max_length=100, null=True)),
                ('ammeter_app_code', models.CharField(max_length=255)),
                ('ammeter_sensorId', models.CharField(max_length=255, null=True)),
                ('ammeter_info', models.CharField(max_length=255, null=True)),
                ('ammeter_unit', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'ammeters',
            },
        ),
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
            name='ConfirmedUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('openId', models.CharField(verbose_name='微信的openid', max_length=255, unique=True)),
                ('name', models.CharField(max_length=100, blank=True, null=True)),
                ('phone', models.CharField(max_length=100, blank=True, null=True)),
                ('address', models.CharField(max_length=255, blank=True, null=True)),
                ('createTime', models.DateTimeField(auto_now=True)),
                ('IDcard', models.CharField(verbose_name='注册时的身份证', max_length=255, blank=True, null=True)),
                ('extraInfo', models.CharField(max_length=255, blank=True, null=True)),
                ('ammeter', models.ManyToManyField(to='app.Ammeters')),
            ],
            options={
                'db_table': 'confirmedUser',
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
            name='Project',
            fields=[
                ('source_id', models.IntegerField(primary_key=True, serialize=False)),
                ('projectname', models.CharField(max_length=255)),
                ('province', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=100)),
                ('extraInfo', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'project',
            },
        ),
        migrations.CreateModel(
            name='PushHistory',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('touser', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=100)),
                ('massage', models.CharField(max_length=512)),
                ('pushtime', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'pushhistory',
            },
        ),
        migrations.CreateModel(
            name='SuperUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('openId', models.CharField(verbose_name='微信的openid', max_length=255, unique=True)),
                ('name', models.CharField(max_length=100, blank=True, null=True)),
                ('phone', models.CharField(max_length=100, blank=True, null=True)),
                ('address', models.CharField(max_length=255, blank=True, null=True)),
                ('createTime', models.DateTimeField(auto_now=True)),
                ('IDcard', models.CharField(verbose_name='注册时的身份证', max_length=255, blank=True, null=True)),
                ('extraInfo', models.CharField(max_length=255, blank=True, null=True)),
                ('source_id', models.CharField(max_length=255, null=True)),
                ('domain', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'superUser',
            },
        ),
        migrations.CreateModel(
            name='UnconfirmUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('openId', models.CharField(verbose_name='微信的openid', max_length=255, unique=True)),
                ('name', models.CharField(max_length=100, blank=True, null=True)),
                ('phone', models.CharField(max_length=100, blank=True, null=True)),
                ('address', models.CharField(max_length=255, blank=True, null=True)),
                ('createTime', models.DateTimeField(auto_now=True)),
                ('IDcard', models.CharField(verbose_name='注册时的身份证', max_length=255, blank=True, null=True)),
                ('extraInfo', models.CharField(max_length=255, blank=True, null=True)),
                ('ammeter', models.ManyToManyField(to='app.Ammeters')),
            ],
            options={
                'db_table': 'unconfirmUser',
            },
        ),
        migrations.CreateModel(
            name='URLSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('url', models.CharField(max_length=255, null=True)),
                ('desc', models.CharField(max_length=100, null=True)),
                ('vaild', models.BooleanField()),
            ],
            options={
                'db_table': 'urlsource',
            },
        ),
        migrations.CreateModel(
            name='WxUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('openId', models.CharField(verbose_name='微信的openid', max_length=255, db_index=True)),
                ('nickname', models.CharField(verbose_name='微信名字', max_length=255, blank=True, null=True)),
                ('sex', models.NullBooleanField()),
                ('city', models.CharField(verbose_name='所在城市', max_length=100, blank=True, null=True)),
                ('country', models.CharField(verbose_name='所在国家', max_length=100, blank=True, null=True)),
                ('subscribe_time', models.BigIntegerField()),
                ('subscribe', models.BooleanField()),
                ('subscribe_scene', models.CharField(max_length=50, blank=True, null=True)),
                ('ammeter_id', models.BigIntegerField(blank=True, null=True)),
                ('name', models.CharField(verbose_name='注册时的名字', max_length=100, blank=True, null=True)),
                ('phone', models.CharField(verbose_name='注册时的手机', max_length=100, blank=True, null=True)),
                ('IDcard', models.CharField(verbose_name='注册时的身份证', max_length=255, blank=True, null=True)),
                ('address', models.CharField(max_length=255, blank=True, null=True)),
                ('source_id', models.IntegerField(verbose_name='source的外键', null=True)),
                ('vaild', models.NullBooleanField(verbose_name='是否注销', default=False)),
            ],
            options={
                'db_table': 'wxUser',
            },
        ),
        migrations.AddField(
            model_name='ammeters',
            name='source',
            field=models.ForeignKey(to='app.Project'),
        ),
    ]
