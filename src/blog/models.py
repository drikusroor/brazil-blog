from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db import models
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
            self.get_children()
                .live()
                .filter(blogpage__date__lte=now)
                .order_by('-blogpage__date')
                .specific()
        )
        context['blogpages'] = blogpages
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

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('author'),
        FieldPanel('date'),
        FieldPanel('image'),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.promote_panels, heading='Promote'),
    ])

    base_form_class = BlogPageForm

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

    @classmethod
    def can_create_at(cls, parent):
        # You can only create one author page under the author index page
        return super(AuthorPage, cls).can_create_at(parent) \
               and not parent.get_children().type(cls)

class AuthorIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    def get_context(self, request):
        context = super().get_context(request)
        editor_group = Group.objects.get(name='Editors')
        authors = editor_group.user_set.filter(blog_posts__isnull=False).distinct()
        context['authors'] = authors
        return context

    subpage_types = ['AuthorPage']