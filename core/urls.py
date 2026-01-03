from django.urls import path
from . import views

urlpatterns = [
    # User Auth & Profile
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_page, name='settings'),
    path('analytics/', views.analytics_page, name='analytics'),
    
    # Task Management Paths
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/new/', views.task_create, name='task_create'),
    path('tasks/update/<int:pk>/', views.task_update, name='task_update'),

    path("calendar/", views.task_calendar, name="task_calendar"),
    path("calendar/events/", views.task_calendar_events, name="task_calendar_events"),
    path("calendar/tasks-by-date/", views.tasks_by_date, name="tasks_by_date"),
]