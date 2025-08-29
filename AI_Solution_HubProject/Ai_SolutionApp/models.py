from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

class Contact(models.Model):
    """Contact form submissions model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, validators=[
        RegexValidator(regex=r'^[a-zA-Z\s]+$', message='Name can only contain letters and spaces')
    ])
    email = models.EmailField()
    phone = models.CharField(max_length=20, validators=[
        RegexValidator(regex=r'^[\+]?[1-9][\d]{0,15}$', message='Enter a valid phone number')
    ])
    company = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    job_details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('contacted', 'Contacted'),
        ('closed', 'Closed')
    ], default='new')
    notes = models.TextField(blank=True, null=True)
    admin_reply_sent = models.BooleanField(default=False, help_text="Mark as true when admin reply email is sent")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'
    
    def __str__(self):
        return f"{self.name} - {self.company} ({self.created_at.strftime('%Y-%m-%d')})"


class Service(models.Model):
    """AI services offered by the company"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, help_text="FontAwesome icon class")
    features = models.JSONField(default=list, help_text="List of service features")
    pricing_tier = models.CharField(max_length=20, choices=[
        ('basic', 'Basic'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise')
    ])
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title


class PastSolution(models.Model):
    """Past AI solutions and case studies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    client_name = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    description = models.TextField()
    challenge = models.TextField()
    solution = models.TextField()
    results = models.TextField()
    image = models.ImageField(upload_to='solutions/', blank=True, null=True)
    technologies_used = models.JSONField(default=list)
    completion_date = models.DateField()
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-completion_date']
        verbose_name = 'Past Solution'
        verbose_name_plural = 'Past Solutions'
    
    def __str__(self):
        return f"{self.title} - {self.client_name}"


class Event(models.Model):
    """Company events and webinars"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=50, choices=[
        ('webinar', 'Webinar'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('meetup', 'Meetup')
    ])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    is_virtual = models.BooleanField(default=False)
    registration_link = models.URLField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(blank=True, null=True)
    current_participants = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%Y-%m-%d')}"
    
    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()
    
    @property
    def registration_open(self):
        return self.current_participants < (self.max_participants or float('inf'))


class Gallery(models.Model):
    """Photo gallery for events and company activities"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='gallery/')
    category = models.CharField(max_length=100, choices=[
        ('events', 'Events'),
        ('team', 'Team'),
        ('office', 'Office'),
        ('awards', 'Awards'),
        ('other', 'Other')
    ])
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name_plural = 'Galleries'
    
    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """Customer testimonials and reviews"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.company} ({self.rating}★)"
    
    def get_stars(self):
        return range(self.rating)


class Article(models.Model):
    """Blog articles and company insights"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    excerpt = models.TextField(max_length=300)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, choices=[
        ('ai_insights', 'AI Insights'),
        ('industry_news', 'Industry News'),
        ('case_studies', 'Case Studies'),
        ('technology', 'Technology'),
        ('company_updates', 'Company Updates')
    ])
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class AdminDashboard(models.Model):
    """Admin dashboard configuration and analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard_title = models.CharField(max_length=200, default="AI Solution Hub Dashboard")
    welcome_message = models.TextField(default="Welcome to the AI Solution Hub Admin Dashboard")
    chart_config = models.JSONField(default=dict, help_text="Chart.js configuration")
    quick_actions = models.JSONField(default=list, help_text="Quick action actions")
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Admin Dashboard'
        verbose_name_plural = 'Admin Dashboard'
    
    def __str__(self):
        return self.dashboard_title


class SiteSettings(models.Model):
    """Global site settings and configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site_name = models.CharField(max_length=200, default="AI Solution Hub")
    site_description = models.TextField(default="Leading AI Solutions Provider")
    contact_email = models.EmailField(default="info@aisolutionshub.com")
    contact_phone = models.CharField(max_length=20, default="+1-555-123-4567")
    address = models.TextField(default="123 AI Street, Tech City, TC 12345")
    social_links = models.JSONField(default=dict)
    analytics_code = models.TextField(blank=True, null=True)
    maintenance_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    @classmethod
    def get_settings(cls):
        """Get or create site settings singleton"""
        obj, created = cls.objects.get_or_create(pk=cls.objects.first().pk if cls.objects.exists() else None)
        return obj
