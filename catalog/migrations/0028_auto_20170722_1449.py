# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-22 12:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0027_auto_20170722_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookinstance',
            name='book',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.Book'),
        ),
        migrations.AlterField(
            model_name='bookinstance',
            name='status',
            field=models.CharField(choices=[('l', 'Loaned to'), ('o', 'Outside'), ('a', 'Available')], default='a', max_length=1),
        ),
    ]
