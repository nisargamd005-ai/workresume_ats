from django.contrib import admin
from .models import Job, Candidate, Application, Question

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'min_match_score', 'test_threshold', 'created_at')

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'language', 'created_at')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'status', 'match_score', 'test_score', 'created_at')
    list_filter = ('status', 'job')

admin.site.register(Question)
