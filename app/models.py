from django.db import models

# Create your models here.
class Author(models.Model):
    name=models.CharField(max_length=150, unique=True)

class Message(models.Model):
    author=models.ForeignKey(Author, on_delete=models.CASCADE)
    content=models.TextField()
    create_at=models.DateTimeField(auto_now_add=True)