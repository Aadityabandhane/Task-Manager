from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _ # New Import for better choices

# --- Profile Model ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    
    # 💡 Improvement: Add related_name to the OneToOneField
    # This isn't strictly necessary but is good practice to prevent future conflicts
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        # 💡 Improvement: Return the full name if set, otherwise the username
        return self.full_name or self.user.username


# --- Task Model ---
class Task(models.Model):
    # 💡 Improvement 1: Use gettext_lazy (_) for choice labels
    class Status(models.TextChoices):
        TODO = 'TODO', _('To Do')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        DONE = 'DONE', _('Done')
        BLOCKED = 'BLOCKED', _('Blocked')
    
    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')
        CRITICAL = 'CRITICAL', _('Critical')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_assigned')
    # 💡 Improvement 2: related_name for created_by should be tasks_created_by to be clearer
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tasks_created_by') 
    
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, # Use new TextChoices
        default=Status.TODO
    )
    priority = models.CharField(
        max_length=20, 
        choices=Priority.choices, # Use new TextChoices
        default=Priority.MEDIUM
    )
    due_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'due_date', 'status']
        verbose_name_plural = "Tasks" # Good practice for Admin readability

    def __str__(self):
        return f"Task: {self.title} assigned to {self.assigned_to.username}" # More informative