from django.contrib import admin

from .models import Dataset, Record, Vote, Seen, ActiveDataset, AppConfig, ArchiveMap
# Register your models here.

admin.site.register(Dataset)
admin.site.register(Record)
admin.site.register(Vote)
admin.site.register(Seen)
admin.site.register(ActiveDataset)
admin.site.register(AppConfig)
admin.site.register(ArchiveMap)