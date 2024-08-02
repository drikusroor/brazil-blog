from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db import models
from django.db.models import Q
from modelcluster.fields import ParentalKey

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface

from wagtail.admin.forms import WagtailAdminPageForm

from wagtail.search import index

User = get_user_model()

class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    def get_context(self, request):
        context = super().get_context(request)
        now = timezone.now()
        blogpages = (
            BlogPage.objects
            .child_of(self)
            .live()
            .filter(date__lte=now)
            .order_by('-date')
        )
        context['blogpages'] = blogpages
    
        # Author filter
        author_username = request.GET.get('author')
        if author_username:
            blogpages = blogpages.filter(Q(author__username=author_username))

        # Date filter
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')

        if date_from:
            date_from = parse_date(date_from)
            if date_from:
                blogpages = blogpages.filter(date__gte=date_from)

        if date_to:
            date_to = parse_date(date_to)
            if date_to:
                blogpages = blogpages.filter(date__lte=date_to)

        query = request.GET.get('query')
        if query:
            blogpages = blogpages.search(query, fields=['title', 'body'])

        context['blogpages'] = blogpages
        context['authors'] = User.objects.filter(blog_posts__isnull=False).distinct()
        context['page'] = self  # Add this line for the reset button

        context['active_filters'] = any([author_username, query, date_from, date_to])

        return context

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

class BlogPageForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance._state.adding:
            self.initial['author'] = self.for_user.pk

class BlogPage(Page):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_posts'
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
    video = models.URLField(null=True, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('intro'),
        index.SearchField('body'),
        index.FilterField('username'),
        index.FilterField('date'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('author'),
        FieldPanel('date'),
        FieldPanel('image'),
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('video'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.promote_panels, heading='Promote'),
    ])

    base_form_class = BlogPageForm

    def get_context(self, request):
        context = super().get_context(request)

        preview_url = self.video

        # Transform google drive share url to preview url for embedding
        if 'drive.google' in self.video :
            preview_url = (self.video.replace("view?usp=sharing","preview"))

        context['preview_url'] = preview_url

        return context

class Comment(models.Model):
    post = models.ForeignKey(BlogPage, on_delete=models.CASCADE, related_name='comments')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    body = models.TextField()
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['created_date']

    def __str__(self):
        return self.body

class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]


class AuthorPage(Page):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_page')
    bio = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('user'),
        FieldPanel('bio'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['posts'] = self.user.blog_posts.live().order_by('-first_published_at')
        return context

    parent_page_types = ['AuthorIndexPage']

class AuthorIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # Fetch all users who have the role of "Authors"
        authors = User.objects.filter(groups__name='Authors')
        context['authors'] = authors
        return context

    subpage_types = ['AuthorPage']