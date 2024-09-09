from django.db import models

class Group(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=300)

    def __str__(self):
        return self.title