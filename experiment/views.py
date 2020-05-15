from django.shortcuts import render


def router(request):
    """
    This view routes to all the other ones depending on the stage the participant is at
    """
    return welcome(request)


def welcome(request):
    return render(request, 'experiment/welcome.html')
