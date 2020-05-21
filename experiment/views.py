import json

from django.shortcuts import render
from django.http import JsonResponse

from .models import Participant, Trial


def router(request):
    """
    This view routes to all the other ones depending on the stage the participant is at
    """
    participant = Participant.get_participant(request)

    if participant.is_done:
        return goodbye(request)

    saw_welcome = request.COOKIES.get("saw-welcome")
    if not saw_welcome:
        return welcome(request)
    else:
        return mousetracking(request)


def welcome(request):
    return render(request, 'experiment/welcome.html')


def mousetracking(request):
    return render(request, 'experiment/trial.html')


def goodbye(request):
    return render(request, 'experiment/goodbye.html')


def ajax_redirect():
    return JsonResponse(data=dict(type='redirect'))


def get_new_trial_settings(request, participant: Participant = None):
    participant: Participant = participant or Participant.get_participant(request)
    trial: Trial = participant.get_next_trial()
    if trial:
        trial_settings = trial.get_settings()
        trial_settings['type'] = 'trial_settings'
        trial.sent = True
        trial.save()
        return JsonResponse(data=trial_settings)
    else:
        return ajax_redirect()


def save_trial_results(request):
    participant: Participant = Participant.get_participant(request)
    trial: Trial = participant.get_last_sent_trial()
    trial.save_results(json.loads(request.body.decode('utf-8')).get('results'))
    return get_new_trial_settings(request, participant=participant)
