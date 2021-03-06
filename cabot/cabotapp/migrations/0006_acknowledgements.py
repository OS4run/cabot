# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-05-14 22:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cabotapp', '0005_auto_20190301_2114'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acknowledgement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_if', models.TextField(choices=[(b'C', b'Match check.')], default=b'C', max_length=1)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('note', models.TextField(blank=True, help_text=b'Leave a note explaining why this ack was created.', max_length=255)),
                ('closed_at', models.DateTimeField(default=None, null=True)),
                ('closed_reason', models.TextField(default=None, max_length=255, null=True)),
                ('expire_at', models.DateTimeField(default=None, help_text=b'After this time the acknowledgement will be automatically closed and alerts will resume, even if the check is still failing.', null=True)),
                ('close_after_successes', models.PositiveIntegerField(default=1, help_text=b'After this many consecutive successful runs the acknowledgement will be automatically closed. Enter 0 to disable.', null=True)),
                ('created_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='statuscheckresult',
            name='acked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='statuscheck',
            name='calculated_status',
            field=models.CharField(blank=True, choices=[(b'passing', b'passing'), (b'acked', b'acked'), (b'intermittent', b'intermittent'), (b'failing', b'failing')], default=b'passing', max_length=50),
        ),
        migrations.AddField(
            model_name='acknowledgement',
            name='status_check',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cabotapp.StatusCheck'),
        ),
        migrations.AddIndex(
            model_name='acknowledgement',
            index=models.Index(fields=[b'status_check_id', b'closed_at', b'expire_at', b'created_at'], name='cabotapp_ac_status__231f51_idx'),
        ),
        migrations.AddIndex(
            model_name='acknowledgement',
            index=models.Index(fields=[b'closed_at'], name='cabotapp_ac_closed__8e3332_idx'),
        ),
    ]
