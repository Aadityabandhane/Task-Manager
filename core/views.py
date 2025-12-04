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
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, "profile.html", {"profile": profile})

@login_required
def settings_page(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

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


# views.py - Updated task_list view
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from .forms import SignUpForm, ProfileUpdateForm, TaskForm
from .models import Profile, Task
from django.core.paginator import Paginator

# ... (keep your existing views up to task_list)

@login_required
def task_list(request):
    """
    Enhanced task list with search, filter, and pagination
    """
    # Determine base queryset based on user role
    if request.user.is_superuser:
        tasks = Task.objects.all()
        page_title = "All System Tasks"
    else:
        tasks = Task.objects.filter(assigned_to=request.user)
        page_title = "My Assigned Tasks"
    
    # Initialize filter variables
    search_query = ''
    status_filter = ''
    priority_filter = ''
    assigned_to_filter = ''
    date_filter = ''
    sort_by = request.GET.get('sort', 'due_date')
    
    # ----- SEARCH FUNCTIONALITY -----
    if 'q' in request.GET:
        search_query = request.GET.get('q', '').strip()
        if search_query:
            tasks = tasks.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(assigned_to__username__icontains=search_query) |
                Q(assigned_to__first_name__icontains=search_query) |
                Q(assigned_to__last_name__icontains=search_query)
            )
    
    # ----- FILTER BY STATUS -----
    if 'status' in request.GET:
        status_filter = request.GET.get('status')
        if status_filter and status_filter != 'all':
            tasks = tasks.filter(status=status_filter)
    
    # ----- FILTER BY PRIORITY -----
    if 'priority' in request.GET:
        priority_filter = request.GET.get('priority')
        if priority_filter and priority_filter != 'all':
            tasks = tasks.filter(priority=priority_filter)
    
    # ----- FILTER BY ASSIGNED USER (Admin only) -----
    if request.user.is_superuser and 'assigned_to' in request.GET:
        assigned_to_filter = request.GET.get('assigned_to')
        if assigned_to_filter and assigned_to_filter != 'all':
            tasks = tasks.filter(assigned_to__id=assigned_to_filter)
    
    # ----- FILTER BY DATE -----
    if 'date_filter' in request.GET:
        date_filter = request.GET.get('date_filter')
        today = timezone.now().date()
        
        if date_filter == 'today':
            tasks = tasks.filter(due_date__date=today)
        elif date_filter == 'tomorrow':
            tasks = tasks.filter(due_date__date=today + timezone.timedelta(days=1))
        elif date_filter == 'week':
            end_date = today + timezone.timedelta(days=7)
            tasks = tasks.filter(due_date__date__range=[today, end_date])
        elif date_filter == 'overdue':
            tasks = tasks.filter(due_date__lt=timezone.now(), status__in=['TODO', 'IN_PROGRESS', 'BLOCKED'])
        elif date_filter == 'no_date':
            tasks = tasks.filter(due_date__isnull=True)
    
    # ----- SORTING FUNCTIONALITY -----
    sort_options = {
        'due_date': 'due_date',  # Ascending: oldest first
        '-due_date': '-due_date',  # Descending: newest first
        'priority': 'priority',  # Low to High (LOW, MEDIUM, HIGH, CRITICAL)
        '-priority': '-priority',  # High to Low (CRITICAL, HIGH, MEDIUM, LOW)
        'created_at': 'created_at',  # Oldest first
        '-created_at': '-created_at',  # Newest first
        'title': 'title',  # A-Z
        '-title': '-title',  # Z-A
        'status': 'status',  # Status order
    }
    
    # Default to sorting by due_date if invalid sort option
    sort_by = sort_options.get(sort_by, 'due_date')
    tasks = tasks.order_by(sort_by)
    
    # ----- PAGINATION -----
    paginator = Paginator(tasks, 10)  # Show 10 tasks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all users for admin filter dropdown
    users = User.objects.all().order_by('username') if request.user.is_superuser else None
    
    # Get filter counts for active filters
    total_tasks = tasks.count()
    filtered_tasks_count = page_obj.paginator.count
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'assigned_to_filter': assigned_to_filter,
        'date_filter': date_filter,
        'sort_by': sort_by,
        'users': users,
        'total_tasks': total_tasks,
        'filtered_tasks_count': filtered_tasks_count,
        'status_choices': Task.Status.choices,
        'priority_choices': Task.Priority.choices,
        'page_title': page_title,
        'is_admin': request.user.is_superuser,
        'date_filter_options': [
            ('all', 'All Dates'),
            ('today', 'Today'),
            ('tomorrow', 'Tomorrow'),
            ('week', 'Next 7 Days'),
            ('overdue', 'Overdue'),
            ('no_date', 'No Due Date'),
        ],
        'sort_options': [
            ('due_date', 'Due Date (Oldest First)'),
            ('-due_date', 'Due Date (Newest First)'),
            ('priority', 'Priority (Low to High)'),
            ('-priority', 'Priority (High to Low)'),
            ('created_at', 'Created (Oldest First)'),
            ('-created_at', 'Created (Newest First)'),
            ('title', 'Title (A-Z)'),
            ('-title', 'Title (Z-A)'),
            ('status', 'Status'),
        ],
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