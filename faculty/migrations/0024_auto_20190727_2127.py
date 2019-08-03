# Generated by Django 2.2.1 on 2019-07-27 15:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('faculty', '0023_auto_20190727_2117'),
    ]

    operations = [
        migrations.AddField(
            model_name='iabatchroommapping',
            name='suervisor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ia',
            name='ia_end_time',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='ia',
            name='ia_start_time',
            field=models.TimeField(),
        ),
    ]