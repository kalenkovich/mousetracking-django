# Generated by Django 2.2.13 on 2020-07-08 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0031_participant_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='session',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sessions.Session'),
        ),
    ]
