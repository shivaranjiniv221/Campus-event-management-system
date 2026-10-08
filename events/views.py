from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
import csv
from .models import Event, RSVP, StudentProfile, Review, EventRegistration, Favorite

def parse_aware_datetime(value):
    """Parse a naive datetime string from a datetime-local input and make it timezone-aware."""
    if not value:
        return None
    try:
        # datetime-local format: '2026-05-30T12:00'
        dt = datetime.strptime(value, '%Y-%m-%dT%H:%M')
        return make_aware(dt)
    except (ValueError, TypeError):
        return None

def is_user_admin(user):
    """Check if the logged-in user is an administrator."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    profile = getattr(user, 'student_profile', None)
    return profile is not None and profile.role == 'admin'

def is_user_organizer(user):
    """Check if the logged-in user is an event organizer."""
    if not user.is_authenticated:
        return False
    if is_user_admin(user):
        return True
    profile = getattr(user, 'student_profile', None)
    return profile is not None and profile.role == 'organizer'

def admin_required(view_func):
    """Decorator for views that require admin access."""
    def wrapper(request, *args, **kwargs):
        if not is_user_admin(request.user):
            messages.error(request, "Access denied. Administrator privileges required.")
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper

def index(request):
    now = timezone.now()
    
    # Upcoming Approved Events (soonest first)
    upcoming_events = Event.objects.filter(date__gte=now, status='approved').order_by('date')[:6]
    
    # Trending Approved Events (most RSVPs)
    trending_events = Event.objects.filter(status='approved').order_by('-rsvp_count')[:6]
    
    recommendations = []
    if request.user.is_authenticated:
        user_categories = RSVP.objects.filter(user=request.user).values_list('event__category', flat=True).distinct()
        if user_categories:
            recommendations = Event.objects.filter(
                category__in=user_categories,
                status='approved'
            ).exclude(
                event_rsvps__user=request.user
            ).order_by('?')[:3]
            
    return render(request, 'index.html', {
        'upcoming_events': upcoming_events,
        'trending_events': trending_events,
        'recommendations': recommendations,
        'categories': [c[0] for c in Event.CATEGORY_CHOICES]
    })

def explore(request):
    query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    upcoming_only = request.GET.get('upcoming', '') == 'true'
    
    events = Event.objects.filter(status='approved').order_by('date')
    
    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category:
        events = events.filter(category=category)
    if upcoming_only:
        events = events.filter(date__gte=timezone.now())
        
    return render(request, 'explore.html', {
        'events': events,
        'query': query,
        'category': category,
        'upcoming_only': upcoming_only,
        'categories': [c[0] for c in Event.CATEGORY_CHOICES]
    })

def about(request):
    return render(request, 'about.html')

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_rsvp = False
    is_favorite = False
    
    if request.user.is_authenticated:
        user_rsvp = RSVP.objects.filter(user=request.user, event=event).exists()
        is_favorite = Favorite.objects.filter(user=request.user, event=event).exists()
        
    return render(request, 'event_detail.html', {
        'event': event,
        'user_rsvp': user_rsvp,
        'is_favorite': is_favorite
    })

def register(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        # Use email as the username since username field is removed
        if not post_data.get('username') and post_data.get('email'):
            post_data['username'] = post_data.get('email')

        form = UserCreationForm(post_data)
        if form.is_valid():
            user = form.save()
            
            # Save user names and email
            user.first_name = request.POST.get('name', '')
            user.last_name = ''
            user.email = request.POST.get('email', '')
            user.save()
            
            # Save role and student profile fields
            role = request.POST.get('role', 'student')
            StudentProfile.objects.create(
                user=user,
                student_id=request.POST.get('student_id', ''),
                department=request.POST.get('department', ''),
                year=request.POST.get('year', ''),
                phone=request.POST.get('phone', ''),
                role=role
            )
            
            # Send Email Confirmation (Console Backend)
            try:
                send_mail(
                    subject="Welcome to CampusEvents!",
                    message=f"Hi {user.first_name or user.username},\n\nThank you for registering on CampusEvents. You can now discover, register, and coordinate fests across your campus!\n\nBest regards,\nCampusEvents Team",
                    from_email="events@campus.edu",
                    recipient_list=[user.email],
                    fail_silently=True
                )
            except Exception:
                pass
                
            messages.success(request, "Registration successful. Please login to continue.")
            return redirect('login')
    else:
        form = UserCreationForm()
    
    departments = StudentProfile.DEPARTMENT_CHOICES
    years = StudentProfile.YEAR_CHOICES
    roles = StudentProfile.ROLE_CHOICES
    
    return render(request, 'register.html', {
        'form': form,
        'departments': departments,
        'years': years,
        'roles': roles
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Check user role and redirect to dashboards if Admin
            if is_user_admin(user):
                messages.success(request, f"Logged in as Administrator: {user.username}")
                return redirect('admin_dashboard')
            else:
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect('index')

@login_required
def profile(request):
    user = request.user
    profile_obj, created = StudentProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        profile_obj.student_id = request.POST.get('student_id', '')
        profile_obj.department = request.POST.get('department', '')
        profile_obj.year = request.POST.get('year', '')
        profile_obj.phone = request.POST.get('phone', '')
        profile_obj.save()
        
        messages.success(request, "Your profile has been updated successfully!")
        return redirect('profile')
        
    favorites = Favorite.objects.filter(user=user).select_related('event')
    departments = StudentProfile.DEPARTMENT_CHOICES
    years = StudentProfile.YEAR_CHOICES
    
    return render(request, 'profile.html', {
        'user': user,
        'profile': profile_obj,
        'favorites': favorites,
        'departments': departments,
        'years': years
    })

@login_required
def rsvp_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    # Check registration deadline
    if event.is_registration_closed:
        messages.error(request, "Registration has closed for this event.")
        return redirect('event_detail', pk=pk)
        
    # Check capacity
    if event.is_full:
        messages.error(request, "This event is at full capacity.")
        return redirect('event_detail', pk=pk)
        
    rsvp, created = RSVP.objects.get_or_create(user=request.user, event=event)
    if created:
        event.rsvp_count += 1
        event.save()

        # Also store detailed registration record
        profile_obj = getattr(request.user, 'student_profile', None)
        EventRegistration.objects.get_or_create(
            user=request.user,
            event=event,
            defaults={
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email or "noemail@campus.edu",
                'phone': getattr(profile_obj, 'phone', ''),
                'student_id': getattr(profile_obj, 'student_id', ''),
                'department': getattr(profile_obj, 'department', ''),
                'year': getattr(profile_obj, 'year', ''),
            }
        )
        
        # Send Confirmation Email (Console Backend)
        try:
            send_mail(
                subject=f"RSVP Confirmation: {event.title}",
                message=f"Hi {request.user.first_name or request.user.username},\n\nYou have successfully RSVPed for the event: {event.title}.\n\nLocation: {event.location}\nDate & Time: {event.date.strftime('%A, %b %d, %Y at %I:%M %p')}\n\nWe look forward to seeing you there!\n\nBest regards,\nCampusEvents Team",
                from_email="events@campus.edu",
                recipient_list=[request.user.email],
                fail_silently=True
            )
        except Exception:
            pass

        messages.success(request, "Successfully registered for the event!")
    else:
        messages.info(request, "You are already registered for this event.")
    return redirect('event_detail', pk=pk)

@login_required
def cancel_rsvp(request, pk):
    event = get_object_or_404(Event, pk=pk)
    rsvp = RSVP.objects.filter(user=request.user, event=event).first()
    
    if rsvp:
        rsvp.delete()
        EventRegistration.objects.filter(user=request.user, event=event).delete()
        if event.rsvp_count > 0:
            event.rsvp_count -= 1
            event.save()
        messages.success(request, "Your registration has been cancelled.")
    else:
        messages.error(request, "You are not registered for this event.")
        
    return redirect('event_detail', pk=pk)

@login_required
def toggle_favorite(request, pk):
    event = get_object_or_404(Event, pk=pk)
    fav = Favorite.objects.filter(user=request.user, event=event).first()
    if fav:
        fav.delete()
        messages.success(request, f"Removed '{event.title}' from your saved favorites.")
    else:
        Favorite.objects.create(user=request.user, event=event)
        messages.success(request, f"Added '{event.title}' to your saved favorites!")
    return redirect('event_detail', pk=pk)

@login_required
def view_registrations(request, pk):
    """Let the event organizer or Admin view all student registrations for their event."""
    event = get_object_or_404(Event, pk=pk)
    
    # Restrict to Organizer of event OR Admin
    if event.organizer != request.user and not is_user_admin(request.user):
        messages.error(request, "Access denied. You do not organize this event.")
        return redirect('organized_events')
        
    registrations = EventRegistration.objects.filter(event=event).select_related('user')

    # CSV export support
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="registrations_{event.pk}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Full Name', 'Email', 'Phone', 'Student ID', 'Department', 'Year', 'Registered At'])
        for reg in registrations:
            writer.writerow([
                reg.full_name, reg.email, reg.phone,
                reg.student_id, reg.department, reg.year,
                reg.registered_at.strftime('%Y-%m-%d %H:%M'),
            ])
        return response

    return render(request, 'view_registrations.html', {
        'event': event,
        'registrations': registrations,
    })

@login_required
def my_events(request):
    rsvps = RSVP.objects.filter(user=request.user).select_related('event')
    favorites = Favorite.objects.filter(user=request.user).select_related('event')
    return render(request, 'my_events.html', {
        'rsvps': rsvps,
        'favorites': favorites
    })

def chat_api(request):
    query = request.GET.get('msg', '').lower()
    if not query:
        return JsonResponse({'response': "I didn't quite catch that. Could you ask about a specific category or event?"})
    
    matches = Event.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query) |
        Q(category__icontains=query),
        status='approved'
    )[:3]

    if matches:
        titles = ", ".join([e.title for e in matches])
        response = f"I found some live events for you: {titles}. Would you like to see more details about these?"
    else:
        response = f"I couldn't find any events matching '{query}'. Try asking about 'Technology', 'Arts', or 'Workshop'!"
        
    return JsonResponse({'response': response})

@login_required
def organized_events(request):
    # Only allow Event Organizers or Admins
    if not is_user_organizer(request.user) and not is_user_admin(request.user):
        messages.error(request, "Access denied. You must be an Event Organizer to access this hub.")
        return redirect('index')
        
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    # Analytics Data
    stats = {
        'total_rsvps': sum(e.rsvp_count for e in events),
        'labels': [e.title[:15] for e in events[:5]],
        'data': [e.rsvp_count for e in events[:5]]
    }
    return render(request, 'organized_events.html', {'events': events, 'stats': stats})

@login_required
def add_review(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        Review.objects.create(
            user=request.user,
            event=event,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment')
        )
    return redirect('event_detail', pk=pk)

def export_calendar(request, pk):
    event = get_object_or_404(Event, pk=pk)
    content = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:{event.title}\nDTSTART:{event.date.strftime('%Y%m%dT%H%M%SZ')}\nLOCATION:{event.location}\nDESCRIPTION:{event.description}\nEND:VEVENT\nEND:VCALENDAR"
    response = HttpResponse(content, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="event_{pk}.ics"'
    return response

@login_required
def notify_attendees(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    
    # Send actual email to all RSVPed student emails
    registrations = EventRegistration.objects.filter(event=event)
    emails = [reg.email for reg in registrations if reg.email]
    
    if emails:
        try:
            send_mail(
                subject=f"Important Update: {event.title}",
                message=f"Hello attendee,\n\nOrganizer of the event '{event.title}' has sent an update.\n\nPlease check the events detail page for any schedule or location modifications.\n\nBest regards,\nCampusEvents Admin",
                from_email="events@campus.edu",
                recipient_list=emails,
                fail_silently=True
            )
            messages.success(request, f"E-mail broadcast sent to all {len(emails)} registered attendees!")
        except Exception:
            messages.error(request, "Failed to broadcast email notifications.")
    else:
        messages.info(request, "No attendees registered to notify yet.")
        
    event.notified = True
    event.save()
    return redirect('organized_events')

@login_required
def create_event(request):
    # Only allow Event Organizers or Admins
    if not is_user_organizer(request.user) and not is_user_admin(request.user):
        messages.error(request, "Access denied. Organizer access required.")
        return redirect('index')
        
    error_message = None
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        location = request.POST.get('location')
        category = request.POST.get('category')
        image = request.FILES.get('image')
        
        # AI-Inspired Spam Detection Heuristics
        is_spam = False
        if len(description) < 20: 
            error_message = "Description is too short. Please provide more details."
            is_spam = True
        elif 'http' in description and description.count('http') > 2:
            error_message = "Suspicious links detected. Please reduce the number of links."
            is_spam = True
        elif any(bad_word in title.lower() for bad_word in ['free money', 'winner', 'lottery']):
            error_message = "Event title seems suspicious."
            is_spam = True

        if not is_spam:
            capacity_val = request.POST.get('capacity')
            capacity = int(capacity_val) if capacity_val and capacity_val.isdigit() else 50

            registration_deadline = parse_aware_datetime(request.POST.get('registration_deadline'))
            event_date = parse_aware_datetime(request.POST.get('date')) or date

            # Set status based on Admin approval workflow
            status_val = 'approved' if is_user_admin(request.user) else 'pending'
            
            event = Event.objects.create(
                title=title,
                description=description,
                date=event_date,
                location=location,
                category=category,
                image=image,
                capacity=capacity,
                registration_deadline=registration_deadline,
                organizer=request.user,
                status=status_val
            )
            if status_val == 'pending':
                messages.success(request, "Event submitted successfully! It will appear on campus pages once approved by Admin.")
            else:
                messages.success(request, "Event created and published successfully!")
            return redirect('organized_events')
            
    return render(request, 'create_event.html', {
        'error_message': error_message,
        'categories': Event.CATEGORY_CHOICES
    })

@login_required
def edit_event(request, pk):
    # Retrieve event. Organizer of event or Admin can edit.
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user and not is_user_admin(request.user):
        messages.error(request, "Access denied. You cannot edit this event.")
        return redirect('organized_events')
        
    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.date = parse_aware_datetime(request.POST.get('date')) or event.date
        event.location = request.POST.get('location')
        event.category = request.POST.get('category')

        capacity_val = request.POST.get('capacity')
        event.capacity = int(capacity_val) if capacity_val and capacity_val.isdigit() else 50

        event.registration_deadline = parse_aware_datetime(request.POST.get('registration_deadline'))

        if request.FILES.get('image'):
            event.image = request.FILES.get('image')
            
        event.save()
        messages.success(request, "Event details updated successfully.")
        return redirect('organized_events')
        
    return render(request, 'create_event.html', {
        'event': event,
        'categories': Event.CATEGORY_CHOICES
    })

@login_required
def delete_event(request, pk):
    # Organizer or Admin can delete
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user and not is_user_admin(request.user):
        messages.error(request, "Access denied. You cannot delete this event.")
        return redirect('organized_events')
        
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully.")
        return redirect('organized_events')
    return render(request, 'delete_confirm.html', {'event': event})

# ─────────────────────────────────────────────────────────────────────────
#    ADMIN ONLY VIEWS
# ─────────────────────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_dashboard(request):
    # Analytics Metrics
    total_events_count = Event.objects.count()
    approved_events_count = Event.objects.filter(status='approved').count()
    pending_events_count = Event.objects.filter(status='pending').count()
    rejected_events_count = Event.objects.filter(status='rejected').count()
    
    total_registrations = RSVP.objects.count()
    upcoming_events_count = Event.objects.filter(date__gte=timezone.now(), status='approved').count()
    
    # Most Popular Event Category
    popular_categories = Event.objects.values('category').annotate(reg_count=Count('event_rsvps')).order_by('-reg_count')
    most_popular_cat = popular_categories[0]['category'] if popular_categories else "None"
    
    # Recent registrations (last 10)
    recent_registrations = EventRegistration.objects.select_related('event', 'user').order_by('-registered_at')[:10]
    
    # Categories stats for ChartJS
    categories_data = Event.objects.values('category').annotate(count=Count('id'))
    stats = {
        'labels': [c['category'] for c in categories_data],
        'data': [c['count'] for c in categories_data],
        'total_events': total_events_count,
        'approved_events': approved_events_count,
        'pending_events': pending_events_count,
        'rejected_events': rejected_events_count,
        'total_registrations': total_registrations,
        'upcoming_events': upcoming_events_count,
        'most_popular_cat': most_popular_cat,
    }
    
    return render(request, 'admin_dashboard.html', {
        'stats': stats,
        'recent_registrations': recent_registrations
    })

@login_required
@admin_required
def admin_events(request):
    events = Event.objects.select_related('organizer').order_by('-created_at')
    return render(request, 'admin_events.html', {'events': events})

@login_required
@admin_required
def approve_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.status = 'approved'
    event.save()
    
    # Notify organizer via Console Email
    if event.organizer and event.organizer.email:
        try:
            send_mail(
                subject=f"Event Approved: {event.title}",
                message=f"Hi {event.organizer.username},\n\nWe are pleased to inform you that your event '{event.title}' has been approved by the Admin and is now live on the CampusEvents platform.\n\nBest regards,\nCampusEvents Team",
                from_email="events@campus.edu",
                recipient_list=[event.organizer.email],
                fail_silently=True
            )
        except Exception:
            pass
            
    messages.success(request, f"Event '{event.title}' approved successfully!")
    return redirect('admin_events')

@login_required
@admin_required
def reject_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.status = 'rejected'
    event.save()
    
    # Notify organizer via Console Email
    if event.organizer and event.organizer.email:
        try:
            send_mail(
                subject=f"Event Request Update: {event.title}",
                message=f"Hi {event.organizer.username},\n\nYour submission for '{event.title}' has been reviewed by the Admin team and is unfortunately rejected at this time.\n\nPlease review event guidelines and try again.\n\nBest regards,\nCampusEvents Team",
                from_email="events@campus.edu",
                recipient_list=[event.organizer.email],
                fail_silently=True
            )
        except Exception:
            pass
            
    messages.warning(request, f"Event '{event.title}' request rejected.")
    return redirect('admin_events')

@login_required
@admin_required
def admin_students(request):
    students = StudentProfile.objects.select_related('user').all()
    
    # Handle user deletion
    if request.method == 'POST':
        student_id_to_del = request.POST.get('student_pk')
        if student_id_to_del:
            user_to_del = get_object_or_404(User, pk=student_id_to_del)
            # Prevent self-deletion
            if user_to_del == request.user:
                messages.error(request, "You cannot delete your own Administrator account!")
            else:
                user_to_del.delete()
                messages.success(request, f"User account '{user_to_del.username}' deleted successfully.")
            return redirect('admin_students')
            
    return render(request, 'admin_students.html', {'students': students})

# ─────────────────────────────────────────────────────────────────────────
#    INTERACTIVE CALENDAR VIEW
# ─────────────────────────────────────────────────────────────────────────

def calendar_view(request):
    # Return approved events as JSON for AJAX FullCalendar loading if requested
    if request.GET.get('format') == 'json':
        events = Event.objects.filter(status='approved')
        events_list = []
        for e in events:
            # Map categories to clean visual colors
            color = '#38bdf8' # Default primary blue
            if e.category == 'Sports': color = '#10b981' # Green
            elif e.category == 'Academic': color = '#6366f1' # Indigo
            elif e.category == 'Arts': color = '#ec4899' # Pink
            elif e.category == 'Technology': color = '#f59e0b' # Orange
            elif e.category == 'Workshop': color = '#8b5cf6' # Purple
            elif e.category == 'Party': color = '#ef4444' # Red
            elif e.category == 'Cultural Fest': color = '#14b8a6' # Teal
            
            events_list.append({
                'id': e.id,
                'title': e.title,
                'start': e.date.isoformat(),
                'url': f'/event/{e.id}/',
                'backgroundColor': color,
                'borderColor': color,
                'textColor': '#fff'
            })
        return JsonResponse(events_list, safe=False)
        
    return render(request, 'calendar.html')
