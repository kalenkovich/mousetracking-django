# Generated by Django 2.2.12 on 2020-05-15 07:59

from django.db import migrations


def add_test_participant(apps, schema_editor):
    Participant = apps.get_model('experiment', 'Participant')
    test_participant = Participant(is_test=True)
    test_participant.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_test_participant),
    ]
