from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, reverse
from .forms import UserProfileForm
from django.contrib.auth.models import User
from blog.templatetags.user_tags import user_display_name, get_user_avatar_url


def profile(request, username):
    # get user object
    user = User.objects.get(username=username)

    # get user profile
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name

    # attach user profile to context
    context = {
        "username": username,
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "display_name": user_display_name(user),
        "avatar": get_user_avatar_url(user),
    }

    return render(request, "profile.html", context)


@login_required
def edit_profile(request, username):
    user = User.objects.get(username=username)

    # if the user is not the owner of the profile, redirect to the profile page
    if request.user != user:
        raise PermissionDenied()

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse("profile", args=[username]))
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "edit_profile.html", {"form": form})
