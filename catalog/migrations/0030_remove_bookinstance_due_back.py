# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-22 17:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0029_bookinstance_borrowed_day'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookinstance',
            name='due_back',
        ),
    ]
