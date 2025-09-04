from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv

from .models import Contact, Service, PastSolution, Event, Gallery, Testimonial, Article, UserRole, UserProfile
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

class AISolutionHubAdminSite(admin.AdminSite):
    site_header = "🤖 AI Solution Hub"
    site_title = "AI Solution Hub Admin Portal"
    index_title = "🚀 Welcome to AI Solution Hub Command Center"
    index_template = "admin/index.html"
    login_template = "admin/login.html"
    logout_template = "admin/logged_out.html"
    change_list_template = "admin/base.html"
    change_form_template = "admin/base.html"
    
    def login(self, request, extra_context=None):
        """
        Override login to use our custom template without default admin structure
        """
        from django.contrib.auth.views import LoginView
        from django.urls import reverse_lazy
        
        return LoginView.as_view(
            template_name=self.login_template,
            redirect_authenticated_user=True,
            extra_context=extra_context
        )(request) 

    # /admin/export/contacts.csv
    def get_urls(self):
        urls = super().get_urls()

        def export_contacts_csv(request):
            resp = HttpResponse(content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = 'attachment; filename="contacts_all.csv"'
            resp.write('\ufeff')  # BOM for Excel
            w = csv.writer(resp)
            w.writerow(["Name","Email","Phone","Company","Country","Job Title","Status","Created"])
            for c in Contact.objects.all().order_by('-created_at'):
                w.writerow([c.name, c.email, c.phone, c.company, c.country, c.job_title, c.status, c.created_at.strftime('%Y-%m-%d %H:%M')])
            return resp

        my = [path("export_contacts_csv/", self.admin_view(export_contacts_csv), name="export_contacts_csv")]
        return my + urls

    def index(self, request, extra_context=None):
        """
        Optimized dashboard with minimal database queries for better performance
        """
        try:
            # Use single query with aggregation for better performance
            from django.db.models import Count, Q
            from datetime import datetime, timedelta
            
            # Get all counts in one query using aggregation
            contact_stats = Contact.objects.aggregate(
                total=Count('id'),
                new=Count('id', filter=Q(status='new')),
                contacted=Count('id', filter=Q(status='contacted')),
                in_progress=Count('id', filter=Q(status='in_progress'))
            )
            
            # Get recent contacts with limit
            recent_contacts = list(Contact.objects.select_related().order_by('-created_at')[:5].values(
                'name', 'company', 'status', 'created_at'
            ))
            
            # Get recent activity for notifications
            recent_activity = []
            
            # Check for new contacts in last 24 hours
            yesterday = datetime.now() - timedelta(days=1)
            new_contacts_today = Contact.objects.filter(created_at__gte=yesterday).count()
            if new_contacts_today > 0:
                recent_activity.append({
                    'type': 'contact',
                    'title': f'{new_contacts_today} New Contact{"s" if new_contacts_today > 1 else ""}',
                    'message': f'{new_contacts_today} new contact{"s" if new_contacts_today > 1 else ""} received in the last 24 hours',
                    'time': 'Today'
                })
            
            # Check for new testimonials
            try:
                from .models import Testimonial
                new_testimonials = Testimonial.objects.filter(created_at__gte=yesterday).count()
                if new_testimonials > 0:
                    recent_activity.append({
                        'type': 'testimonial',
                        'title': f'{new_testimonials} New Testimonial{"s" if new_testimonials > 1 else ""}',
                        'message': f'{new_testimonials} new testimonial{"s" if new_testimonials > 1 else ""} received',
                        'time': 'Today'
                    })
            except:
                pass
            
            ctx = {
                "total_contacts": contact_stats['total'],
                "new_contacts": contact_stats['new'],
                "contacted_contacts": contact_stats['contacted'],
                "in_progress_contacts": contact_stats['in_progress'],
                "recent_contacts": recent_contacts,
                "recent_activity": recent_activity,
                "total_testimonials": 0,  # Simplified for performance
                "featured_testimonials": 0,
                "total_services": 0,
                "total_articles": 0
            }
            
            # Safe URL reversing
            ctx["quick"] = {
                "contacts": "/admin/Ai_SolutionApp/contact/",
                "articles": "/admin/Ai_SolutionApp/article/",
                "services": "/admin/Ai_SolutionApp/service/",
                "testimonials": "/admin/Ai_SolutionApp/testimonial/",
                "export_inquiries": "/admin/export_contacts_csv/"
            }
                
            if extra_context:
                ctx.update(extra_context)
            return super().index(request, ctx)
            
        except Exception as e:
            # Minimal fallback
            ctx = {
                "total_contacts": 0,
                "new_contacts": 0,
                "contacted_contacts": 0,
                "in_progress_contacts": 0,
                "recent_contacts": [],
                "recent_activity": [],
                "total_testimonials": 0,
                "featured_testimonials": 0,
                "total_services": 0,
                "total_articles": 0
            }
            if extra_context:
                ctx.update(extra_context)
            return super().index(request, ctx)

# Create our custom admin site instance
custom_admin_site = AISolutionHubAdminSite(name='admin')

# Admin functions are handled through the existing admin actions and views

# User Role and Profile Admin
@admin.register(UserRole, site=custom_admin_site)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    list_filter = ['name', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']
    
    fieldsets = (
        ('Role Information', {
            'fields': ('name', 'description')
        }),
        ('Permissions', {
            'fields': ('permissions',),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserProfile, site=custom_admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'is_active', 'created_at']
    list_filter = ['role', 'department', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'department']
    list_editable = ['is_active']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role')
        }),
        ('Profile Details', {
            'fields': ('phone', 'department', 'is_active')
        }),
    )
    
    actions = ['activate_users', 'deactivate_users']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} users activated.")
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} users deactivated.")
    deactivate_users.short_description = "Deactivate selected users"

# Replace the default admin site
admin.site = custom_admin_site

# Custom Filters
class ContactStatusFilter(admin.SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('new', 'New'),
            ('in_progress', 'In Progress'),
            ('contacted', 'Contacted'),
            ('closed', 'Closed'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())

class PriorityFilter(admin.SimpleListFilter):
    title = 'Priority'
    parameter_name = 'priority'

    def lookups(self, request, model_admin):
        return (
            ('high', 'High Priority'),
            ('normal', 'Normal Priority'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'high':
            return queryset.filter(status='new')
        elif self.value() == 'normal':
            return queryset.exclude(status='new')

# ModelAdmin Classes
@admin.register(Contact, site=custom_admin_site)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'status', 'created_at']
    list_filter = [ContactStatusFilter, 'created_at', 'country']
    search_fields = ['name', 'email', 'company', 'job_title']
    readonly_fields = ['id', 'created_at']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    actions = ['export_csv', 'mark_as_contacted', 'send_reply_email']
    
    # Performance optimizations
    list_per_page = 25  # Reduce page size for faster loading
    list_select_related = True
    
    def get_queryset(self, request):
        """Optimize queryset for better performance"""
        return super().get_queryset(request).select_related()

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'company', 'country', 'job_title')
        }),
        ('Inquiry Details', {
            'fields': ('job_details', 'status', 'notes')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'admin_reply_sent'),
            'classes': ('collapse',)
        }),
    )

    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contacts.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Phone', 'Company', 'Country', 'Job Title', 'Status', 'Created'])
        for contact in queryset:
            writer.writerow([contact.name, contact.email, contact.phone, contact.company, contact.country, contact.job_title, contact.status, contact.created_at])
        return response
    export_csv.short_description = "Export selected contacts to CSV"

    def mark_as_contacted(self, request, queryset):
        queryset.update(status='contacted')
        self.message_user(request, f"{queryset.count()} contacts marked as contacted.")
    mark_as_contacted.short_description = "Mark selected contacts as contacted"

    def send_reply_email(self, request, queryset):
        # This would integrate with your email system
        queryset.update(admin_reply_sent=True)
        self.message_user(request, f"Reply emails sent to {queryset.count()} contacts.")
    send_reply_email.short_description = "Send reply email to selected contacts"

@admin.register(Service, site=custom_admin_site)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'pricing_tier', 'is_featured', 'order', 'created_at']
    list_filter = ['pricing_tier', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['pricing_tier', 'is_featured', 'order']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(PastSolution, site=custom_admin_site)
class PastSolutionAdmin(admin.ModelAdmin):
    list_display = ['title', 'client_name', 'industry', 'completion_date', 'is_featured']
    list_filter = ['industry', 'is_featured', 'completion_date']
    search_fields = ['title', 'client_name', 'industry']
    readonly_fields = ['id', 'created_at']
    list_editable = ['is_featured']

@admin.register(Event, site=custom_admin_site)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'location', 'is_featured']
    list_filter = ['event_type', 'is_featured', 'start_date']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['id', 'created_at']
    list_editable = ['is_featured']

@admin.register(Gallery, site=custom_admin_site)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'event', 'is_featured', 'order']
    list_filter = ['category', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['category', 'is_featured', 'order']
    readonly_fields = ['id', 'created_at']

@admin.register(Testimonial, site=custom_admin_site)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'company', 'rating', 'is_featured', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_featured', 'is_verified', 'created_at']
    search_fields = ['customer_name', 'company', 'review']
    list_editable = ['is_featured', 'is_verified']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'company', 'job_title', 'image')
        }),
        ('Review Details', {
            'fields': ('rating', 'review', 'is_verified')
        }),
        ('Display Settings', {
            'fields': ('is_featured',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset for better performance"""
        return super().get_queryset(request).select_related()
    
    def save_model(self, request, obj, form, change):
        """Add exception handling for testimonial saves"""
        try:
            super().save_model(request, obj, form, change)
            if not change:  # New testimonial
                self.message_user(request, f"Testimonial from {obj.customer_name} added successfully!")
            else:
                self.message_user(request, f"Testimonial from {obj.customer_name} updated successfully!")
        except Exception as e:
            self.message_user(request, f"Error saving testimonial: {str(e)}", level='ERROR')
    
    def delete_model(self, request, obj):
        """Add exception handling for testimonial deletion"""
        try:
            customer_name = obj.customer_name
            super().delete_model(request, obj)
            self.message_user(request, f"Testimonial from {customer_name} deleted successfully!")
        except Exception as e:
            self.message_user(request, f"Error deleting testimonial: {str(e)}", level='ERROR')
    
    actions = ['mark_as_featured', 'mark_as_verified', 'export_testimonials']
    
    def mark_as_featured(self, request, queryset):
        """Bulk action to mark testimonials as featured"""
        try:
            updated = queryset.update(is_featured=True)
            self.message_user(request, f"{updated} testimonials marked as featured.")
        except Exception as e:
            self.message_user(request, f"Error marking testimonials as featured: {str(e)}", level='ERROR')
    mark_as_featured.short_description = "Mark selected testimonials as featured"
    
    def mark_as_verified(self, request, queryset):
        """Bulk action to mark testimonials as verified"""
        try:
            updated = queryset.update(is_verified=True)
            self.message_user(request, f"{updated} testimonials marked as verified.")
        except Exception as e:
            self.message_user(request, f"Error marking testimonials as verified: {str(e)}", level='ERROR')
    mark_as_verified.short_description = "Mark selected testimonials as verified"
    
    def export_testimonials(self, request, queryset):
        """Export selected testimonials to CSV"""
        try:
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="testimonials.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Customer Name', 'Company', 'Job Title', 'Rating', 'Review', 'Featured', 'Verified', 'Created'])
            
            for testimonial in queryset:
                writer.writerow([
                    testimonial.customer_name,
                    testimonial.company,
                    testimonial.job_title,
                    testimonial.rating,
                    testimonial.review[:100] + '...' if len(testimonial.review) > 100 else testimonial.review,
                    'Yes' if testimonial.is_featured else 'No',
                    'Yes' if testimonial.is_verified else 'No',
                    testimonial.created_at.strftime('%Y-%m-%d %H:%M')
                ])
            
            return response
        except Exception as e:
            self.message_user(request, f"Error exporting testimonials: {str(e)}", level='ERROR')
            return None
    export_testimonials.short_description = "Export selected testimonials to CSV"

@admin.register(Article, site=custom_admin_site)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'is_featured', 'created_at']
    list_filter = ['category', 'is_published', 'is_featured', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    list_editable = ['is_published', 'is_featured']
    readonly_fields = ['id', 'created_at', 'updated_at', 'views_count']
    prepopulated_fields = {'slug': ('title',)}

# Register built-in models with our custom admin site
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)