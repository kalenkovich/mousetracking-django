# Generated by Django 2.2.12 on 2020-05-22 05:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sessions', '0001_initial'),
        ('experiment', '0011_participant_is_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='session',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sessions.Session'),
        ),
    ]
