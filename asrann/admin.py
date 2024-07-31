from django.contrib import admin

from .models import Dataset, Record, Vote, ActiveDataset, AppConfig, ArchiveMap, CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# Register your models here.

class UserCustomInline(admin.StackedInline):
    model = CustomUser
    can_delete = False
    verbose_name_plural = "customuser"

class UserAdmin(BaseUserAdmin):
    inlines = [UserCustomInline]

class VoteAdmin(admin.ModelAdmin):
    raw_id_fields = ['record', 'added_by']


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Dataset)
admin.site.register(Record)
admin.site.register(Vote, VoteAdmin)
admin.site.register(ActiveDataset)
admin.site.register(AppConfig)
admin.site.register(ArchiveMap)