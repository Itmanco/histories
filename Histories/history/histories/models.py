import os
from django.db import models
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField
from PIL import Image
from io import BytesIO
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

from django.utils import timezone

User = get_user_model()


class History(models.Model):
    title = models.CharField(max_length=100,  null=False, blank=True, default="")
    user = models.ForeignKey(User, related_name='storiestold', on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    description = RichTextField(blank=True, null=True)
    place = models.CharField(max_length=200)
    n_images = models.IntegerField(default=0)

    def update(self, *args, **kwargs):
        self.modified_at = timezone.now()
        super(History, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.created_at = timezone.now()
        self.modified_at = timezone.now()
        super(History, self).save(*args, **kwargs)

    def __str__(self):
        return f"title:{self.title}, creation:{self.created_at.strftime('%Y/%m/%d[%H:%M:%S]')}, by:{self.user.username}, images:{self.n_images}, "

    def get_absolute_url(self):
        return reverse('histories:history_detail', kwargs={'pk': self.pk})

    def delete(self, *args, **kwargs):
        for local in self.comments.all():
            local.delete()
        print('Delete History Model')
        return super().delete(*args, **kwargs)


class Guest(models.Model):
    user = models.ForeignKey(User, related_name='guests', on_delete=models.CASCADE)
    history = models.ForeignKey(History, related_name='guestsbyhistory', on_delete=models.CASCADE)
    """
        Permit_level have 3 levels for a guest:
        R = Can watch pictures and read comments
        C = R + can create comments about pictures
        I = C + can add new pictures.
    """
    permit_level = models.CharField(max_length=1, verbose_name="Permitir:",  null=False, blank=False, default="R")

    def __str__(self):
        level = "Permitir: Ver fotos y leer comentarios."
        match self.permit_level:
            case "C":
                level = "Permitir: Ver fotos y crear comentarios."
            case "I":
                level = "Permitir: Ver y agregar fotos y comentarios."

        return self.user.username + "\n"+level

    def get_level_description(self):
        level = "Visitar."
        match self.permit_level:
            case "C":
                level = "Visitar, Comentar."
            case "I":
                level = "Visitar, comentar, agregar fotos."

        return level

    def get_absolute_url(self):
        print(self.pk)
        return reverse('histories:history_guests', kwargs={'hpk': self.history.pk})

    class Meta:
        unique_together = ('user', 'history')

class Comment(models.Model):
    title = models.CharField(max_length=100,  null=False, blank=True, default="", verbose_name="Titulo")
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    description = RichTextField(blank=True, null=True, verbose_name="")
    history = models.ForeignKey(History, related_name='comments', null=True, blank=True, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images", null=False, verbose_name="Imagen")

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        loc_history = History.objects.get(pk=self.history.pk)
        print("delete--> n_images")
        print(loc_history.n_images)
        loc_history.n_images = loc_history.n_images-1
        loc_history.save()
        if self.image:
            print('delete was called with in model')
            imageloc = self.image.path
            if os.path.isfile(imageloc):
                os.remove(imageloc)
        return super().delete(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.modified_at = timezone.now()
        super(Comment, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        try:
            if not self.id and self.image:
                print("doing image compression..")
                self.image = self.compressImage(uploadedimage=self.image)
        except:
            print("there is a problem with the uploaded image,")
            print(sys.exc_info())

        self.created_at = timezone.now()
        self.modified_at = timezone.now()
        super(Comment, self).save(*args, **kwargs)

    def compressImage(self, uploadedimage):
        imagetemporary = Image.open(uploadedimage)
        outputIoStream = BytesIO()
        imageTemproaryResized = imagetemporary.resize((1020, 573))
        imagetemporary.save(outputIoStream, format='JPEG', quality=60)
        outputIoStream.seek(0)
        uploadedImage = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % uploadedimage.name.split('.')[0],
                                             'image/jpeg', sys.getsizeof(outputIoStream), None)
        return uploadedImage

    def get_absolute_url(self):
        print("Inside-->reverse Comment!!")
        print(self.history.pk)
        return reverse('histories:comment_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']
        # unique_together = ['user', 'description']
