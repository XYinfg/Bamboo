from django.db import models
import os

class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField(upload_to='uploads/')
    content_summary = models.TextField(blank=True)
    wordcloud = models.ImageField(upload_to='wordclouds/', blank=True)
    word_freq = models.ImageField(upload_to='word_freqs/', null=True, blank=True)
    gpt_questions = models.TextField(null=True ,blank=True)
    # Add other fields for analytics as needed
    def delete(self, *args, **kwargs):
        # Delete the uploaded document
        if self.upload:
            if os.path.isfile(self.upload.path):
                os.remove(self.upload.path)

        # Delete the wordcloud image
        if self.wordcloud:
            if os.path.isfile(self.wordcloud.path):
                os.remove(self.wordcloud.path)

        # Delete the model instance
        super().delete(*args, **kwargs)
