from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
import csv
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.utils import timezone
from .models import (
    Contact, Service, PastSolution, Event, Gallery, 
    Testimonial, Article, AdminDashboard, SiteSettings
)

# Custom Admin Site
class AISolutionHubAdminSite(admin.AdminSite):
    site_header = "🤖 AI Solution Hub"
    site_title = "AI Solution Hub Admin Portal"
    index_title = "🚀 Welcome to AI Solution Hub Command Center"
    site_url = "/"

admin_site = AISolutionHubAdminSite(name='ai_solution_hub_admin')

# Custom Filters
class ContactStatusFilter(SimpleListFilter):
    title = _('Status')
    parameter_name = 'status_filter'

    def lookups(self, request, model_admin):
        return (
            ('urgent', _('🚨 Urgent (New)')),
            ('active', _('🔄 Active (In Progress)')),
            ('completed', _('✅ Completed')),
            ('closed', _('🔒 Closed')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'urgent':
            return queryset.filter(status='new', created_at__gte=timezone.now() - timedelta(hours=24))
        elif self.value() == 'active':
            return queryset.filter(status='in_progress')
        elif self.value() == 'completed':
            return queryset.filter(status='contacted')
        elif self.value() == 'closed':
            return queryset.filter(status='closed')

class PriorityFilter(SimpleListFilter):
    title = _('Priority Level')
    parameter_name = 'priority'

    def lookups(self, request, model_admin):
        return (
            ('high', _('🔴 High Priority')),
            ('medium', _('🟡 Medium Priority')),
            ('low', _('🟢 Low Priority')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'high':
            return queryset.filter(
                Q(status='new') | 
                Q(company__icontains='enterprise') |
                Q(job_details__icontains='urgent')
            )
        elif self.value() == 'medium':
            return queryset.filter(status='in_progress')
        elif self.value() == 'low':
            return queryset.filter(status='contacted')

# Enhanced Contact Admin
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [
        'priority_indicator', 'name', 'company', 'country', 'job_title', 
        'status_badge', 'admin_reply_sent', 'created_at', 'response_time', 'actions'
    ]
    list_filter = [ContactStatusFilter, PriorityFilter, 'country', 'created_at', 'company']
    search_fields = ['name', 'email', 'company', 'job_details', 'job_title']
    readonly_fields = ['id', 'created_at', 'response_time_display', 'priority_score']
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('👤 Contact Information', {
            'fields': ('name', 'email', 'phone', 'company', 'country'),
            'classes': ('wide',)
        }),
        ('💼 Project Details', {
            'fields': ('job_title', 'job_details'),
            'classes': ('wide',)
        }),
        ('📊 Status & Priority', {
            'fields': ('status', 'priority_score'),
            'classes': ('wide',)
        }),
        ('💬 Admin Reply', {
            'fields': ('notes', 'admin_reply_sent'),
            'classes': ('wide',),
            'description': 'Use the notes field to write your reply. Check "Admin Reply Sent" when you send the email.'
        }),
        ('⏰ System Information', {
            'fields': ('id', 'created_at', 'response_time_display'),
            'classes': ('collapse',)
        }),
    )
    
    def priority_indicator(self, obj):
        if obj.status == 'new' and obj.created_at >= timezone.now() - timedelta(hours=24):
            return format_html('<span style="color: #dc2626;">🔴</span>')
        elif obj.status == 'in_progress':
            return format_html('<span style="color: #d97706;">🟡</span>')
        elif obj.status == 'contacted':
            return format_html('<span style="color: #059669;">🟢</span>')
        return format_html('<span style="color: #6b7280;">⚪</span>')
    priority_indicator.short_description = 'Priority'
    
    def status_badge(self, obj):
        status_colors = {
            'new': '#dc2626',
            'in_progress': '#d97706',
            'contacted': '#059669',
            'closed': '#6b7280'
        }
        status_icons = {
            'new': '🆕',
            'in_progress': '🔄',
            'contacted': '✅',
            'closed': '🔒'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{} {}</span>',
            status_colors.get(obj.status, '#6b7280'),
            status_icons.get(obj.status, '❓'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def response_time(self, obj):
        if obj.status == 'new':
            time_diff = timezone.now() - obj.created_at
            if time_diff.total_seconds() > 86400:  # 24 hours
                return format_html('<span style="color: #dc2626; font-weight: bold;">⚠️ Overdue</span>')
            elif time_diff.total_seconds() > 43200:  # 12 hours
                return format_html('<span style="color: #d97706; font-weight: bold;">⏰ Soon Due</span>')
            else:
                return format_html('<span style="color: #059669;">✅ On Time</span>')
        return '-'
    response_time.short_description = 'Response Time'
    
    def response_time_display(self, obj):
        if obj.status == 'new':
            time_diff = timezone.now() - obj.created_at
            hours = int(time_diff.total_seconds() // 3600)
            minutes = int((time_diff.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m ago"
        return '-'
    response_time_display.short_description = 'Time Since Creation'
    
    def priority_score(self, obj):
        score = 0
        if obj.status == 'new':
            score += 10
        if 'enterprise' in obj.company.lower() or 'corp' in obj.company.lower():
            score += 5
        if 'urgent' in obj.job_details.lower() or 'asap' in obj.job_details.lower():
            score += 3
        if obj.created_at >= timezone.now() - timedelta(hours=12):
            score += 2
        return f"Priority Score: {score}/20"
    
    def actions(self, obj):
        if obj.status == 'new':
            return format_html(
                '<a class="button" style="background: #d97706; color: white; border: none; padding: 6px 12px; border-radius: 6px; text-decoration: none;" href="{}">🔄 Start Progress</a>',
                reverse('admin:ai_solutionapp_contact_change', args=[obj.id])
            )
        elif obj.status == 'in_progress':
            return format_html(
                '<a class="button" style="background: #059669; color: white; border: none; padding: 6px 12px; border-radius: 6px; text-decoration: none;" href="{}">✅ Mark Contacted</a>',
                reverse('admin:ai_solutionapp_contact_change', args=[obj.id])
            )
        elif obj.status == 'contacted':
            return format_html(
                '<a class="button" style="background: #6b7280; color: white; border: none; padding: 6px 12px; border-radius: 6px; text-decoration: none;" href="{}">🔒 Close</a>',
                reverse('admin:ai_solutionapp_contact_change', args=[obj.id])
            )
        return '-'
    actions.short_description = 'Quick Actions'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
    
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="ai_solution_hub_contacts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Priority', 'Name', 'Email', 'Phone', 'Company', 'Country', 
            'Job Title', 'Job Details', 'Status', 'Created At', 'Response Time'
        ])
        
        for contact in queryset:
            priority = '🔴' if contact.status == 'new' and contact.created_at >= timezone.now() - timedelta(hours=24) else '🟡' if contact.status == 'in_progress' else '🟢'
            response_time = self.response_time_display(contact)
            writer.writerow([
                priority, contact.name, contact.email, contact.phone, contact.company,
                contact.country, contact.job_title, contact.job_details,
                contact.get_status_display(), contact.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                response_time
            ])
        
        return response
    export_csv.short_description = "📊 Export to CSV"
    
    actions = ['export_csv', 'mark_as_contacted', 'mark_as_closed', 'mark_as_in_progress']

# Enhanced Service Admin
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'pricing_tier_badge', 'is_featured', 'order', 'created_at', 'service_actions']
    list_filter = ['pricing_tier', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_featured']
    prepopulated_fields = {'title': ('title',)}
    
    fieldsets = (
        ('📝 Service Information', {
            'fields': ('title', 'description', 'features', 'pricing_tier')
        }),
        ('🎯 Display Settings', {
            'fields': ('is_featured', 'order', 'icon_class')
        }),
        ('💰 Pricing Details', {
            'fields': ('price', 'currency', 'billing_cycle'),
            'classes': ('collapse',)
        }),
    )
    
    def pricing_tier_badge(self, obj):
        colors = {
            'basic': '#059669',
            'professional': '#d97706',
            'enterprise': '#dc2626'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.pricing_tier, '#6b7280'),
            obj.get_pricing_tier_display()
        )
    pricing_tier_badge.short_description = 'Pricing Tier'
    
    def service_actions(self, obj):
        return format_html(
            '<a class="button" style="background: #3b82f6; color: white; border: none; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;" href="{}">✏️ Edit</a>',
            reverse('admin:ai_solutionapp_service_change', args=[obj.id])
        )
    service_actions.short_description = 'Actions'

# Enhanced Past Solution Admin
@admin.register(PastSolution)
class PastSolutionAdmin(admin.ModelAdmin):
    list_display = ['title', 'client_name', 'industry_badge', 'completion_date', 'is_featured', 'solution_actions']
    list_filter = ['industry', 'is_featured', 'completion_date', 'technologies_used']
    search_fields = ['title', 'client_name', 'description', 'technologies']
    list_editable = ['is_featured']
    date_hierarchy = 'completion_date'
    
    fieldsets = (
        ('📋 Project Overview', {
            'fields': ('title', 'description', 'client_name', 'client_company')
        }),
        ('🏭 Industry & Technology', {
            'fields': ('industry', 'technologies', 'project_duration')
        }),
        ('📅 Timeline & Results', {
            'fields': ('start_date', 'completion_date', 'results', 'challenges_solved')
        }),
        ('⭐ Display Settings', {
            'fields': ('is_featured', 'featured_image')
        }),
    )
    
    def industry_badge(self, obj):
        colors = {
            'healthcare': '#dc2626',
            'finance': '#059669',
            'education': '#3b82f6',
            'retail': '#d97706',
            'manufacturing': '#7c3aed'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.industry, '#6b7280'),
            obj.get_industry_display()
        )
    industry_badge.short_description = 'Industry'
    
    def solution_actions(self, obj):
        return format_html(
            '<a class="button" style="background: #3b82f6; color: white; border: none; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;" href="{}">✏️ Edit</a>',
            reverse('admin:ai_solutionapp_pastsolution_change', args=[obj.id])
        )
    solution_actions.short_description = 'Actions'

# Enhanced Event Admin
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type_badge', 'start_date', 'end_date', 'location', 'is_virtual', 'is_featured', 'event_actions']
    list_filter = ['event_type', 'is_virtual', 'is_featured', 'start_date', 'location']
    search_fields = ['title', 'description', 'location', 'organizer']
    list_editable = ['is_featured']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('📅 Event Details', {
            'fields': ('title', 'description', 'event_type', 'start_date', 'end_date')
        }),
        ('📍 Location & Registration', {
            'fields': ('location', 'is_virtual', 'virtual_meeting_link', 'registration_required')
        }),
        ('🎯 Display & Features', {
            'fields': ('is_featured', 'featured_image', 'organizer')
        }),
    )
    
    def event_type_badge(self, obj):
        colors = {
            'webinar': '#3b82f6',
            'workshop': '#d97706',
            'conference': '#7c3aed',
            'meetup': '#059669'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.event_type, '#6b7280'),
            obj.get_event_type_display()
        )
    event_type_badge.short_description = 'Event Type'
    
    def event_actions(self, obj):
        return format_html(
            '<a class="button" style="background: #3b82f6; color: white; border: none; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;" href="{}">✏️ Edit</a>',
            reverse('admin:ai_solutionapp_event_change', args=[obj.id])
        )
    event_actions.short_description = 'Actions'

# Enhanced Gallery Admin
@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_badge', 'event', 'is_featured', 'order', 'image_preview', 'gallery_actions']
    list_filter = ['category', 'is_featured', 'created_at', 'event']
    search_fields = ['title', 'description', 'category']
    list_editable = ['order', 'is_featured']
    
    fieldsets = (
        ('🖼️ Image Details', {
            'fields': ('title', 'description', 'image', 'alt_text')
        }),
        ('🏷️ Categorization', {
            'fields': ('category', 'event', 'tags')
        }),
        ('⭐ Display Settings', {
            'fields': ('is_featured', 'order')
        }),
    )
    
    def category_badge(self, obj):
        colors = {
            'events': '#3b82f6',
            'solutions': '#059669',
            'team': '#d97706',
            'office': '#7c3aed'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.category, '#6b7280'),
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 60px; border-radius: 8px; object-fit: cover; border: 2px solid #e5e7eb;" />',
                obj.image.url
            )
        return format_html('<span style="color: #6b7280;">🖼️ No Image</span>')
    image_preview.short_description = 'Preview'
    
    def gallery_actions(self, obj):
        return format_html(
            '<a class="button" style="background: #3b82f6; color: white; border: none; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;" href="{}">✏️ Edit</a>',
            reverse('admin:ai_solutionapp_gallery_change', args=[obj.id])
        )
    gallery_actions.short_description = 'Actions'

# Enhanced Testimonial Admin
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'company', 'rating_stars', 'is_featured', 'is_verified', 'created_at', 'testimonial_actions']
    list_filter = ['rating', 'is_featured', 'is_verified', 'created_at', 'company']
    search_fields = ['customer_name', 'company', 'review']
    list_editable = ['is_featured', 'is_verified']
    
    fieldsets = (
        ('👤 Customer Information', {
            'fields': ('customer_name', 'company', 'job_title', 'profile_image')
        }),
        ('⭐ Rating & Review', {
            'fields': ('rating', 'review', 'review_summary')
        }),
        ('✅ Verification & Display', {
            'fields': ('is_featured', 'is_verified', 'verification_date')
        }),
    )
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html(
            '<span style="font-size: 16px; color: #fbbf24;">{}</span>',
            stars
        )
    rating_stars.short_description = 'Rating'
    
    def testimonial_actions(self, obj):
        return format_html(
            '<a class="button" style="background: #3b82f6; color: white; border: none; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;" href="{}">✏️ Edit</a>',
            reverse('admin:ai_solutionapp_testimonial_change', args=[obj.id])
        )
    testimonial_actions.short_description = 'Actions'

# Enhanced Article Admin
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category_badge', 'is_published', 'is_featured', 'views_count', 'published_at', 'article_actions']
    list_filter = ['category', 'is_published', 'is_featured', 'created_at', 'author']
    search_fields = ['title', 'content', 'excerpt', 'tags']
    list_editable = ['is_published', 'is_featured']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('📝 Content', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image')
        }),
        ('🏷️ Metadata', {
            'fields': ('author', 'category', 'tags', 'seo_description')
        }),
        ('📊 Publication', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('📈 Analytics', {
            'fields': ('views_count', 'reading_time'),
            'classes': ('collapse',)
        }),
    )
    
    def category_badge(self, obj):
        colors = {
            'ai': '#dc2626',
            'technology': '#3b82f6',
            'business': '#059669',
            'innovation': '#d97706',
            'tutorial': '#7c3aed'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.category, '#6b7280'),
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    
    def article_actions(self, obj):
        return format_html(
            '<a class="button" style="background: #3b82f6; color: white; border: none; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;" href="{}">✏️ Edit</a>',
            reverse('admin:ai_solutionapp_article_change', args=[obj.id])
        )
    article_actions.short_description = 'Actions'

# Enhanced Admin Dashboard Admin
@admin.register(AdminDashboard)
class AdminDashboardAdmin(admin.ModelAdmin):
    list_display = ['dashboard_title', 'last_updated', 'dashboard_actions']
    readonly_fields = ['last_updated']
    
    fieldsets = (
        ('📊 Dashboard Configuration', {
            'fields': ('dashboard_title', 'welcome_message', 'quick_stats_enabled')
        }),
        ('🎯 Analytics Settings', {
            'fields': ('chart_types', 'refresh_interval', 'export_formats')
        }),
    )
    
    def has_add_permission(self, request):
        return not AdminDashboard.objects.exists()
    
    def dashboard_actions(self, obj):
        return format_html(
            '<a class="button" style="background: #3b82f6; color: white; border: none; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;" href="{}">✏️ Edit</a>',
            reverse('admin:ai_solutionapp_admindashboard_change', args=[obj.id])
        )
    dashboard_actions.short_description = 'Actions'

# Enhanced Site Settings Admin
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email', 'maintenance_mode', 'updated_at', 'settings_actions']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('🌐 Basic Settings', {
            'fields': ('site_name', 'site_description', 'contact_email', 'phone_number')
        }),
        ('🔧 Technical Settings', {
            'fields': ('maintenance_mode', 'google_analytics_id', 'recaptcha_enabled')
        }),
        ('📱 Social Media', {
            'fields': ('social_links', 'footer_links'),
            'classes': ('collapse',)
        }),
        ('🎨 Appearance', {
            'fields': ('logo', 'favicon', 'primary_color', 'secondary_color'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def settings_actions(self, obj):
        return format_html(
            '<a class="button" style="background: #3b82f6; color: white; border: none; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px;" href="{}">✏️ Edit</a>',
            reverse('admin:ai_solutionapp_sitesettings_change', args=[obj.id])
        )
    settings_actions.short_description = 'Actions'

# Custom admin actions
def mark_as_contacted(modeladmin, request, queryset):
    queryset.update(status='contacted')
    modeladmin.message_user(request, f"✅ {queryset.count()} contact(s) marked as contacted successfully!")
mark_as_contacted.short_description = "✅ Mark as Contacted"

def mark_as_closed(modeladmin, request, queryset):
    queryset.update(status='closed')
    modeladmin.message_user(request, f"🔒 {queryset.count()} contact(s) closed successfully!")
mark_as_closed.short_description = "🔒 Close Contacts"

def mark_as_in_progress(modeladmin, request, queryset):
    queryset.update(status='in_progress')
    modeladmin.message_user(request, f"🔄 {queryset.count()} contact(s) marked as in progress!")
mark_as_in_progress.short_description = "🔄 Mark as In Progress"

def export_urgent_contacts(modeladmin, request, queryset):
    urgent_contacts = Contact.objects.filter(
        status='new',
        created_at__gte=timezone.now() - timedelta(hours=24)
    )
    return ContactAdmin.export_csv(modeladmin, request, urgent_contacts)
export_urgent_contacts.short_description = "🚨 Export Urgent Contacts"

def send_reply_email(modeladmin, request, queryset):
    """Send reply email to selected contacts"""
    from django.core.mail import send_mail
    from django.conf import settings
    
    success_count = 0
    for contact in queryset:
        if contact.notes and not contact.admin_reply_sent:
            try:
                # Send reply email to customer
                reply_subject = f'Re: Your inquiry to AI Solution Hub - {contact.job_title}'
                reply_message = f"""
Dear {contact.name},

Thank you for your inquiry regarding: {contact.job_title}

{contact.notes}

If you have any further questions, please don't hesitate to contact us.

Best regards,
AI Solution Hub Support Team
AiSolutionhubsupport@gmail.com
                """
                
                send_mail(
                    reply_subject,
                    reply_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [contact.email],
                    fail_silently=False,
                )
                
                # Mark as replied
                contact.admin_reply_sent = True
                contact.status = 'contacted'
                contact.save()
                success_count += 1
                
            except Exception as e:
                modeladmin.message_user(request, f"❌ Failed to send email to {contact.email}: {str(e)}", level='ERROR')
    
    if success_count > 0:
        modeladmin.message_user(request, f"✅ Successfully sent {success_count} reply email(s)!")
    else:
        modeladmin.message_user(request, "⚠️ No emails sent. Make sure contacts have notes and haven't been replied to yet.")
        
send_reply_email.short_description = "📧 Send Reply Email"

# Register custom actions
ContactAdmin.actions = list(ContactAdmin.actions) + [
    mark_as_contacted, 
    mark_as_closed, 
    mark_as_in_progress,
    export_urgent_contacts,
    send_reply_email
]

# Custom admin site configuration
admin.site.site_header = "🤖 AI Solution Hub"
admin.site.site_title = "AI Solution Hub Admin Portal"
admin.site.index_title = "🚀 Welcome to AI Solution Hub Command Center"

# Add custom CSS for admin interface
class Media:
    css = {
        'all': ('admin/css/custom_admin.css',)
    }
    js = ('admin/js/custom_admin.js',)

# Apply custom media to all admin classes
for admin_class in [ContactAdmin, ServiceAdmin, PastSolutionAdmin, EventAdmin, 
                   GalleryAdmin, TestimonialAdmin, ArticleAdmin, AdminDashboardAdmin, SiteSettingsAdmin]:
    admin_class.Media = Media
