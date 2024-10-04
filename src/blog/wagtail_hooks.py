from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Subscription


class SubscriptionViewSet(SnippetViewSet):
    model = Subscription
    icon = "user"
    list_display = ["subscriber", "author", "created_at", "send_test_email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


register_snippet(Subscription, viewset=SubscriptionViewSet)
