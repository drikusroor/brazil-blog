# blog/models.py

import logging
from itertools import groupby
from django.utils import translation

from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django import forms
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db.models.functions import Cast
from modelcluster.fields import ParentalKey
from django.db.models import DateField
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    ObjectList,
    TabbedInterface,
    FieldRowPanel,
)
from wagtail.snippets.models import register_snippet
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.search import index

from locations.forms import MapPickerWidget
from locations.models import Itinerary

from .templatetags.user_tags import user_display_name

logger = logging.getLogger(__name__)


User = get_user_model()


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    def get_context(self, request):
        context = super().get_context(request)
        now = timezone.now()
        blogpages = (
            BlogPage.objects.child_of(self)
            .live()
            .filter(date__lte=now)
            .order_by("-date")
            .prefetch_related("location")
            .annotate(date_only=Cast("date", DateField()))
        )
        context["blogpages"] = blogpages

        # Author filter
        author_username = request.GET.get("author")
        if author_username:
            blogpages = blogpages.filter(Q(author__username=author_username))

        # Date filter
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")

        if date_from:
            date_from = parse_date(date_from)
            if date_from:
                blogpages = blogpages.filter(date__gte=date_from)

        if date_to:
            date_to = parse_date(date_to)
            if date_to:
                blogpages = blogpages.filter(date__lte=date_to)

        query = request.GET.get("query")
        if query:
            blogpages = blogpages.search(query, fields=["title", "body"])

        context["blogpages"] = blogpages
        context["authors"] = User.objects.filter(blog_posts__isnull=False).distinct()
        context["page"] = self  # Add this line for the reset button

        context["active_filters"] = any([author_username, query, date_from, date_to])

        # Group blog posts by date
        grouped_posts = {}
        for date, posts in groupby(blogpages, key=lambda x: x.date_only):
            grouped_posts[date] = list(posts)

        context["grouped_blog_posts"] = grouped_posts

        itinerary = Itinerary.objects.first()

        if itinerary:
            context["itinerary"] = {
                "id": itinerary.id,
                "name": itinerary.name,
                "description": itinerary.description,
                "stops": itinerary.serialize_stops(),
            }

        return context

    content_panels = Page.content_panels + [FieldPanel("intro")]

    subpage_types = ["BlogPage"]


class BlogPageForm(WagtailAdminPageForm):
    map_location = forms.CharField(
        widget=MapPickerWidget(
            attrs={
                "placeholder": "Click on the map to select a location",
                "latitude_field_name": "latitude",
                "longitude_field_name": "longitude",
                "model_name": "location",
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance._state.adding:
            self.initial["author"] = self.for_user.pk

        if self.instance and self.instance.location.exists():
            location = self.instance.location.first()

            self.fields[
                "map_location"
            ].initial = f"{location.latitude},{location.longitude}"

    def clean(self):
        super().clean()

        if self.instance.location.count() > 1:
            raise ValidationError("Only one location can be added to a blog page.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        map_location = self.cleaned_data.get("map_location")
        location = instance.location.first()
        if location and map_location:
            lat, lon = map_location.split(",")
            location.latitude = float(lat)
            location.longitude = float(lon)
        if commit:
            location.save()
        return instance

    class Media:
        js = ["js/location_limiter.js"]


class BlogPage(Page):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="blog_posts"
    )
    date = models.DateTimeField("Post date", default=timezone.now)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Blog featured image",
    )
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    video = models.URLField(null=True, blank=True, help_text="Google drive share link")
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("title"),
        index.SearchField("intro"),
        index.SearchField("body"),
        index.FilterField("username"),
        index.FilterField("date"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("author"),
        FieldPanel("date"),
        FieldPanel("image"),
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("video"),
        InlinePanel("gallery_images", label="Gallery images"),
    ]

    location_panels = [
        FieldRowPanel(
            children=[
                InlinePanel("location", label="Location", min_num=1, max_num=1),
                FieldPanel("map_location"),
            ]
        )
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(location_panels, heading="Location"),
            ObjectList(Page.promote_panels, heading="Promote"),
        ]
    )

    base_form_class = BlogPageForm

    def get_context(self, request):
        context = super().get_context(request)

        if request.user.is_authenticated:
            context["is_subscribed"] = Subscription.objects.filter(
                subscriber=request.user, author=self.author
            ).exists()

        if self.video:
            preview_url = self.video

            # Transform google drive share url to preview url for embedding
            if "drive.google" in self.video:
                preview_url = self.video.replace("view?usp=sharing", "preview")

            context["preview_url"] = preview_url

        return context

    def like_toggle(self, user):
        if user in self.likes.all():
            self.likes.remove(user)
            return False
        else:
            self.likes.add(user)
            return True

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def liked_by(self):
        return [user_display_name(user) for user in self.likes.all()]


@register_snippet
class Comment(models.Model):
    post = models.ForeignKey(
        BlogPage, on_delete=models.CASCADE, related_name="comments"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    body = models.TextField()
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    likes = models.ManyToManyField(User, related_name="liked_comments", blank=True)

    class Meta:
        ordering = ["created_date"]

    def __str__(self):
        return self.body

    @property
    def like_count(self):
        return self.likes.count()

    def like_toggle(self, user):
        if user in self.likes.all():
            self.likes.remove(user)
            return False
        else:
            self.likes.add(user)
            return True

    @property
    def liked_by(self):
        return [user_display_name(user) for user in self.likes.all()]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(
        BlogPage, on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+"
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]


class AuthorPage(Page):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="author_page"
    )
    bio = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("user"),
        FieldPanel("bio"),
    ]

    def get_context(self, request):
        now = timezone.now()
        context = super().get_context(request)
        context["posts"] = (
            self.user.blog_posts.live().filter(date__lte=now).order_by("-date")
        )

        if request.user.is_authenticated:
            context["is_subscribed"] = Subscription.objects.filter(
                subscriber=request.user, author=self.user
            ).exists()

        return context

    parent_page_types = ["AuthorIndexPage"]


class AuthorIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]

    def get_context(self, request):
        context = super().get_context(request)

        # authors are the users for which an AuthorPage has been created under AuthorIndexPage
        authors = [
            author_page.user for author_page in self.get_children().live().specific()
        ]

        context["authors"] = authors
        return context

    subpage_types = ["AuthorPage"]


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    list_display = ["subscriber", "author", "created_at", "send_test_email"]

    class Meta:
        unique_together = ("subscriber", "author")

    def send_test_email_button(self):
        obj = Subscription.objects.get(id=self.id)

        return format_html(
            '<button class="button button-small" onclick="sendTestEmail({})">Send Test Email</button>',
            obj.id,
        )

    def send_daily_digest_email_button(self):
        return format_html(
            '<button class="button button-small" onclick="sendDailyDigestEmail()">Send Daily Digest Email</button>'
        )

    send_test_email_button.short_description = "Send Test Email"
    send_daily_digest_email_button.short_description = "Send Daily Digest Email"

    def send_test_email(self, request, subscription_id):
        subscription = Subscription.objects.get(id=subscription_id)

        try:
            backend = EmailBackend(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
                fail_silently=False,
                timeout=10,
            )

            if backend.open():
                logger.info("Email backend opened successfully")
            else:
                logger.error("Email backend failed to open")
                return "Error: Email backend failed to open"

            num_sent = send_mail(
                "Test email",
                f"This is a test email from {subscription.author.username} to {subscription.subscriber.username}",
                "noreply@tropischeverrassing.fun",
                [subscription.subscriber.email],
                fail_silently=False,
                connection=backend,
            )

            if num_sent >= 1:
                message = "Email sent successfully"
                logger.info(message)
            else:
                message = "Error: Email not sent"
                logger.error(message)

        except Exception as e:
            logger.error(f"Error sending test email: {e}")
            message = f"Error: {e}"

        finally:
            if backend:
                backend.close()

        return message

    def __str__(self):
        return f"{self.subscriber.username} subscribed to {self.author.username}"
