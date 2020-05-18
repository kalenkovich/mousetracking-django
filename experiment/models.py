from django.db import models
from django.utils import timezone


class Participant(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    is_test = models.BooleanField(default=False)


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


class ResourceModel(models.Model):
    name = models.CharField(max_length=40)
    uri = models.URLField()

    class Meta:
        abstract = True


class Image(ResourceModel):
    pass


class Audio(ResourceModel):
    pass
