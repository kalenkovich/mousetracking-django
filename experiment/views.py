import json

from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import ParticipantForm
from .models import Participant, Trial, Stages


def router(request, is_test):
    """
    This view routes to all the other ones depending on the stage the participant is at
    """
    participant = Participant.get_or_create_participant(request, is_test=is_test)
    stage = participant.determine_stage(page_just_seen=request.POST.get('just_saw'))

    if stage == Stages.welcome:
        return welcome(request)

    if stage == Stages.participant_form:
        return participant_form(request, participant=participant)

    if stage == Stages.before_training:
        return training(request)

    if stage == Stages.in_training:
        return mousetracking(request)

    if stage == Stages.before_block:
        return before_block(request, block_number=participant.next_block_number, n_blocks=participant.n_blocks)

    if stage == Stages.in_block:
        return mousetracking(request)

    if stage == Stages.goodbye:
        return goodbye(request)


def before_block(request, block_number, n_blocks):
    return render(request, 'experiment/block.html', context=dict(stage=Stages.before_block,
                                                                 block_number=block_number,
                                                                 n_blocks=n_blocks))


def welcome(request):
    return render(request, 'experiment/welcome.html', context=dict(stage=Stages.welcome))


def mousetracking(request):
    return render(request, 'experiment/trial.html')


def goodbye(request):
    return render(request, 'experiment/goodbye.html')


def training(request):
    return render(request, 'experiment/training.html', context=dict(stage=Stages.before_training))


def ajax_redirect():
    return JsonResponse(data=dict(type='redirect'))


def get_new_trial_settings(request, participant: Participant = None):
    participant: Participant = participant or Participant.get_participant(request)
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
    participant: Participant = Participant.get_participant(request)
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


def participant_form(request, participant=None):
    participant = participant or Participant.get_participant(request)

    if request.method == 'POST':
        form = ParticipantForm(request.POST, instance=participant)

        if form.is_valid():
            participant.save_data_from_form(form)
            return HttpResponseRedirect(reverse('router'))

    else:
        form = ParticipantForm(instance=participant)

    context = {
        'form': form,
        'participant': participant,
    }

    return render(request, 'experiment/participant_form.html', context)
