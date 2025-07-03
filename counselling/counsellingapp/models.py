from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from datetime import datetime 
from django.contrib.auth.models import User  # Import datetime for other uses

class User(AbstractUser):
    # Add your custom fields here
    is_admin = models.BooleanField(default=False)
    is_counselor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True) # Default to student for general users
    phone = models.CharField(max_length=15, blank=True, null=True) # Assuming you also want to add 'phone'
    is_verified = models.BooleanField(default=False)
    def __str__(self):
        return self.username


class VerifyEmailLinkCounter(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE)

class CounselorAvailability(models.Model):
    counselor = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now)  # Set default to current date
    start_time = models.TimeField()
    end_time = models.TimeField()

class Appointment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments_as_user',
    )
    counselor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments_as_counselor',
    )
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending',
    )

    def __str__(self):
        return f"{self.user.username} - {self.counselor.username} on {self.date} at {self.time}"
    


class Feedback(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_feedbacks")
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="counselor_feedbacks")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} → {self.counselor.username} ({self.rating} Stars)"
    
# mental_health_app/models.py
# Or your custom User model

class Conversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    # You might want to add a field for session ID or topic if you implement multiple conversation threads

    def __str__(self):
        return f"Conversation with {self.user.username} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def __str__(self):
        return f"Conversation {self.id}" # Or a more descriptive name


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages' # Good practice to define related_name
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # *** ADD THIS FIELD ***
    # Define choices for clarity and consistency
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI'),
    ]
    sender_type = models.CharField(
        max_length=10,
        choices=SENDER_CHOICES,
        default='user' # Or a default that makes sense for your app
    )
    # *** END ADDITION ***

    def __str__(self):
        return f"{self.sender_type.upper()}: {self.text[:50]}..."

    class Meta:
        ordering = ['timestamp'] # Order messages by time