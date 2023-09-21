from django.contrib import admin

from .models import History, Comment, Guest


class HistoryAdmin(admin.ModelAdmin):
    fields = ['user',  'title', 'modified_at', 'place']


admin.site.register(History, HistoryAdmin)
admin.site.register(Comment)
admin.site.register(Guest)