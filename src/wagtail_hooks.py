from wagtail import hooks

from notifications.models import Notification


# after publishing page
@hooks.register("after_publish_page")
def after_publish_page(request, page):
    pass
