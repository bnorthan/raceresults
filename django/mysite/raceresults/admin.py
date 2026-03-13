from django.contrib import admin
from .models import Result, Race, Runner

# Register your models here.
admin.site.register(Result)
#admin.site.register(Race)
admin.site.register(Runner)

class RaceAdmin(admin.ModelAdmin):
    list_display = ('race_name', 'id')

admin.site.register(Race, RaceAdmin)
