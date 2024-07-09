from django.db import models


class Article(models.Model):
    """
    модель статьи блога
    """
    heading = models.CharField(max_length=100, verbose_name="Заголовок")
    body = models.TextField(verbose_name="содержимое статьи")
    image = models.ImageField(
        verbose_name="фото",
        upload_to="blog/images/",
    )
    views_amount = models.PositiveIntegerField(default=0,  verbose_name="количество просмотров")
    published_at = models.DateTimeField(auto_now=True, verbose_name="дата публикации")

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.heading
