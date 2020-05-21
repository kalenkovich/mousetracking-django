# Generated by Django 2.2.12 on 2020-05-20 08:33
import pandas as pd

from django.db import migrations

from experiment.models import Participant


def get_if_exists(cls, **kwargs):
    try:
        return cls.objects.get(**kwargs)
    except cls.DoesNotExist:
        return None


def create_trials_for_test_participant(apps, schema_editor):
    Participant = apps.get_model('experiment', 'Participant')
    test_participant = Participant.objects.get(is_test=True)

    test_trials = pd.DataFrame(
        columns='frame,frame_duration,response_option_left,response_option_right,audio_name,hold_duration'.split(
            ','),
        data=[
            [[[None, 'acorn'], ['axe', None]], 1500, 'acorn', 'axe', 'in-this-picture_left_negative', 1714],
            [[['acorn', None], [None, 'axe']], 1500, 'axe', 'acorn', 'this-time_negative_top', 1123],
            [[['flask', 'acorn'], [None, 'axe']], 2250, 'acorn', 'axe', 'this-time_negative_top', 1123],
            [[['medal', 'axe'], ['flask', 'acorn']], 3000, 'medal', 'acorn', 'this-time_top_negative', 1442],
            [[['flask', 'medal'], ['axe', None]], 2250, 'axe', 'medal', 'this-time_negative_right', 1123],
            [[[None, 'acorn'], ['flask', 'medal']], 2250, 'acorn', 'flask', 'this-time_positive_bottom', 1160],
        ])

    Trial = apps.get_model('experiment', 'Trial')
    Image = apps.get_model('experiment', 'Image')
    Audio = apps.get_model('experiment', 'Audio')

    for number, row in enumerate(test_trials.itertuples(), 1):
        trial = Trial(participant=test_participant, number=number)

        trial.frame_top_left = get_if_exists(Image, name=row.frame[0][0])
        trial.frame_top_right = get_if_exists(Image, name=row.frame[0][1])
        trial.frame_bottom_left = get_if_exists(Image, name=row.frame[1][0])
        trial.frame_bottom_right = get_if_exists(Image, name=row.frame[1][1])
        trial.frame_duration = row.frame_duration

        trial.response_option_left = Image.objects.get(name=row.response_option_left)
        trial.response_option_right = Image.objects.get(name=row.response_option_right)

        trial.audio = Audio.objects.get(name=row.audio_name)
        trial.hold_duration = row.hold_duration

        trial.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0007_auto_20200520_1043'),
    ]

    operations = [
        migrations.RunPython(create_trials_for_test_participant)
    ]