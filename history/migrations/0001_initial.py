# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-22 17:47
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalog', '0031_auto_20170722_1947'),
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrowed_day', models.DateField(default=datetime.date.today)),
                ('returning_day', models.DateField(default=datetime.date.today, null=True)),
                ('book_owner_name', models.TextField(max_length=30)),
                ('book_holder_name', models.TextField(max_length=30)),
                ('book_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.BookInstance')),
            ],
            options={
                'ordering': ['-borrowed_day'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='history',
            unique_together=set([('book_instance', 'borrowed_day', 'returning_day')]),
        ),
    ]
