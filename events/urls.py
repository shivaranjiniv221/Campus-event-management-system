from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('events/', RedirectView.as_view(url='/explore/', permanent=True)),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/<int:pk>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('event/<int:pk>/cancel-rsvp/', views.cancel_rsvp, name='cancel_rsvp'),
    path('event/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    # Dashboards & Event Ops
    path('my-events/', views.my_events, name='my_events'),
    path('organized-events/', views.organized_events, name='organized_events'),
    path('create-event/', views.create_event, name='create_event'),
    path('edit-event/<int:pk>/', views.edit_event, name='edit_event'),
    path('delete-event/<int:pk>/', views.delete_event, name='delete_event'),
    path('event/<int:pk>/review/', views.add_review, name='add_review'),
    path('event/<int:pk>/calendar/', views.export_calendar, name='export_calendar'),
    path('event/<int:pk>/notify/', views.notify_attendees, name='notify_attendees'),
    path('event/<int:pk>/registrations/', views.view_registrations, name='view_registrations'),
    
    # Admin Dashboard (Custom)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/events/', views.admin_events, name='admin_events'),
    path('admin-dashboard/events/<int:pk>/approve/', views.approve_event, name='approve_event'),
    path('admin-dashboard/events/<int:pk>/reject/', views.reject_event, name='reject_event'),
    path('admin-dashboard/students/', views.admin_students, name='admin_students'),
    
    # Interactive Calendar & API
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('explore/', views.explore, name='explore'),
    path('about/', views.about, name='about'),
]
