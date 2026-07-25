from django.db import models


class UssdSession(models.Model):
    phone_number = models.CharField(max_length=20)
    session_id = models.CharField(max_length=100, unique=True)
    current_menu = models.CharField(max_length=50, default='main')
    menu_state = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.phone_number} - {self.current_menu}"


class SmsLog(models.Model):
    DIRECTION_CHOICES = [('IN', 'Incoming'), ('OUT', 'Outgoing')]
    phone_number = models.CharField(max_length=20)
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES)
    message = models.TextField()
    command = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default='delivered')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.direction} {self.phone_number}: {self.message[:50]}"
