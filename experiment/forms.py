from django.forms import ModelForm, BooleanField
from .models import Participant


class ParticipantForm(ModelForm):
    gave_consent = BooleanField(required=True)

    class Meta:
        model = Participant
        fields = ['age', 'sex', 'gave_consent']
