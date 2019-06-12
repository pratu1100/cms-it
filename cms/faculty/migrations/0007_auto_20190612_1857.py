# Generated by Django 2.2.1 on 2019-06-12 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0006_auto_20190612_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='makeuplecture',
            name='division',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='faculty.Division'),
        ),
        migrations.AlterField(
            model_name='makeuplecture',
            name='year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='faculty.Year'),
        ),
    ]
