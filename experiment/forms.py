from django.forms import ModelForm, BooleanField, HiddenInput, CharField
from .models import Participant


class ParticipantForm(ModelForm):
    gave_consent = BooleanField(required=True)
    form_name = CharField(widget=HiddenInput(), initial=Participant.PARTICIPANT_FORM_NAME)

    class Meta:
        model = Participant
        fields = ['age', 'sex', 'native_language', 'dominant_hand', 'gave_consent']
        help_texts = {
            "native_language": 'Если у вас несколько родных языков и один из них - русский, выберите опцию "русский"'
        }


class DevicesQuestionnaireForm(ModelForm):
    form_name = CharField(widget=HiddenInput(), initial=Participant.DEVICES_QUESTIONNAIRE_FORM_NAME)

    class Meta:
        model = Participant
        fields = ['pointing_device', 'headphones_on']
