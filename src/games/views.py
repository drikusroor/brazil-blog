from django.shortcuts import render


def frogger(request):
    return render(request, "games/frogger.html")
