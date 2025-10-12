from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import os
from PIL import Image

# Custom Image Field with validation
class OptimizedImageField(models.ImageField):
    """Custom ImageField with automatic optimization and format validation"""
    
    def __init__(self, *args, **kwargs):
        # Set default validators for image formats
        validators = kwargs.get('validators', [])
        validators.append(FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']))
        kwargs['validators'] = validators
        
        # Set default help text
        if 'help_text' not in kwargs:
            kwargs['help_text'] = 'Upload PNG, JPEG, or WebP images. Max size: 10MB'
            
        super().__init__(*args, **kwargs)
    
    def clean(self, value, model_instance):
        """Clean and validate the uploaded image"""
        value = super().clean(value, model_instance)
        
        if value:
            # Check file size (10MB limit)
            if value.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError('Image file too large. Maximum size is 10MB.')
            
            # Validate image format using PIL
            try:
                with Image.open(value) as img:
                    if img.format.lower() not in ['jpeg', 'png', 'webp']:
                        raise ValidationError('Only JPEG, PNG, and WebP images are allowed.')
            except Exception as e:
                raise ValidationError('Invalid image file. Please upload a valid image.')
        
        return value

# User Roles
class UserRole(models.Model):
    """User roles for admin system"""
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('content_manager', 'Content Manager'),
        ('events_manager', 'Events Manager'),
        ('support_agent', 'Support Agent'),
        ('analyst', 'Analyst'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField('auth.Permission', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"

class UserProfile(models.Model):
    """Extended user profile with role information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    profile_picture = OptimizedImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, help_text="Brief bio about the user")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name if self.role else 'No Role'}"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class Contact(models.Model):
    """Contact form submissions model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, validators=[
        RegexValidator(regex=r'^[a-zA-Z\s]+$', message='Name can only contain letters and spaces')
    ])
    email = models.EmailField()
    phone = models.CharField(max_length=20, validators=[
        RegexValidator(regex=r'^[\+]?[0-9][\d\s\-\(\)]{0,20}$', message='Enter a valid phone number')
    ])
    company = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    job_details = models.TextField()
    interest = models.CharField(max_length=100, blank=True, null=True, help_text="What the customer is interested in")
    message = models.TextField(blank=True, null=True, help_text="Additional message from customer")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('contacted', 'Contacted'),
        ('closed', 'Closed')
    ], default='new')
    form_type = models.CharField(max_length=20, choices=[
        ('contact', 'Contact Inquiry'),
        ('demo', 'Demo Request'),
        ('event', 'Event Registration'),
    ], default='contact', help_text="Type of form submission")
    notes = models.TextField(blank=True, null=True)
    admin_reply_sent = models.BooleanField(default=False, help_text="Mark as true when admin reply email is sent")
    # Event-specific fields
    event = models.ForeignKey('Event', on_delete=models.SET_NULL, null=True, blank=True, help_text="Associated event for event registrations")
    reminder_sent = models.BooleanField(default=False, help_text="Whether reminder email has been sent")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'
        permissions = [
            ("export_contact", "Can export contact inquiries"),
        ]
    
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
    image = OptimizedImageField(upload_to='solutions/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="External image URL as alternative to uploaded image")
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
    
    @property
    def get_image(self) -> str:
        """Return the image URL (uploaded file or external URL)."""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return ""


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
    featured_image = OptimizedImageField(upload_to='events/', blank=True, null=True)
    featured_image_url = models.URLField(blank=True, null=True, help_text="External image URL as alternative to uploaded image")
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%Y-%m-%d')}"
    
    @property
    def get_featured_image(self) -> str:
        """Return the featured image URL (uploaded file or external URL)."""
        if self.featured_image:
            return self.featured_image.url
        elif self.featured_image_url:
            return self.featured_image_url
        return ""
    
    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()
    
    @property
    def registration_open(self):
        return self.current_participants < (self.max_participants or float('inf'))


class Gallery(models.Model):
    """Photo gallery for events and company activities with enhanced image support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = OptimizedImageField(upload_to='gallery/')
    thumbnail = OptimizedImageField(upload_to='gallery/thumbnails/', blank=True, null=True)
    category = models.CharField(max_length=100, choices=[
        ('ai_solutions', 'AI Solutions'),
        ('team_events', 'Team Events'),
        ('conferences', 'Conferences'),
        ('workshops', 'Workshops'),
        ('office', 'Office'),
        ('awards', 'Awards'),
        ('client_meetings', 'Client Meetings'),
        ('product_demos', 'Product Demos'),
        ('research', 'Research & Development'),
        ('other', 'Other')
    ], default='other')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_hero_image = models.BooleanField(default=False, help_text="Use as hero background image")
    order = models.PositiveIntegerField(default=0)
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alt text for accessibility")
    tags = models.JSONField(default=list, help_text="Tags for filtering and search")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name_plural = 'Galleries'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate alt text if not provided
        if not self.alt_text:
            self.alt_text = f"{self.title} - AI Solution Hub Gallery"
        super().save(*args, **kwargs)
    
    @property
    def image_url(self):
        """Return image URL for templates"""
        if self.image:
            return self.image.url
        return None
    
    @property
    def thumbnail_url(self):
        """Return thumbnail URL for templates"""
        if self.thumbnail:
            return self.thumbnail.url
        elif self.image:
            return self.image.url
        return None


class Testimonial(models.Model):
    """Customer testimonials and reviews"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField()
    image = OptimizedImageField(upload_to='testimonials/', blank=True, null=True)
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
    featured_image = OptimizedImageField(upload_to='articles/', blank=True, null=True)
    featured_image_url = models.URLField(blank=True, null=True, help_text="External image URL as alternative to uploaded image")
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
        # Auto-generate slug if empty
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
            
            # Ensure slug is unique
            original_slug = self.slug
            counter = 1
            while Article.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Auto-manage published_at timestamp
        if self.is_published:
            if not self.published_at:
                self.published_at = timezone.now()
        else:
            # When unpublishing, clear published_at so it behaves as a draft
            self.published_at = None
        super().save(*args, **kwargs)

    @property
    def get_featured_image(self) -> str:
        """Return the featured image URL (uploaded file or external URL)."""
        if self.featured_image:
            return self.featured_image.url
        elif self.featured_image_url:
            return self.featured_image_url
        return ""
    
    @property
    def first_image_url(self) -> str:
        """Return the first image URL found in content (best-effort), or empty string."""
        try:
            import re
            if not self.content:
                return ""
            # Search for <img src="..."> first occurrence
            m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', self.content, re.IGNORECASE)
            return m.group(1) if m else ""
        except Exception:
            return ""


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


class NewsletterSubscriber(models.Model):
    """Newsletter subscription management"""
    email = models.EmailField(unique=True, help_text="Subscriber email address")
    subscribed_at = models.DateTimeField(auto_now_add=True, help_text="When the user subscribed")
    is_active = models.BooleanField(default=True, help_text="Whether the subscription is active")
    source = models.CharField(max_length=100, default='website', help_text="Where the subscription came from")
    unsubscribed_at = models.DateTimeField(null=True, blank=True, help_text="When the user unsubscribed")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address when subscribed")
    user_agent = models.TextField(blank=True, help_text="Browser information when subscribed")
    
    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
    
    def unsubscribe(self):
        """Mark subscriber as unsubscribed"""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()


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


class ExportLog(models.Model):
    """Audit log for data exports from admin/backoffice"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    model = models.CharField(max_length=150)
    filter_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Export Log'
        verbose_name_plural = 'Export Logs'

    def __str__(self):
        return f"{self.model} export by {self.user or 'system'} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
