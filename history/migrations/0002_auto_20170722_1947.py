# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-22 17:47
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='returning_day',
            field=models.DateField(blank=True, default=datetime.date.today, null=True),
        ),
    ]
