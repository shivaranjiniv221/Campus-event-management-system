from django.contrib import admin
from .models import Event, RSVP, Review, StudentProfile, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date', 'location', 'rsvp_count', 'capacity', 'organizer')
    list_filter = ('category', 'date')
    search_fields = ('title', 'description', 'location')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'event', 'department', 'year', 'student_id', 'registered_at')
    list_filter = ('event', 'department', 'year')
    search_fields = ('full_name', 'email', 'student_id', 'event__title')
    readonly_fields = ('registered_at',)


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'timestamp')
    list_filter = ('event',)
    search_fields = ('user__username', 'event__title')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'rating', 'created_at')
    list_filter = ('rating', 'event')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'department', 'year', 'phone')
    list_filter = ('department', 'year')
    search_fields = ('user__username', 'student_id')
