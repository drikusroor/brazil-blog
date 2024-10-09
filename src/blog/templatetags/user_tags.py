from django import template
from django.utils.html import format_html
from django.contrib.auth.models import User
from easy_thumbnails.files import get_thumbnailer

register = template.Library()


@register.simple_tag
def user_display_name(user: User):
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.get_full_name():  # This will work if get_full_name is defined
        return user.get_full_name()
    elif user.username:
        return user.username
    else:
        return "Anonymous"


@register.simple_tag
def post_user_display_name(post):
    user = post.author

    # If the post doesn't have an author, we'll use the owner of the post as a fallback
    # Do we want to do this? Maybe we should just return "Anonymous"?
    if not user:
        user = post.owner

    if not user:
        return "Anonymous"

    return user_display_name(user)


def get_thumbnail_url(image, size):
    if image:
        thumbnailer = get_thumbnailer(image)
        thumbnail_options = {"size": (size, size), "crop": True}
        return thumbnailer.get_thumbnail(thumbnail_options).url
    return ""


@register.simple_tag
def get_user_avatar_url(user: User, max_size: int = 128) -> str:
    if hasattr(user, "wagtail_userprofile") and user.wagtail_userprofile.avatar:
        return get_thumbnail_url(user.wagtail_userprofile.avatar, max_size)
    return ""


@register.simple_tag
def user_avatar(
    user: User,
    classes: str = "rounded-full w-16 h-16 object-cover",
    max_size: int = 128,
) -> str:
    name = user_display_name(user)

    if hasattr(user, "wagtail_userprofile") and user.wagtail_userprofile.avatar:
        image = user.wagtail_userprofile.avatar
        max_size = (
            128  # This should be larger than the largest size you use in your CSS
        )

        # Generate URLs for full size and thumbnail
        full_url = get_thumbnail_url(image, max_size)
        thumb_url = get_thumbnail_url(image, 10)  # Tiny thumbnail for placeholder

        return format_html(
            '<img src="{}" data-src="{}" alt="{}" class="{} lazyload blur-up" title="{}"'
            ' style="filter: blur(5px); transition: filter 0.3s;"'
            " onload=\"this.style.filter='none';\">",
            thumb_url,
            full_url,
            name,
            classes,
            name,
        )
    return ""


@register.simple_tag
def post_user_avatar(post, classes: str = "rounded-full w-16 h-16 object-cover") -> str:
    user = post.author

    # If the post doesn't have an author, we'll use the owner of the post as a fallback
    # Do we want to do this? Maybe we should just return "Anonymous"?
    if not user:
        user = post.owner

    if not user:
        return ""

    return user_avatar(user, classes)
