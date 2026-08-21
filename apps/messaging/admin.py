from django.contrib import admin
from .models import Conversation, Message, Rating


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'body', 'created_at', 'read']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['report', 'claimant', 'created_at', 'ownership_verified']
    inlines = [MessageInline]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['rater', 'ratee', 'stars', 'created_at']
    readonly_fields = ['conversation', 'rater', 'ratee', 'stars', 'comment', 'created_at']
