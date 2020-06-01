import uuid
from random import randint
from enum import Enum

import numpy as np
import pandas as pd
from django.contrib.sessions.models import Session
from django.db import models
from django.templatetags.static import static
from django.utils import timezone


def create_random_seed():
    return randint(1, 1e6)


class Stages(object):
    welcome = 'welcome'
    before_block = 'before_block'
    in_block = 'in_block'
    goodbye = 'goodbye'


class Participant(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    session = models.OneToOneField(Session, on_delete=models.SET_NULL, null=True)
    random_seed = models.IntegerField(default=create_random_seed, null=True)

    stage = models.CharField(max_length=80)

    is_test = models.BooleanField(default=False)

    is_done = models.BooleanField(default=False)

    @classmethod
    def get_or_create_participant(cls, request) -> 'Participant':
        # This will create the session instance if it does not exist yet
        if not request.session.session_key:
            request.session.save()
        session = Session.objects.get(session_key=request.session.session_key)
        try:
            return session.participant
        except Session.participant.RelatedObjectDoesNotExist:
            participant = cls.objects.create(session=session)
            participant.create_trials(test=False)
            return participant

    def get_next_trial(self):
        next_trial = self.trial_set.filter(sent=False).order_by('number').first()
        if not next_trial:
            self.is_done = True
            self.save()

        return next_trial

    def get_last_sent_trial(self):
        return self.trial_set.filter(sent=True).order_by('number').last()

    def create_trials(self, test=False):
        experiment_list = self.create_trial_list(test=test)

        trials = list()
        for number, row in enumerate(experiment_list.itertuples(), 1):
            trial = Trial(participant=self, number=number)

            trial.frame_top_left = Image.get_if_exists(name=row.frame[0][0])
            trial.frame_top_right = Image.get_if_exists(name=row.frame[0][1])
            trial.frame_bottom_left = Image.get_if_exists(name=row.frame[1][0])
            trial.frame_bottom_right = Image.get_if_exists(name=row.frame[1][1])
            trial.frame_duration = row.frame_duration

            trial.response_option_left = Image.objects.get(name=row.response_option_left)
            trial.response_option_right = Image.objects.get(name=row.response_option_right)

            trial.audio = Audio.objects.get(name=row.audio_name)
            trial.hold_duration = row.hold_duration

            trials.append(trial)

        Trial.objects.bulk_create(trials)

    def create_trial_list(self, test=False) -> pd.DataFrame:
        if not test:
            # I import here to allow myself to have circular imports. This is a big no-no but I can't figure out how
            # to structure it better.
            from .create_trial_list import make_stimulus_list

            trial_list = make_stimulus_list(random_seed=self.random_seed)

            # The data format has to be adapted a bit from the offline version.
            # This is some awful code below and it might have been better to change the original code but that would
            # make it less compatible with the offline version.

            def make_frame(configuration, objects):
                frame = [[None, None], [None, None]]
                for r, c, object_ in zip(*np.where(configuration), objects):
                    frame[r][c] = object_
                return frame
            trial_list['frame'] = trial_list.apply(lambda row: make_frame(row.configuration, row.objects),
                                                   axis='columns')
            trial_list['frame_duration'] = trial_list.objects.apply(len) * 750  # 750 ms per object

            trial_list['target'] = trial_list.apply(lambda row: row.frame[row.target_cell[0]][row.target_cell[1]],
                                                    axis='columns')
            trial_list['lure'] = trial_list.apply(lambda row: row.frame[row.lure_cell[0]][row.lure_cell[1]],
                                                  axis='columns')
            trial_list['response_option_left'] = trial_list.target.where(trial_list.target_position == 'left',
                                                                         trial_list.lure)
            trial_list['response_option_right'] = trial_list.target.where(trial_list.target_position == 'right',
                                                                          trial_list.lure)

            trial_list.rename(columns={'onset': 'hold_duration'}, inplace=True)

            return trial_list
        else:
            return self.create_test_trial_list()

    @staticmethod
    def create_test_trial_list():
        return pd.DataFrame(
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

    def determine_stage(self, page_just_seen):

        if self.stage == '':
            self.stage = Stages.welcome
        elif self.stage == Stages.welcome and page_just_seen == Stages.welcome:
            self.stage = Stages.before_block
        elif self.stage == Stages.before_block and page_just_seen == Stages.before_block:
            self.stage = Stages.in_block
        else:
            # Setting "before_block" and "goodbye" stages is handles by the `get_settings` view
            pass

        self.save()
        return self.stage


class Trial(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    # First, second, etc. trial
    number = models.IntegerField()

    participant = models.ForeignKey(Participant, on_delete=models.PROTECT)

    # Have we sent this trial to the participant already
    sent = models.BooleanField(default=False)

    frame_top_left = models.ForeignKey('Image', on_delete=models.PROTECT, default=None, null=True,
                                       related_name='trials_with_this_in_top_left')
    frame_top_right = models.ForeignKey('Image', on_delete=models.PROTECT, default=None, null=True,
                                        related_name='trials_with_this_in_top_right')
    frame_bottom_left = models.ForeignKey('Image', on_delete=models.PROTECT, default=None, null=True,
                                          related_name='trials_with_this_in_bottom_left')
    frame_bottom_right = models.ForeignKey('Image', on_delete=models.PROTECT, default=None, null=True,
                                           related_name='trials_with_this_in_bottom_right')
    frame_duration = models.IntegerField()

    response_option_left = models.ForeignKey('Image', on_delete=models.PROTECT, null=False,
                                             related_name='trial_with_this_as_left_option')
    response_option_right = models.ForeignKey('Image', on_delete=models.PROTECT, null=False,
                                              related_name='trial_with_this_as_right_option')

    audio = models.ForeignKey('Audio',  on_delete=models.PROTECT, null=False)

    # Time before the options are presented and the cursor is released
    hold_duration = models.IntegerField()

    def get_settings(self):
        frame_images_uris = [
            static(self.frame_top_left.uri) if self.frame_top_left else None,
            static(self.frame_top_right.uri) if self.frame_top_right else None,
            static(self.frame_bottom_left.uri) if self.frame_bottom_left else None,
            static(self.frame_bottom_right.uri) if self.frame_bottom_right else None
        ]
        uris = dict(left=static(self.response_option_left.uri),
                    right=static(self.response_option_right.uri),
                    audio=static(self.audio.uri),
                    frame_images=frame_images_uris)
        timing = dict(frame=1500, audio=1160)
        return dict(uris=uris, timing=timing)

    def save_results(self, results):
        trial_results = TrialResults(
            trial=self,
            start_pressed=results['dt_start_pressed'],
            frame_presented=results['dt_frame_presented'],
            audio_started=results['dt_audio_started'],
            response_selected=results['dt_response_selected'],
            selected_response=results['selected_response'],
            trajectory=results['trajectory'],
        )
        trial_results.save()


class TrialResults(models.Model):
    trial = models.OneToOneField(Trial, on_delete=models.PROTECT)

    start_pressed = models.DateTimeField()
    frame_presented = models.DateTimeField()
    audio_started = models.DateTimeField()
    response_selected = models.DateTimeField()
    selected_response = models.CharField(max_length=40)
    trajectory = models.TextField()


class ResourceModel(models.Model):
    name = models.CharField(max_length=40, unique=True)
    uri = models.URLField()

    class Meta:
        abstract = True

    @classmethod
    def get_if_exists(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except cls.DoesNotExist:
            return None


class Image(ResourceModel):
    pass


class Audio(ResourceModel):
    pass
