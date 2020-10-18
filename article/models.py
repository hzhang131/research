from django.db import models

# Create your models here.
class Article(models.Model):
    submitter = models.CharField(max_length=100)
    authors = models.TextField()
    title = models.TextField()
    abstract = models.TextField()
    categories = models.CharField(max_length=100)
    update_date = models.CharField(max_length=100)

class Related(models.Model):
    title = models.TextField()
    abstract = models.TextField()

    
