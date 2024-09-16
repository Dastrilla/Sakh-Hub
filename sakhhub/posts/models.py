from django.db import models
from django.contrib.auth import get_user_model
from groups.models import Group

User = get_user_model()

class Post(models.Model):
    text = models.TextField(help_text="Текст вашей записи", verbose_name="Текст")
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
    related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, help_text="Группа публикации",
    verbose_name="Группа", related_name="posts", blank=True, null=True)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    
    def __str__(self):
        return self.text
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments",
                             blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(help_text="Напишите свой комментарий", verbose_name="Текст")
    created = models.DateTimeField("date_published", auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')