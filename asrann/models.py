import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
import uuid

class Dataset(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    
    gzip = "gzip"
    zip = "zip"
    tar = "tar"
    rar = "rar"
    bzip = "bzip2"
    wim = "wim"
    xz = "xz"
    sevenz = "7z"
    none = "none"
    COMPRESSED_TYPES = {
        gzip: "gzip",
        zip: "zip",
        tar: "tar",
        rar: "rar",
        bzip: "bzip2",
        wim: "wim",
        xz: "xz",
        sevenz: "7z",
        none: "none"
    }
    name = models.CharField(max_length=200, default="unknown")
    version = models.CharField(max_length=50, default="0.1.0")
    data_folder = models.CharField(max_length=200, default=".")
    add_date = models.DateTimeField("date added")
    added_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    is_compressed = models.CharField(default="none", max_length=5, choices=COMPRESSED_TYPES)
    def __str__(self):
        return self.name


class Record(models.Model):
    id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    audio_file = models.CharField(max_length=200)
    transcription = models.TextField()

    add_date = models.DateTimeField("date added", default=timezone.now)
    #added_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.audio_file

class Vote(models.Model):
    class VoteChoices(models.IntegerChoices):
        up = 1
        down = -1
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.IntegerField(choices=VoteChoices)
    vote_date = models.DateTimeField("date voted")
    def __str__(self):
        user_vote = "UP" if self.vote == 1 else "DOWN"
        return "Vote " + " on " + self.record.audio_file + " (" + self.record.dataset.name + ") by " + self.added_by.username + ", " + user_vote

@receiver(post_save, sender=Vote)
def update_record_score(sender, instance, created, **kwargs):
    record = instance.record
    record_score = abs(Vote.objects.filter(record=record).aggregate(Sum('vote'))['vote__sum'])
    Record.objects.filter(id=record.id).update(score = record_score)
    print(sender)
    print('instance:', record)
    print('score: ', record_score)

class Seen(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    seen_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    count = models.IntegerField(default=0)

class ArchiveMap(models.Model):
    tar_file = models.SmallIntegerField()
    audio_file = models.CharField(max_length=50)
    dataset = models.ForeignKey(Dataset, on_delete=models.DO_NOTHING)

class ActiveDataset(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.DO_NOTHING)
    def __str__(self):
        return self.dataset.name

class AppConfig(models.Model):
    autoplay = models.BooleanField(default=True)