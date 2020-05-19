from django.shortcuts import render
from django.http import JsonResponse

from .models import Image, Audio


def router(request):
    """
    This view routes to all the other ones depending on the stage the participant is at
    """
    saw_welcome = request.COOKIES.get("saw-welcome")
    if not saw_welcome:
        return welcome(request)
    else:
        return mousetracking(request)


def welcome(request):
    return render(request, 'experiment/welcome.html')


def mousetracking(request):
    return render(request, 'experiment/trial.html')


def get_new_trial_settings(request):

    acorn_uri = Image.objects.get(name='acorn').uri
    axe_uri = Image.objects.get(name='axe').uri
    audio_uri = Audio.objects.get(name='this-time_positive_bottom').uri
    frame_images = [acorn_uri, None, axe_uri, None]
    uris = dict(left=acorn_uri, right=axe_uri, audio=audio_uri, frame_images=frame_images)
    timing = dict(frame=1500, audio=1160)
    data = dict(uris=uris, timing=timing)
    return JsonResponse(data=data)
