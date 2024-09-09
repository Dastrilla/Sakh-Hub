from django.contrib import admin

from .models import Group

class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description",)
    search_fields = ("title", "slug",)
    list_filter = ("title", "slug",)

admin.site.register(Group, GroupAdmin)