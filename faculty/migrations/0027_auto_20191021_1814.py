# Generated by Django 2.2.1 on 2019-10-21 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0026_leave_supporting_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guestlecture',
            name='lec_subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='faculty.Subject'),
        ),
    ]