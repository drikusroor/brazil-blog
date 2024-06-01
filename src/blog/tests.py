import datetime
from django.test import TestCase
from django.utils import timezone
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from blog.models import BlogIndexPage, BlogPage, Comment
from django.contrib.auth.models import User

class BlogIndexPageTests(WagtailPageTestCase):
    
    @classmethod
    def setUpTestData(self):
        root = Page.get_first_root_node()
        Site.objects.create(
            hostname="testserver",
            root_page=root,
            is_default_site=True,
            site_name="testserver",
        )
        self.blog_index_page = BlogIndexPage(title="Knalvis", slug="snorkel")
        root.add_child(instance=self.blog_index_page)

    def test_blog_index_page_context(self):
        now = timezone.now()
        past_date = now - datetime.timedelta(days=1)
        future_date = now + datetime.timedelta(days=1)

        past_post = BlogPage(
            title="Past Post", 
            slug="past-post", 
            date=past_date, 
            intro="Past intro", 
            body="Past body"
        )
        future_post = BlogPage(
            title="Future Post", 
            slug="future-post", 
            date=future_date, 
            intro="Future intro", 
            body="Future body"
        )

        self.blog_index_page.add_child(instance=past_post)
        self.blog_index_page.add_child(instance=future_post)

        response = self.client.get(self.blog_index_page.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_post.title)
        self.assertNotContains(response, future_post.title)

        self.assertPageIsRoutable(self.blog_index_page)
        self.assertPageIsRoutable(past_post)
        self.assertPageIsRoutable(future_post)

class BlogPageTests(TestCase):
    def setUp(self):
        self.root_page = Page.objects.get(id=1)
        self.blog_index_page = BlogIndexPage(title="Blog", slug="blog")
        self.root_page.add_child(instance=self.blog_index_page)
        self.blog_index_page.save()

        self.blog_page = BlogPage(
            title="Test Post",
            slug="test-post",
            date=timezone.now(),
            intro="Test intro",
            body="Test body"
        )
        self.blog_index_page.add_child(instance=self.blog_page)
        self.blog_page.save()

    def test_blog_page_creation(self):
        self.assertEqual(BlogPage.objects.count(), 1)
        self.assertEqual(self.blog_page.title, "Test Post")

class CommentTests(TestCase):
    def setUp(self):
        self.root_page = Page.objects.get(id=1)
        self.blog_index_page = BlogIndexPage(title="Blog", slug="blog")
        self.root_page.add_child(instance=self.blog_index_page)
        self.blog_index_page.save()

        self.blog_page = BlogPage(
            title="Test Post",
            slug="test-post",
            date=timezone.now(),
            intro="Test intro",
            body="Test body"
        )
        self.blog_index_page.add_child(instance=self.blog_page)
        self.blog_page.save()

        self.user = User.objects.create_user(username='testuser', password='password')

    def test_comment_creation(self):
        comment = Comment.objects.create(
            post=self.blog_page,
            author=self.user,
            body="Test comment"
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.body, "Test comment")

    def test_comment_reply(self):
        comment = Comment.objects.create(
            post=self.blog_page,
            author=self.user,
            body="Test comment"
        )
        reply = Comment.objects.create(
            post=self.blog_page,
            author=self.user,
            body="Test reply",
            parent_comment=comment
        )
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(reply.body, "Test reply")
        self.assertEqual(reply.parent_comment, comment)
