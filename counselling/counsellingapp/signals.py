# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import datetime, time
from .models import User, CounselorAvailability

@receiver(post_save, sender=User)
def create_default_availability(sender, instance, created, **kwargs):
    if created and instance.is_counselor:
        default_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        default_start = time(9, 0)  # 9:00 AM
        default_end = time(17, 0)   # 5:00 PM

        for day in default_days:
            CounselorAvailability.objects.get_or_create(
                counselor=instance,
                day=day,
                defaults={'start_time': default_start, 'end_time': default_end}
            )
