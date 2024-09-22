# forms.py
from django import forms
from django.contrib.auth.models import User

# import wagtail user profile model
from wagtail.users.models import UserProfile


class UserProfileForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)

    # on save, the avatar should be saved into user.wagtail_userprofile.avatar
    def save(self, commit=True):
        user = super().save(commit=False)
        if not hasattr(user, "wagtail_userprofile"):
            profile = UserProfile(user=user)
        else:
            profile = user.wagtail_userprofile
        if commit:
            profile.avatar = self.cleaned_data["avatar"]
            profile.save()
            user.save()

    def get_initial_for_field(self, field, field_name):
        if field_name == "avatar":
            if (
                hasattr(self.instance, "wagtail_userprofile")
                and self.instance.wagtail_userprofile.avatar
            ):
                return self.instance.wagtail_userprofile.avatar
        return super().get_initial_for_field(field, field_name)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "avatar")
