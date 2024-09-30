# blog/management/commands/send_daily_digest.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mass_mail
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from blog.models import Subscription, BlogPage
from django.contrib.auth import get_user_model
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives

User = get_user_model()


class Command(BaseCommand):
    help = "Sends daily digest emails to subscribers"

    def handle(self, *args, **options):
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        site = Site.objects.get_current()

        emails = []
        for subscriber in User.objects.filter(subscriptions__isnull=False).distinct():
            subscribed_authors = subscriber.subscriptions.values_list(
                "author", flat=True
            )
            new_posts = (
                BlogPage.objects.live()
                .filter(author__in=subscribed_authors, date__date=yesterday)
                .select_related("author")
            )

            if new_posts:
                context = {
                    "subscriber": subscriber,
                    "new_posts": new_posts,
                    "site": site,
                }
                subject = f"Your Daily Digest for {yesterday}"
                message = render_to_string("blog/email/daily_digest.txt", context)
                html_message = render_to_string("blog/email/daily_digest.html", context)
                emails.append(
                    (
                        subject,
                        message,
                        html_message,
                        "noreply@brazil.kokokoding.nl",
                        [subscriber.email],
                    )
                )

        if emails:
            self.send_mass_html_mail(emails, fail_silently=False)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully sent {len(emails)} digest emails")
            )

        else:
            self.stdout.write(self.style.SUCCESS("No digest emails to send"))

    def send_mass_html_mail(
        datatuple, fail_silently=False, auth_user=None, auth_password=None
    ):
        """
        Given a datatuple of (subject, text_content, html_content, from_email, recipient_list),
        sends each message to each recipient list.
        """
        connection = get_connection(
            fail_silently=fail_silently, username=auth_user, password=auth_password
        )

        messages = []
        for (
            subject,
            text_content,
            html_content,
            from_email,
            recipient_list,
        ) in datatuple:
            message = EmailMultiAlternatives(
                subject, text_content, from_email, recipient_list
            )
            message.attach_alternative(html_content, "text/html")
            messages.append(message)

        return connection.send_messages(messages)
