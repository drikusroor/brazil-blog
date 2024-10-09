# In your games/views.py file

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from .models import Score
from django.shortcuts import render


def frogger(request):
    return render(request, "games/frogger.html")


@require_POST
@login_required
@ensure_csrf_cookie
def submit_score(request):
    score = request.POST.get("score")
    if score is not None:
        Score.objects.create(player=request.user, score=int(score))
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid score"}, status=400)
