from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import SignUpForm, ProfileUpdateForm, TaskForm
from .models import Profile, Task
from django import forms # Needed for forms.HiddenInput

# --- General Views ---

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            Profile.objects.create(user=user)
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

# --- User & Profile Views ---

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def profile(request):
    profile = request.user.profile
    return render(request, "profile.html", {"profile": profile})

@login_required
def settings_page(request):
    profile = request.user.profile
    
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, "settings.html", {"form": form})

# --- Task Management Views ---
# views.py

@login_required
def task_list(request):
    
    if request.user.is_superuser:
        tasks = Task.objects.all().order_by('-due_date')
        page_title = "All System Tasks"
    else:
        tasks = Task.objects.filter(assigned_to=request.user).order_by('-due_date')
        page_title = "My Assigned Tasks"

    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
        
    context = {
        'tasks': tasks,
        # 💡 FIX APPLIED HERE: Reference the choices using the inner TextChoices class
        'status_choices': Task.Status.choices, 
        'page_title': page_title,
        'is_admin': request.user.is_superuser,
    }
    return render(request, "tasks/task_list.html", context)
@login_required
def task_create(request):
    """
    Handles the creation of a new task.
    💡 Only accessible by Superusers. Normal users are redirected.
    """
    
    # --- 💡 NEW PERMISSION CHECK ---
    if not request.user.is_superuser:
        # If the user is NOT a superuser, redirect them to the task list or dashboard
        return redirect("task_list") 

    if request.method == 'POST':
        # Admin users can create tasks
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            # Assigned_to field is handled by the form, allowing the admin to choose anyone.
            task.save()
            return redirect("task_list")
    else:
        # Admin users see the form
        form = TaskForm()
        
    # Since only superusers are here, they see the full form options
    context = {'form': form, 'page_title': 'Create New Task', 'is_admin': request.user.is_superuser}
    return render(request, "tasks/task_form.html", context)



@login_required
def task_update(request, pk):
    """
    Handles the editing of an existing task.
    💡 Only accessible by Superusers. Normal users are redirected.
    """
    task = get_object_or_404(Task, pk=pk)
    
    # --- 💡 NEW PERMISSION CHECK ---
    if not request.user.is_superuser:
        # If the user is NOT a superuser, redirect them to the task list
        return redirect("task_list") 

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            # The created_by field must not be overwritten here
            task.save()
            return redirect("task_list")
    else:
        form = TaskForm(instance=task)
        
    context = {'form': form, 'page_title': f'Edit Task: {task.title}', 'is_admin': request.user.is_superuser}
    return render(request, "tasks/task_form.html", context)




from django.db.models import Count # Import Count function
from django.utils import timezone # Import timezone for overdue check

@login_required
def analytics_page(request):
    # Determine the set of tasks to analyze (all for admin, assigned for normal user)
    if request.user.is_superuser:
        all_tasks = Task.objects.all()
    else:
        all_tasks = Task.objects.filter(assigned_to=request.user)
    
    # 1. Status Counts
    status_summary = all_tasks.values('status').annotate(count=Count('status')).order_by()
    
    # 2. Priority Counts
    priority_summary = all_tasks.values('priority').annotate(count=Count('priority')).order_by()
    
    # 3. Overdue Count
    # Overdue tasks are those past the due date and not marked as DONE
    overdue_count = all_tasks.filter(
        due_date__lt=timezone.now(),
        status__in=['TODO', 'IN_PROGRESS', 'BLOCKED']
    ).count()

    context = {
        'total_tasks': all_tasks.count(),
        'status_summary': status_summary,
        'priority_summary': priority_summary,
        'overdue_count': overdue_count,
        'is_admin': request.user.is_superuser
    }
    return render(request, "analytics.html", context)