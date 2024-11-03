from django.contrib import admin
from .models import Profile, Project, Task, Document, Comment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'contact_number')
    search_fields = ('user__username', 'role')
    
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date')
    search_fields = ('title',)
    list_filter = ('start_date', 'end_date')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'project', 'assignee', 'created_at')
    search_fields = ('title', 'project__title')
    list_filter = ('status', 'project', 'assignee')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'project', 'uploaded_at')
    search_fields = ('name', 'project__title')
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'created_at', 'task', 'project')
    search_fields = ('author__username', 'text')
    list_filter = ('task', 'project')