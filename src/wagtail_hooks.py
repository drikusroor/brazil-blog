from wagtail import hooks

from notifications.models import Notification
from blog.models import Subscription


# after publishing page
@hooks.register("after_publish_page")
def after_publish_page(request, page):
    # page author
    author = page.author

    # get all subscriptions for the page author
    subscriptions = Subscription.objects.filter(author=author)

    # create notification for each subscription
    for subscription in subscriptions:
        Notification.objects.create(
            user=subscription.subscriber,
            title=f"New post published: {page.title}",
            url=page.get_url(),
        )
