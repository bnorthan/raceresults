# Generated by Django 3.1.5 on 2021-03-12 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raceresults', '0003_race_date_race'),
    ]

    operations = [
        migrations.AlterField(
            model_name='race',
            name='date_race',
            field=models.DateField(blank=True, null=True, verbose_name='date of race'),
        ),
    ]
