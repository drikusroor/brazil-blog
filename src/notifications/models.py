from django.db import models


# Create your models here.
class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(blank=True)
    read = models.BooleanField(default=False)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    def __str__(self):
        return self.title
