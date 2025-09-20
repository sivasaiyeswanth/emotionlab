# study/admin.py
from django.contrib import admin
from .models import Clip, ParticipantProfile, ClipResponse, ClipQuestion

@admin.register(Clip)
class ClipAdmin(admin.ModelAdmin):
    list_display = ('title', 'order_index')
    ordering = ('order_index', 'title')

@admin.register(ParticipantProfile)
class ParticipantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')

@admin.register(ClipResponse)
class ClipResponseAdmin(admin.ModelAdmin):
    list_display = ('participant', 'clip', 'created_at')
    list_filter = ('clip',)

@admin.register(ClipQuestion)
class ClipQuestionAdmin(admin.ModelAdmin):
    list_display = ('code', 'response_type')