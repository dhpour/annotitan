from django.contrib import admin

from .models import Dataset, Record, Vote, Seen, ActiveDataset, AppConfig, ArchiveMap, CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# Register your models here.

class UserCustomInline(admin.StackedInline):
    model = CustomUser
    can_delete = False
    verbose_name_plural = "customuser"

class UserAdmin(BaseUserAdmin):
    inlines = [UserCustomInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Dataset)
admin.site.register(Record)
admin.site.register(Vote)
admin.site.register(Seen)
admin.site.register(ActiveDataset)
admin.site.register(AppConfig)
admin.site.register(ArchiveMap)