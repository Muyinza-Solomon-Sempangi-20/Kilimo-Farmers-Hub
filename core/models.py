from django.db import models
from django.contrib.auth.models import User

class FarmerProfile(models.Model):
    DISTRICT_CHOICES = [
        ('kampala', 'Kampala'), ('mukono', 'Mukono'), ('wakiso', 'Wakiso'),
        ('jinja', 'Jinja'), ('gulu', 'Gulu'), ('mbarara', 'Mbarara'),
        ('arua', 'Arua'), ('lira', 'Lira'), ('soroti', 'Soroti'),
    ]
    LANGUAGE_CHOICES = [
        ('en', 'English'), ('lug', 'Luganda'), ('ach', 'Acholi'),
        ('nyn', 'Runyankore'), ('sog', 'Lusoga'), ('teo', 'Ateso'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    phone = models.CharField(max_length=15, blank=True)
    district = models.CharField(max_length=50, choices=DISTRICT_CHOICES, default='mukono')
    village = models.CharField(max_length=100, blank=True)
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    farm_size_acres = models.DecimalField(max_digits=6, decimal_places=2, default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — {self.district}"

class Alert(models.Model):
    SEVERITY_CHOICES = [('info', 'Info'), ('warning', 'Warning'), ('danger', 'Danger')]
    CATEGORY_CHOICES = [('disease', 'Disease'), ('weather', 'Weather'), ('market', 'Market'), ('general', 'General')]
    title = models.CharField(max_length=200)
    body = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='info')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='general')
    district = models.CharField(max_length=50, blank=True, help_text="Blank = nationwide")
    source = models.CharField(max_length=100, default='Kilimo Hub')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
