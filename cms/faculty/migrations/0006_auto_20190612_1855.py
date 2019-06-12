# Generated by Django 2.2.1 on 2019-06-12 13:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0005_makeuplecture'),
    ]

    operations = [
        migrations.AddField(
            model_name='makeuplecture',
            name='division',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='faculty.Division'),
        ),
        migrations.AddField(
            model_name='makeuplecture',
            name='year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='faculty.Year'),
        ),
    ]
