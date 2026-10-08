from django.core.management.base import BaseCommand
from events.models import Event
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

class Command(BaseCommand):
    help = 'Seeds the database with initial campus events'

    def handle(self, *args, **kwargs):
        # Clear existing events
        Event.objects.all().delete()

        # Reset SQLite autoincrement so event IDs consistently start from 1
        from django.db import connection
        with connection.cursor() as cursor:
            try:
                cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'events_event';")
            except Exception:
                pass

        # Find or create a default admin / organizer for seeded events
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user, _ = User.objects.get_or_create(
                username='admin',
                defaults={'email': 'admin@campus.edu', 'is_staff': True, 'is_superuser': True}
            )
            admin_user.set_password('admin123')
            admin_user.save()
            
            # Ensure student profile exists with admin role
            from events.models import StudentProfile
            StudentProfile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})

        events_data = [
            {
                'title': 'AI & Future of Coding',
                'description': 'A deep dive into how AI is changing the landscape of software development.',
                'date': timezone.now() + datetime.timedelta(days=5),
                'location': 'Main Auditorium',
                'category': 'Technology',
                'image': 'event_images/ai_future.png',
                'rsvp_count': 120,
                'capacity': 200,
                'organizer': admin_user,
                'status': 'approved'
            },
            {
                'title': 'Midnight Melodies: Jazz Night',
                'description': 'Enjoy a relaxing evening with the best jazz musicians on campus.',
                'date': timezone.now() + datetime.timedelta(days=8),
                'location': 'Campus Plaza',
                'category': 'Arts',
                'image': 'event_images/jazz_night.png',
                'rsvp_count': 85,
                'capacity': 150,
                'organizer': admin_user,
                'status': 'approved'
            },
            {
                'title': 'Inter-Collegiate Basketball',
                'description': 'The biggest sports event of the semester! Come support your team.',
                'date': timezone.now() + datetime.timedelta(days=12),
                'location': 'Sports Arena',
                'category': 'Sports',
                'image': 'event_images/basketball.png',
                'rsvp_count': 250,
                'capacity': 400,
                'organizer': admin_user,
                'status': 'approved'
            },
            {
                'title': 'Web Dev Masterclass',
                'description': 'Learn modern web development using Django and React.',
                'date': timezone.now() + datetime.timedelta(days=15),
                'location': 'CS Lab 3',
                'category': 'Workshop',
                'image': 'event_images/web_dev.png',
                'rsvp_count': 45,
                'capacity': 100,
                'organizer': admin_user,
                'status': 'approved'
            },
            {
                'title': 'HackFest 2026',
                'description': '48 hours of non-stop building, coding, and innovation.',
                'date': timezone.now() + datetime.timedelta(days=20),
                'location': 'Tech Hub',
                'category': 'Technology',
                'image': 'event_images/hackfest.png',
                'rsvp_count': 300,
                'capacity': 500,
                'organizer': admin_user,
                'status': 'approved'
            },
            {
                'title': 'Spring Cultural Carnival',
                'description': 'Celebrate diversity with dance performance, regional cuisines, and cultural booths.',
                'date': timezone.now() + datetime.timedelta(days=7),
                'location': 'Central Lawn',
                'category': 'Cultural Fest',
                'image': 'event_images/carnival.png',
                'rsvp_count': 180,
                'capacity': 300,
                'organizer': admin_user,
                'status': 'approved'
            },
            {
                'title': 'Grad Prep Seminar & Writing workshop',
                'description': 'Get insights from professors and recruiters on preparing for graduate applications.',
                'date': timezone.now() + datetime.timedelta(days=3),
                'location': 'Seminar Hall B',
                'category': 'Academic',
                'image': 'event_images/college.jpeg',
                'rsvp_count': 30,
                'capacity': 60,
                'organizer': admin_user,
                'status': 'approved'
            },
            {
                'title': 'Mid-Term Social Mixer',
                'description': 'Take a break from studying and connect with fellow college peers. Music, food and games!',
                'date': timezone.now() + datetime.timedelta(days=4),
                'location': 'Student Center Clubroom',
                'category': 'Party',
                'image': 'event_images/ArtCafe.jpg',
                'rsvp_count': 95,
                'capacity': 120,
                'organizer': admin_user,
                'status': 'approved'
            }
        ]

        for data in events_data:
            Event.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f'Successfully created event: {data["title"]}'))
