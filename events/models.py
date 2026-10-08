from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('Sports', 'Sports'),
        ('Academic', 'Academic'),
        ('Arts', 'Arts'),
        ('Technology', 'Technology'),
        ('Workshop', 'Workshop'),
        ('Party', 'Party'),
        ('Cultural Fest', 'Cultural Fest'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    rsvp_count = models.IntegerField(default=0)
    capacity = models.IntegerField(default=50)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    organizer = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='organized_events', null=True, blank=True)
    notified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')

    def __str__(self):
        return self.title

    @property
    def seats_available(self):
        return max(0, self.capacity - self.rsvp_count)

    @property
    def is_full(self):
        return self.rsvp_count >= self.capacity

    @property
    def is_registration_closed(self):
        from django.utils import timezone
        from django.utils.timezone import make_aware, is_naive
        if self.registration_deadline:
            deadline = self.registration_deadline
            # Make naive datetimes (e.g. from old data) timezone-aware before comparing
            if is_naive(deadline):
                deadline = make_aware(deadline)
            return timezone.now() > deadline
        return False

class RSVP(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='rsvps')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_rsvps')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class EventRegistration(models.Model):
    """Stores detailed student registration info for each event."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    student_id = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=50, blank=True)
    year = models.CharField(max_length=5, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.full_name} → {self.event.title}"

class Review(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.rating}★)"

class StudentProfile(models.Model):
    YEAR_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
        ('PG', 'Post Graduate'),
    ]

    DEPARTMENT_CHOICES = [
        ('CSE', 'Computer Science & Engineering'),
        ('ECE', 'Electronics & Communication'),
        ('ME',  'Mechanical Engineering'),
        ('CE',  'Civil Engineering'),
        ('EEE', 'Electrical & Electronics'),
        ('IT',  'Information Technology'),
        ('BCA', 'BCA'),
        ('MCA', 'MCA'),
        ('MBA', 'MBA'),
        ('Other', 'Other'),
    ]

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('organizer', 'Event Organizer'),
        ('admin', 'Administrator'),
    ]

    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True)
    year       = models.CharField(max_length=5, choices=YEAR_CHOICES, blank=True)
    phone      = models.CharField(max_length=15, blank=True)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.username} – {self.department} Year {self.year} ({self.role})"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
