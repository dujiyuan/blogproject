# encoding:utf-8
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils.html import strip_tags
import markdown


class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Post(models.Model):
    # 文章标题
    title = models.CharField(max_length=70)
    # 文章正文，我们使用了 TextField。
    # 存储比较短的字符串可以使用 CharField，但对于文章的正文来说可能会是一大段文本，因此使用 TextField 来存储大段文本。
    body = models.TextField()
    # 这两个列分别表示文章的创建时间和最后一次修改时间，存储时间的字段用 DateTimeField 类型。
    create_time = models.DateTimeField()
    modified_time = models.DateTimeField()

    # 文章摘要，可以没有文章摘要，但默认情况下 CharField 要求我们必须存入数据，否则就会报错。
    # 指定 CharField 的 blank=True 参数值后就可以允许空值了。
    excerpt = models.CharField(max_length=200,blank=True)

    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag,blank=True)

    author = models.ForeignKey(User)

    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail',kwargs={'pk':self.pk})

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])
        #update_fields参数来告诉django只更新views字段，提高效率

    def save(self,*args,**kwargs):
        if not self.excerpt:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            self.excerpt = strip_tags(md.convert(self.body))[:54]
        super(Post,self).save(*args,**kwargs)

    def Meta(self):
        ordering = ['-create_time']

