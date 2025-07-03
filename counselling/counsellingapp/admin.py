from django.contrib import admin
from django.conf import settings
from django.apps import apps
# Removed import for CounselorAvailability as it no longer exists


User = apps.get_model(settings.AUTH_USER_MODEL)  # This dynamically gets the User model

admin.site.register(User)

# Removed registration for CounselorAvailability as it no longer exists


