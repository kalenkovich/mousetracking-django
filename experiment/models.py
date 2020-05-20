from django.db import models
from django.utils import timezone
from django.templatetags.static import static


class Participant(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    is_test = models.BooleanField(default=False)

    @classmethod
    def get_participant(cls, request):
        # TODO: get participant from a cookie
        return cls.objects.get(is_test=True)

    def get_next_trial(self):
        # TODO: get next trial that has not been sent to the participant yet
        return self.trial_set.first()

    def get_last_sent_trial(self):
        # TODO: get the last trial whose settings have been sent to the participant
        return self.trial_set.first()


class Trial(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    # First, second, etc. trial
    number = models.IntegerField()

    participant = models.ForeignKey(Participant, on_delete=models.PROTECT)

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
            static(self.frame_bottom_right.uri) if self.frame_top_right else None
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
    name = models.CharField(max_length=40)
    uri = models.URLField()

    class Meta:
        abstract = True


class Image(ResourceModel):
    pass


class Audio(ResourceModel):
    pass
