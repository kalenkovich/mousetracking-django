from django.forms import ModelForm, BooleanField, HiddenInput, CharField
from .models import Participant


class ParticipantForm(ModelForm):
    gave_consent = BooleanField(required=True)
    form_name = CharField(widget=HiddenInput(), initial='ParticipantForm')

    class Meta:
        model = Participant
        fields = ['age', 'sex', 'native_language', 'gave_consent']
        help_texts = {
            "native_language": 'Если у вас несколько родных языков и один из них - русский, выберите опцию "русский"'
        }
