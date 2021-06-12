from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, blank=True,
                              null=True, related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()
    created = models.DateTimeField('Дата и время публикации',
                                   auto_now_add=True, db_index=True)

    def __str__(self):
        return self.title

    class Meta():
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(User, ondelete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')
