# Generated by Django 3.1.6 on 2021-02-14 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raceresults', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='time',
            field=models.DurationField(default=0, null=True),
        ),
    ]
