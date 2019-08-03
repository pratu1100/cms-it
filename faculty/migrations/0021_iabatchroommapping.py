# Generated by Django 2.2.1 on 2019-07-27 11:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0020_auto_20190727_1254'),
    ]

    operations = [
        migrations.CreateModel(
            name='IaBatchRoomMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='faculty.Batch')),
                ('ia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='faculty.IA')),
                ('room', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='faculty.Room')),
            ],
        ),
    ]