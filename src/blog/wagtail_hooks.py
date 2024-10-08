from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Subscription

from notifications.models import Notification

from blog.templatetags.user_tags import user_display_name


def after_publish_blog_page(request, page):
    # page author
    author = page.author

    # get all subscriptions for the page author
    subscriptions = Subscription.objects.filter(author=author)

    user_name = user_display_name(author)

    # create notification for each subscription
    for subscription in subscriptions:
        Notification.objects.create(
            user=subscription.subscriber,
            title=f"New post published: {page.title}",
            message=f"Your subscription to {user_name} has a new post: {page.title}",
            url=page.get_url(),
        )


# after publishing page
@hooks.register("after_publish_page")
def after_publish_page(request, page):
    if page.__class__.__name__ == "BlogPage":
        after_publish_blog_page(request, page)


class SubscriptionViewSet(SnippetViewSet):
    model = Subscription
    icon = "user"
    list_display = [
        "subscriber",
        "author",
        "created_at",
        "send_test_email_button",
        "send_daily_digest_email_button",
    ]
    inline_actions = ["send_test_email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


register_snippet(Subscription, viewset=SubscriptionViewSet)
