from experiment.models import Participant, Trial, TrialResults

test_participant = Participant.objects.get(is_test=True)


def reset_test_participant():
    for trial in test_participant.trial_set.all():
        # Delete results
        try:
            trial.trialresults.delete()
        except Trial.trialresults.RelatedObjectDoesNotExist:
            pass

        # Forget that we've sent it already
        trial.sent = False

        trial.save()

    test_participant.is_done = False
    test_participant.save()
