from django.db import models
from rest_framework.exceptions import ValidationError


class Author(models.Model):
    name = models.CharField(max_length=150, unique=True)
    profile_picture = models.TextField(null=True, blank=True)
    state = models.BooleanField(default=True)


class Message(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    pdf = models.TextField(null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not any([self.content, self.image, self.pdf]):
            raise ValidationError("Al menos uno de los campos (content, image, pdf) debe estar presente")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)