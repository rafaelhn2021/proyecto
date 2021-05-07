from django.db import models

class translator_gdl_v1(models.Model):
    HORROR = 'horror'
    COMEDY = 'comedy'
    ACTION = 'action'
    DRAMA = 'drama'

    CATEGORIES_CHOICES = (
        (HORROR, 'Horror'),
        (COMEDY, 'Comedy'),
        (ACTION, 'Action'),
        (DRAMA, 'Drama'),
    )

    name = models.CharField(max_length=100)
    release_date = models.DateField()
    rating = models.IntegerField(default=0)
    category = models.CharField(max_length=10, choices=CATEGORIES_CHOICES)