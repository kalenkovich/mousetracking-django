from django.shortcuts import render
from django.http import HttpResponse


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
    return HttpResponse('The mousetracking will happen here')
