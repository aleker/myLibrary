# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-22 18:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0002_auto_20170722_1947'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='history',
            unique_together=set([]),
        ),
    ]
