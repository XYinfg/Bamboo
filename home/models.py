from django.db import models

class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField(upload_to='uploads/')
    content_summary = models.TextField(blank=True)
    wordcloud = models.ImageField(upload_to='wordclouds/', blank=True)
    # Add other fields for analytics as needed
# Create your models here.
