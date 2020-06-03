import json

from django.shortcuts import render
from django.http import JsonResponse

from .models import Participant, Trial, Stages


def router(request):
    """
    This view routes to all the other ones depending on the stage the participant is at
    """
    participant = Participant.get_or_create_participant(request)
    stage = participant.determine_stage(page_just_seen=request.POST.get('just_saw'))

    if stage == Stages.welcome:
        return welcome(request)

    if stage == Stages.before_block:
        return before_block(request)

    if stage == Stages.in_block:
        return mousetracking(request)

    if stage == Stages.goodbye:
        return goodbye(request)


def before_block(request):
    return render(request, 'experiment/block.html', context=dict(stage=Stages.before_block))


def welcome(request):
    return render(request, 'experiment/welcome.html', context=dict(stage=Stages.welcome))


def mousetracking(request):
    return render(request, 'experiment/trial.html')


def goodbye(request):
    return render(request, 'experiment/goodbye.html')


def ajax_redirect():
    return JsonResponse(data=dict(type='redirect'))


def get_new_trial_settings(request, participant: Participant = None):
    participant: Participant = participant or Participant.get_or_create_participant(request)
    trial: Trial = participant.get_next_trial(about_to_be_sent=True)
    if trial:
        trial_settings = trial.get_settings()
        trial_settings['type'] = 'trial_settings'
        trial_settings['trial_id'] = trial.unique_id
        return JsonResponse(data=trial_settings)
    else:
        return ajax_redirect()


def save_trial_results(request):
    results = json.loads(request.body.decode('utf-8')).get('results')
    participant: Participant = Participant.get_or_create_participant(request)
    trial: Trial = participant.get_last_sent_trial()

    # Trial might be None if another participant is using the same browser by clearing cookies without clearing local
    # storage which contained trial setting from the last unrun trial of the previous participant. This is very unlikely
    # to happen outside of the development situation but we don't want to get an error. In this case, we just proceed to
    # sending the first actual trial.
    if trial is not None:
        trial_id_received = results.get('trial_id')
        if trial_id_received == trial.unique_id:
            # This should be the most common case: the received results correspond to the last trial sent.
            trial.save_results(results)
        else:
            # If the trial corresponding to the results belongs to the correct participant and we had not received the
            # result previously, we will save the results. This can happen if we already sent a new trial in parallel,
            # while dealing with saving the results.
            try:
                trial = participant.trial_set.get(unique_id=trial_id_received)
                if not hasattr(trial, 'trialresults'):
                    trial.save_results(results)
            except Trial.DoesNotExist:
                # We got results from a rogue trial, probably from a different attempt on the same computer.
                pass

    return get_new_trial_settings(request, participant=participant)
