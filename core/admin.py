from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Task

# --- 1. Custom User Admin for Inline Profile Editing ---

class ProfileInline(admin.StackedInline):
    """
    Allows the Profile to be edited directly from the User administration page.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    
class UserAdmin(BaseUserAdmin):
    """
    Extends the default Django User admin to include the Profile inline.
    """
    inlines = (ProfileInline,)

# Re-register the User model
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- 2. Task Model Registration ---

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Customizes the display of the Task model in the admin interface.
    """
    list_display = ('title', 'assigned_to', 'status', 'priority', 'due_date', 'created_by', 'is_overdue')
    
    list_filter = ('status', 'priority', 'assigned_to', 'created_at', 'due_date')
    
    search_fields = ('title', 'description', 'assigned_to__username')
    
    date_hierarchy = 'created_at' # Allows navigating by date
    
    # Fields to display when creating or editing a task
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Assignment Details', {
            'fields': ('assigned_to', 'created_by', 'due_date'),
        }),
        ('Status and Priority', {
            'fields': ('status', 'priority'),
            'classes': ('collapse',), # Optional: collapse this section by default
        }),
    )
    
    # Automatically set the 'created_by' field when saving a new task
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        
    # Prevent 'created_by' field from being editable via the form, 
    # but still show it.
    readonly_fields = ('created_by',)
    
    # Custom method to check if the task is overdue (requires import)
    def is_overdue(self, obj):
        from django.utils import timezone
        if obj.due_date and obj.status != 'DONE':
            return obj.due_date < timezone.now()
        return False
    
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'


# --- 3. Profile Model Registration (Optional) ---

# We already handle Profile via the inline above, but you can register it separately if needed:
# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'full_name', 'phone')
#     search_fields = ('user__username', 'full_name')