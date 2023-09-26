# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20210803_1723'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unconfirmuser',
            old_name='phone',
            new_name='code',
        ),
    ]
