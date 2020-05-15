from django.shortcuts import render
from django.http import HttpResponse


def router(request):
    """
    This view routes to all the other ones depending on the stage the participant is at
    """
    return welcome(request)


def welcome(request):
    return HttpResponse('Welcome!')
