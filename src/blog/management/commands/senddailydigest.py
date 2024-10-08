# blog/management/commands/send_daily_digest.py

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.template.loader import render_to_string
from blog.models import BlogPage
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends daily digest emails to subscribers"

    def add_arguments(self, parser):
        parser.add_argument(
            "--subscribers",
            nargs="+",
            type=int,
            help="Specific subscriber IDs to send emails to",
        )

    def handle(self, *args, **options):
        yesterday = timezone.now().date() - timezone.timedelta(days=1)

        subscriber_ids = options.get("subscribers")
        if subscriber_ids:
            subscribers = User.objects.filter(
                id__in=subscriber_ids, subscriptions__isnull=False
            ).distinct()
        else:
            subscribers = User.objects.filter(subscriptions__isnull=False).distinct()

        emails = []
        for subscriber in subscribers:
            subscribed_authors = subscriber.subscriptions.values_list(
                "author", flat=True
            )
            new_posts = (
                BlogPage.objects.live()
                .filter(author__in=subscribed_authors, date__gte=yesterday)
                .select_related("author")
            )

            if new_posts:
                context = {
                    "subscriber": subscriber,
                    "new_posts": new_posts,
                }
                subject = (
                    f"Er zijn nieuwe tropische verrassingen voor jou ({yesterday})"
                )
                message = render_to_string("blog/email/daily_digest.txt", context)
                html_message = render_to_string("blog/email/daily_digest.html", context)
                emails.append((subject, message, html_message, subscriber.email))
            else:
                logger.info(f"No new posts for {subscriber}")

        if emails:
            self.send_mass_html_mail(emails)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully processed {len(emails)} digest emails"
                )
            )
        else:
            logger.info("No digest emails to send")
            self.stdout.write(self.style.SUCCESS("No digest emails to send"))

    def send_mass_html_mail(self, email_data):
        try:
            backend = EmailBackend(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
                fail_silently=False,
                timeout=30,
            )

            if not backend.open():
                logger.error("Failed to open email backend connection")
                return

            from_email = "noreply@tropischeverrassing.fun"
            batch_size = 5
            total_sent = 0

            for i in range(0, len(email_data), batch_size):
                batch = email_data[i : i + batch_size]
                messages = []

                for subject, text_content, html_content, to_email in batch:
                    message = EmailMultiAlternatives(
                        subject, text_content, from_email, [to_email]
                    )
                    message.attach_alternative(html_content, "text/html")
                    messages.append(message)

                try:
                    sent = backend.send_messages(messages)
                    total_sent += sent
                    logger.info(f"Sent batch of {sent} emails")
                except Exception as e:
                    logger.error(f"Error sending batch: {e}")

                # Close and reopen connection for each batch
                backend.close()
                if not backend.open():
                    logger.error("Failed to reopen email backend connection")
                    break

            logger.info(f"Total emails sent: {total_sent}")
            self.stdout.write(
                self.style.SUCCESS(f"Successfully sent {total_sent} digest emails")
            )

        except Exception as e:
            logger.error(f"Error in send_mass_html_mail: {e}")
            self.stdout.write(self.style.ERROR(f"Error sending digest emails: {e}"))

        finally:
            if backend:
                backend.close()
