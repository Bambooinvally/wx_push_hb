# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ammeters',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=100, default=0)),
                ('ammeter_app_code', models.IntegerField()),
                ('ammeter_addr', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'ammeters',
            },
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('name', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('textValue', models.TextField(null=True)),
                ('value', models.CharField(null=True, max_length=255)),
                ('valueAttached', models.CharField(null=True, max_length=255)),
            ],
            options={
                'db_table': 'Config',
            },
        ),
        migrations.CreateModel(
            name='ConfirmedUser',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('openId', models.CharField(max_length=255, verbose_name='微信的openid', unique=True)),
                ('name', models.CharField(null=True, max_length=100, blank=True)),
                ('phone', models.CharField(null=True, max_length=100, blank=True)),
                ('address', models.CharField(null=True, max_length=255, blank=True)),
                ('createTime', models.DateTimeField(auto_now=True)),
                ('IDcard', models.CharField(null=True, max_length=255, verbose_name='注册时的身份证', blank=True)),
                ('extraInfo', models.CharField(null=True, max_length=255, blank=True)),
                ('ammeter', models.ManyToManyField(to='app.Ammeters')),
            ],
            options={
                'db_table': 'confirmedUser',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('submenu_id', models.BigIntegerField(null=True, blank=True)),
                ('name', models.CharField(null=True, max_length=60, blank=True)),
                ('type', models.CharField(null=True, max_length=100, blank=True)),
                ('key', models.CharField(null=True, max_length=128, blank=True)),
                ('url', models.TextField(null=True, blank=True)),
                ('media_id', models.CharField(null=True, max_length=255, blank=True)),
                ('appid', models.CharField(null=True, max_length=100, blank=True)),
                ('pagepath', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'menu',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('source_id', models.IntegerField(serialize=False, primary_key=True)),
                ('projectname', models.CharField(max_length=255)),
                ('province', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=100)),
                ('extraInfo', models.CharField(null=True, max_length=255, blank=True)),
            ],
            options={
                'db_table': 'project',
            },
        ),
        migrations.CreateModel(
            name='PushHistory',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('openId', models.CharField(max_length=255, verbose_name='微信的openid', unique=True)),
                ('name', models.CharField(null=True, max_length=100, blank=True)),
                ('phone', models.CharField(null=True, max_length=100, blank=True)),
                ('address', models.CharField(null=True, max_length=255, blank=True)),
                ('createTime', models.DateTimeField(auto_now=True)),
                ('IDcard', models.CharField(null=True, max_length=255, verbose_name='注册时的身份证', blank=True)),
                ('extraInfo', models.CharField(null=True, max_length=255, blank=True)),
                ('source_id', models.CharField(null=True, max_length=255)),
                ('domain', models.CharField(null=True, max_length=255)),
            ],
            options={
                'db_table': 'superUser',
            },
        ),
        migrations.CreateModel(
            name='UnconfirmUser',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('openId', models.CharField(max_length=255, verbose_name='微信的openid', unique=True)),
                ('name', models.CharField(null=True, max_length=100, blank=True)),
                ('phone', models.CharField(null=True, max_length=100, blank=True)),
                ('address', models.CharField(null=True, max_length=255, blank=True)),
                ('createTime', models.DateTimeField(auto_now=True)),
                ('IDcard', models.CharField(null=True, max_length=255, verbose_name='注册时的身份证', blank=True)),
                ('extraInfo', models.CharField(null=True, max_length=255, blank=True)),
                ('ammeter', models.ManyToManyField(to='app.Ammeters')),
            ],
            options={
                'db_table': 'unconfirmUser',
            },
        ),
        migrations.CreateModel(
            name='URLSource',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('url', models.CharField(null=True, max_length=255)),
                ('desc', models.CharField(null=True, max_length=100)),
                ('vaild', models.BooleanField()),
            ],
            options={
                'db_table': 'urlsource',
            },
        ),
        migrations.CreateModel(
            name='WxUser',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('openId', models.CharField(max_length=255, verbose_name='微信的openid', db_index=True)),
                ('nickname', models.CharField(null=True, max_length=255, verbose_name='微信名字', blank=True)),
                ('sex', models.NullBooleanField()),
                ('city', models.CharField(null=True, max_length=100, verbose_name='所在城市', blank=True)),
                ('country', models.CharField(null=True, max_length=100, verbose_name='所在国家', blank=True)),
                ('subscribe_time', models.BigIntegerField()),
                ('subscribe', models.BooleanField()),
                ('subscribe_scene', models.CharField(null=True, max_length=50, blank=True)),
                ('ammeter_id', models.BigIntegerField(null=True, blank=True)),
                ('name', models.CharField(null=True, max_length=100, verbose_name='注册时的名字', blank=True)),
                ('phone', models.CharField(null=True, max_length=100, verbose_name='注册时的手机', blank=True)),
                ('IDcard', models.CharField(null=True, max_length=255, verbose_name='注册时的身份证', blank=True)),
                ('address', models.CharField(null=True, max_length=255, blank=True)),
                ('source_id', models.IntegerField(null=True, verbose_name='source的外键')),
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
