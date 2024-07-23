from django import template
from django.utils.html import format_html
from blog.models import BlogPage
from django.contrib.auth.models import User

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
def post_user_display_name(post: BlogPage):
    user = post.author
    
    # If the post doesn't have an author, we'll use the owner of the post as a fallback
    # Do we want to do this? Maybe we should just return "Anonymous"?
    if not user:
        user = post.owner

    if not user:
        return "Anonymous"
    
    return user_display_name(user)

@register.simple_tag
def get_user_avatar_url(user: User) -> str:
    if hasattr(user, 'wagtail_userprofile') and user.wagtail_userprofile.avatar:
        return user.wagtail_userprofile.avatar.url
    return ''

@register.simple_tag
def user_avatar(user: User, classes: str = 'rounded-full w-16 h-16 object-cover') -> str:
    if hasattr(user, 'wagtail_userprofile') and user.wagtail_userprofile.avatar:
        return format_html('<img src="{}" alt="{}" class="{}">', 
                           user.wagtail_userprofile.avatar.url, 
                           user_display_name(user), 
                           classes, 
                           )
    return ''
    
@register.simple_tag
def post_user_avatar(post: BlogPage, classes: str = 'rounded-full w-16 h-16 object-cover') -> str:

    user = post.author
    
    # If the post doesn't have an author, we'll use the owner of the post as a fallback
    # Do we want to do this? Maybe we should just return "Anonymous"?
    if not user:
        user = post.owner

    if not user:
        return ''
    
    return user_avatar(user, classes)
