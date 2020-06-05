from django.forms import ModelForm, BooleanField, HiddenInput, CharField
from .models import Participant


class ParticipantForm(ModelForm):
    gave_consent = BooleanField(required=True)
    form_name = CharField(widget=HiddenInput(), initial='ParticipantForm')

    class Meta:
        model = Participant
        fields = ['age', 'sex', 'gave_consent']
