from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import timedelta, datetime
import csv
import json

from .models import (
    Contact, Service, PastSolution, Event, Gallery, Testimonial, 
    Article, NewsletterSubscriber, UserProfile, UserRole, ExportLog, SiteSettings
)
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.forms import PasswordResetForm
from .admin import custom_admin_site
from .export_functions import (
    export_gallery_csv, export_testimonials_csv, export_articles_csv, 
    export_services_csv, export_past_solutions_csv
)

def is_super_admin(user):
    """Check if user is super admin with full access"""
    return user.is_authenticated and user.is_superuser

def is_admin_user(user):
    """Check if user has admin privileges (super admin or normal admin)"""
    if not user.is_authenticated:
        return False
    
    # Super admin has all access
    if user.is_superuser:
        return True
    
    # Check if user has admin role
    try:
        profile = user.profile
        return profile.role.name in ['admin', 'superadmin']
    except:
        return False

def is_content_manager(user):
    """Check if user can manage content (super admin, admin, or content manager)"""
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    try:
        profile = user.profile
        return profile.role.name in ['admin', 'superadmin', 'content_manager']
    except:
        return False

def is_analyst(user):
    """Check if user can view analytics and reports"""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        profile = user.profile
        return profile.role and profile.role.name in ['admin', 'superadmin', 'analyst']
    except Exception:
        return False
@login_required
@user_passes_test(is_admin_user)
def kpi_summary(request):
    """Lightweight KPIs for live refresh on dashboard."""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    data = {
        'total_inquiries': Contact.objects.count(),
        'weekly_inquiries': Contact.objects.filter(created_at__date__gte=week_ago).count(),
        'total_subscribers': NewsletterSubscriber.objects.filter(is_active=True).count(),
        'new_inquiries': Contact.objects.filter(status='new').count(),
        'contacted_inquiries': Contact.objects.filter(status='contacted').count(),
        'in_progress_inquiries': Contact.objects.filter(status='in_progress').count(),
        'closed_inquiries': Contact.objects.filter(status='closed').count(),
    }
    return JsonResponse(data)
    
    if user.is_superuser:
        return True
    
    try:
        profile = user.profile
        return profile.role.name in ['admin', 'superadmin', 'analyst']
    except:
        return False

@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):
    """Admin dashboard with KPI cards and analytics"""
    try:
        # Get date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Calculate KPIs
        total_inquiries = Contact.objects.count()
        new_inquiries = Contact.objects.filter(status='new').count()
        contacted_inquiries = Contact.objects.filter(status='contacted').count()
        in_progress_inquiries = Contact.objects.filter(status='in_progress').count()
        closed_inquiries = Contact.objects.filter(status='closed').count()
        
        # Weekly inquiries
        weekly_inquiries = Contact.objects.filter(created_at__date__gte=week_ago).count()
        
        # Top countries
        top_countries = Contact.objects.values('country').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Total subscribers
        total_subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()
        
        # Recent inquiries (last 5)
        recent_inquiries = Contact.objects.select_related().order_by('-created_at')[:5]
        
        # Top inquiries (by company/status)
        top_inquiries = Contact.objects.select_related().order_by('-created_at')[:5]
        
        # Recent activities
        recent_activities = []
        
        # Check for new inquiries today
        today_inquiries = Contact.objects.filter(created_at__date=today).count()
        if today_inquiries > 0:
            recent_activities.append({
                'icon': 'envelope',
                'text': f'{today_inquiries} new inquiry{"s" if today_inquiries > 1 else ""} received today',
                'time': 'Today'
            })
        
        # Check for new subscribers
        today_subscribers = NewsletterSubscriber.objects.filter(subscribed_at__date=today).count()
        if today_subscribers > 0:
            recent_activities.append({
                'icon': 'user-plus',
                'text': f'{today_subscribers} new subscriber{"s" if today_subscribers > 1 else ""} joined today',
                'time': 'Today'
            })
        
        # Check for new testimonials
        today_testimonials = Testimonial.objects.filter(created_at__date=today).count()
        if today_testimonials > 0:
            recent_activities.append({
                'icon': 'quote-left',
                'text': f'{today_testimonials} new testimonial{"s" if today_testimonials > 1 else ""} received',
                'time': 'Today'
            })
        
        # Calculate conversion ratio (contacted / total)
        conversion_ratio = (contacted_inquiries / total_inquiries * 100) if total_inquiries > 0 else 0
        
        # Mock revenue data (you can replace with actual revenue tracking)
        total_revenue = 56562  # This should come from actual revenue tracking
        
        # Inquiry statistics for table
        inquiry_statistics = Contact.objects.select_related().order_by('-created_at')[:5]
        
        context = {
            'total_inquiries': total_inquiries,
            'new_inquiries': new_inquiries,
            'contacted_inquiries': contacted_inquiries,
            'in_progress_inquiries': in_progress_inquiries,
            'closed_inquiries': closed_inquiries,
            'weekly_inquiries': weekly_inquiries,
            'total_subscribers': total_subscribers,
            'conversion_ratio': round(conversion_ratio, 2),
            'total_revenue': total_revenue,
            'top_countries': top_countries,
            'recent_inquiries': recent_inquiries,
            'top_inquiries': top_inquiries,
            'recent_activities': recent_activities,
            'inquiry_statistics': inquiry_statistics,
            'successful_inquiries': contacted_inquiries,
            'pending_inquiries': in_progress_inquiries,
            'rejected_inquiries': closed_inquiries,
            'website_inquiries': int(total_inquiries * 0.4),
            'social_inquiries': int(total_inquiries * 0.3),
            'referral_inquiries': int(total_inquiries * 0.2),
            'other_inquiries': int(total_inquiries * 0.1),
        }
        
        return render(request, 'admin/admin_dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return render(request, 'admin/admin_dashboard.html', {
            'total_inquiries': 0,
            'new_inquiries': 0,
            'contacted_inquiries': 0,
            'in_progress_inquiries': 0,
            'closed_inquiries': 0,
            'weekly_inquiries': 0,
            'total_subscribers': 0,
            'conversion_ratio': 0,
            'total_revenue': 0,
            'top_countries': [],
            'recent_inquiries': [],
            'top_inquiries': [],
            'recent_activities': [],
            'inquiry_statistics': [],
        })

@login_required
@user_passes_test(is_admin_user)
def inquiries_list(request):
    """List all inquiries with search and filters"""
    try:
        # Get filter parameters
        search = request.GET.get('search', '')
        status = request.GET.get('status', '')
        country = request.GET.get('country', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Build queryset
        queryset = Contact.objects.all()
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(company__icontains=search) |
                Q(job_details__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Order by newest first
        queryset = queryset.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get('page')
        inquiries = paginator.get_page(page_number)
        
        # Get unique countries for filter dropdown
        countries = Contact.objects.values_list('country', flat=True).distinct().order_by('country')
        
        context = {
            'inquiries': inquiries,
            'countries': countries,
            'search': search,
            'status': status,
            'country': country,
            'date_from': date_from,
            'date_to': date_to,
            'total_count': paginator.count,
        }
        
        return render(request, 'admin/admin_inquiries_list.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading inquiries: {str(e)}')
        return render(request, 'admin/admin_inquiries_list.html', {
            'inquiries': [],
            'countries': [],
            'search': '',
            'status': '',
            'country': '',
            'date_from': '',
            'date_to': '',
            'total_count': 0,
        })

@login_required
@user_passes_test(is_admin_user)
def inquiry_detail(request, inquiry_id):
    """Detail view for a specific inquiry"""
    try:
        inquiry = get_object_or_404(Contact, id=inquiry_id)
        
        if request.method == 'POST':
            # Handle status update
            new_status = request.POST.get('status')
            if new_status in ['new', 'in_progress', 'contacted', 'closed']:
                inquiry.status = new_status
                inquiry.save()
                messages.success(request, f'Inquiry status updated to {new_status}')
                return redirect('admin:inquiry_detail', inquiry_id=inquiry_id)
            
            # Handle notes update
            notes = request.POST.get('notes')
            if notes is not None:
                inquiry.notes = notes
                inquiry.save()
                messages.success(request, 'Notes updated successfully')
                return redirect('admin:inquiry_detail', inquiry_id=inquiry_id)
        
        context = {
            'inquiry': inquiry,
        }
        
        return render(request, 'admin/admin_inquiry_detail.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading inquiry: {str(e)}')
        return redirect('admin:inquiries_list')

@login_required
@user_passes_test(is_admin_user)
def subscribers(request):
    """Manage newsletter subscribers"""
    try:
        # Get filter parameters
        search = request.GET.get('search', '')
        status = request.GET.get('status', '')
        source = request.GET.get('source', '')
        
        # Build queryset
        queryset = NewsletterSubscriber.objects.all()
        
        # Apply filters
        if search:
            queryset = queryset.filter(email__icontains=search)
        
        if status:
            queryset = queryset.filter(is_active=(status == 'active'))
        
        if source:
            queryset = queryset.filter(source=source)
        
        # Order by newest first
        queryset = queryset.order_by('-subscribed_at')
        
        # Pagination
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get('page')
        subscribers = paginator.get_page(page_number)
        
        # Get unique sources for filter dropdown
        sources = NewsletterSubscriber.objects.values_list('source', flat=True).distinct().order_by('source')
        
        context = {
            'subscribers': subscribers,
            'sources': sources,
            'search': search,
            'status': status,
            'source': source,
            'total_count': paginator.count,
        }
        
        return render(request, 'admin/admin_subscribers.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading subscribers: {str(e)}')
        return render(request, 'admin/admin_subscribers.html', {
            'subscribers': [],
            'sources': [],
            'search': '',
            'status': '',
            'source': '',
            'total_count': 0,
        })

@login_required
@user_passes_test(is_admin_user)
def events(request):
    """Manage events"""
    try:
        # Handle POST requests for creating/updating events
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'create':
                # Create new event
                title = request.POST.get('title', '').strip()
                description = request.POST.get('description', '').strip()
                event_type = request.POST.get('event_type', '')
                start_date = request.POST.get('start_date', '').strip()
                end_date = request.POST.get('end_date', '').strip()
                location = request.POST.get('location', '').strip()
                is_virtual = request.POST.get('is_virtual') == 'on'
                registration_link = request.POST.get('registration_link', '').strip()
                max_participants = request.POST.get('max_participants', '').strip()
                featured_image = request.FILES.get('featured_image')
                featured_image_url = request.POST.get('featured_image_url', '').strip()
                is_featured = request.POST.get('is_featured') == 'on'
                
                if not title or not description or not event_type or not start_date or not end_date:
                    messages.error(request, 'Please fill in all required fields')
                else:
                    from datetime import datetime
                    try:
                        start_datetime = datetime.fromisoformat(start_date.replace('T', ' '))
                        end_datetime = datetime.fromisoformat(end_date.replace('T', ' '))
                        
                        event = Event.objects.create(
                            title=title,
                            description=description,
                            event_type=event_type,
                            start_date=start_datetime,
                            end_date=end_datetime,
                            location=location if location else None,
                            is_virtual=is_virtual,
                            registration_link=registration_link if registration_link else None,
                            max_participants=int(max_participants) if max_participants else None,
                            featured_image=featured_image,
                            featured_image_url=featured_image_url if featured_image_url else None,
                            is_featured=is_featured
                        )
                        
                        messages.success(request, f'Event "{title}" created successfully')
                        return redirect('admin:events')
                    except ValueError as e:
                        messages.error(request, f'Invalid date format: {str(e)}')
            
            elif action == 'update':
                # Update existing event
                event_id = request.POST.get('event_id')
                try:
                    event = Event.objects.get(id=event_id)
                    
                    event.title = request.POST.get('title', '').strip()
                    event.description = request.POST.get('description', '').strip()
                    event.event_type = request.POST.get('event_type', '')
                    event.location = request.POST.get('location', '').strip()
                    event.is_virtual = request.POST.get('is_virtual') == 'on'
                    event.registration_link = request.POST.get('registration_link', '').strip()
                    event.is_featured = request.POST.get('is_featured') == 'on'
                    
                    # Handle dates
                    start_date = request.POST.get('start_date', '').strip()
                    end_date = request.POST.get('end_date', '').strip()
                    if start_date and end_date:
                        from datetime import datetime
                        try:
                            event.start_date = datetime.fromisoformat(start_date.replace('T', ' '))
                            event.end_date = datetime.fromisoformat(end_date.replace('T', ' '))
                        except ValueError:
                            messages.error(request, 'Invalid date format')
                            return redirect('admin:events')
                    
                    # Handle max participants
                    max_participants = request.POST.get('max_participants', '').strip()
                    event.max_participants = int(max_participants) if max_participants else None
                    
                    # Handle image updates
                    if 'featured_image' in request.FILES:
                        event.featured_image = request.FILES['featured_image']
                        event.featured_image_url = None  # Clear URL if file uploaded
                    elif request.POST.get('featured_image_url', '').strip():
                        event.featured_image_url = request.POST.get('featured_image_url', '').strip()
                        event.featured_image = None  # Clear file if URL provided
                    
                    event.save()
                    messages.success(request, f'Event "{event.title}" updated successfully')
                    return redirect('admin:events')
                    
                except Event.DoesNotExist:
                    messages.error(request, 'Event not found')
            
            elif action == 'delete':
                # Delete event
                event_id = request.POST.get('event_id')
                try:
                    event = Event.objects.get(id=event_id)
                    event_title = event.title
                    event.delete()
                    messages.success(request, f'Event "{event_title}" deleted successfully')
                    return redirect('admin:events')
                except Event.DoesNotExist:
                    messages.error(request, 'Event not found')
        
        # Get filter parameters
        search = request.GET.get('search', '')
        event_type = request.GET.get('event_type', '')
        featured = request.GET.get('featured', '')
        upcoming = request.GET.get('upcoming', '')
        
        # Build queryset
        queryset = Event.objects.all()
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        if featured:
            queryset = queryset.filter(is_featured=(featured == 'yes'))
        
        if upcoming:
            if upcoming == 'yes':
                queryset = queryset.filter(start_date__gte=timezone.now())
            elif upcoming == 'no':
                queryset = queryset.filter(start_date__lt=timezone.now())
        
        # Order by start date
        queryset = queryset.order_by('start_date')
        
        # Pagination
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get('page')
        events = paginator.get_page(page_number)
        
        context = {
            'events': events,
            'search': search,
            'event_type': event_type,
            'featured': featured,
            'upcoming': upcoming,
            'total_count': paginator.count,
        }
        
        return render(request, 'admin/admin_events.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading events: {str(e)}')
        return render(request, 'admin/admin_events.html', {
            'events': [],
            'search': '',
            'event_type': '',
            'featured': '',
            'upcoming': '',
            'total_count': 0,
        })

@login_required
@user_passes_test(is_admin_user)
def export_events_csv(request):
    """Export events to CSV respecting current filters and log export."""
    # Build queryset with same filters as events()
    search = request.GET.get('search', '')
    event_type = request.GET.get('event_type', '')
    featured = request.GET.get('featured', '')
    upcoming = request.GET.get('upcoming', '')

    queryset = Event.objects.all()
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )
    if event_type:
        queryset = queryset.filter(event_type=event_type)
    if featured:
        queryset = queryset.filter(is_featured=(featured == 'yes'))
    if upcoming:
        if upcoming == 'yes':
            queryset = queryset.filter(start_date__gte=timezone.now())
        elif upcoming == 'no':
            queryset = queryset.filter(start_date__lt=timezone.now())

    # Prepare CSV response
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="events_export.csv"'
    writer = csv.writer(response)
    # Header with filter summary first line
    filter_summary = json.dumps({
        'search': search,
        'event_type': event_type,
        'featured': featured,
        'upcoming': upcoming,
    })
    writer.writerow([f'Filters: {filter_summary}'])
    writer.writerow(['Title', 'Type', 'Start', 'End', 'Location', 'Virtual', 'Featured', 'Registration Link'])

    for ev in queryset.order_by('start_date'):
        writer.writerow([
            ev.title,
            ev.event_type,
            ev.start_date.strftime('%Y-%m-%d %H:%M'),
            ev.end_date.strftime('%Y-%m-%d %H:%M'),
            ev.location or '',
            'Yes' if ev.is_virtual else 'No',
            'Yes' if ev.is_featured else 'No',
            ev.registration_link or '',
        ])

    # Audit log
    try:
        ExportLog.objects.create(
            user=request.user,
            model_name='Event',
            exported_at=timezone.now(),
            filter_summary=filter_summary,
            record_count=queryset.count(),
        )
    except Exception:
        pass

    return response

@login_required
def notifications_count(request):
    """Return a small count for notifications (e.g., new inquiries + subscribers today)."""
    today = timezone.now().date()
    count = 0
    try:
        # New inquiries today
        count += Contact.objects.filter(created_at__date=today, form_type='contact').count()
        
        # New demo requests today
        count += Contact.objects.filter(created_at__date=today, form_type='demo').count()
        
        # New subscribers today
        count += NewsletterSubscriber.objects.filter(subscribed_at__date=today, is_active=True).count()
        
        # Upcoming events in next 7 days (for demo scheduled notifications)
        week_from_now = today + timedelta(days=7)
        upcoming_events = Event.objects.filter(
            start_date__date__gte=today,
            start_date__date__lte=week_from_now
        ).count()
        count += upcoming_events

    except Exception:
        count = 0
    return JsonResponse({'count': count})

@login_required
def notifications_list(request):
    """Return a small list of recent activities for navbar dropdown."""
    today = timezone.now().date()
    items = []
    try:
        # Recent inquiries
        new_contacts = Contact.objects.filter(form_type='contact').order_by('-created_at')[:3]
        for c in new_contacts:
            items.append({
                'icon': 'envelope',
                'text': f'Inquiry from {c.name or c.email}',
                'time': c.created_at.strftime('%b %d %H:%M'),
                'type': 'inquiry'
            })
        
        # Recent demo requests
        demo_requests = Contact.objects.filter(form_type='demo').order_by('-created_at')[:3]
        for d in demo_requests:
            items.append({
                'icon': 'calendar-check',
                'text': f'Demo request from {d.name or d.email}',
                'time': d.created_at.strftime('%b %d %H:%M'),
                'type': 'demo'
            })
        
        # Recent subscribers
        subs = NewsletterSubscriber.objects.filter(is_active=True).order_by('-subscribed_at')[:2]
        for s in subs:
            items.append({
                'icon': 'user-plus',
                'text': f'New subscriber {s.email}',
                'time': s.subscribed_at.strftime('%b %d %H:%M'),
                'type': 'subscriber'
            })
        
        # Upcoming events (next 7 days)
        week_from_now = today + timedelta(days=7)
        upcoming_events = Event.objects.filter(
            start_date__date__gte=today,
            start_date__date__lte=week_from_now
        ).order_by('start_date')[:3]
        for e in upcoming_events:
            items.append({
                'icon': 'calendar-alt',
                'text': f'Upcoming: {e.title}',
                'time': e.start_date.strftime('%b %d %H:%M'),
                'type': 'event'
            })
        
        # Sort by time and limit to 8 items
        items.sort(key=lambda x: x['time'], reverse=True)
        items = items[:8]
    except Exception:
        items = []
    return JsonResponse({'items': items})

@login_required
@user_passes_test(is_content_manager)
def gallery(request):
    """Manage gallery images"""
    try:
        # Get filter parameters
        search = request.GET.get('search', '')
        category = request.GET.get('category', '')
        featured = request.GET.get('featured', '')
        
        # Build queryset
        queryset = Gallery.objects.all()
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(alt_text__icontains=search)
            )
        
        if category:
            queryset = queryset.filter(category=category)
        
        if featured:
            queryset = queryset.filter(is_featured=(featured == 'yes'))
        
        # Order by order field, then by created date
        queryset = queryset.order_by('order', '-created_at')
        
        # Pagination
        paginator = Paginator(queryset, 24)  # 24 for grid layout
        page_number = request.GET.get('page')
        gallery_items = paginator.get_page(page_number)
        
        context = {
            'gallery_items': gallery_items,
            'search': search,
            'category': category,
            'featured': featured,
            'total_count': paginator.count,
        }
        
        return render(request, 'admin/admin_gallery.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading gallery: {str(e)}')
        return render(request, 'admin/admin_gallery.html', {
            'gallery_items': [],
            'search': '',
            'category': '',
            'featured': '',
            'total_count': 0,
        })

@login_required
@user_passes_test(is_content_manager)
@csrf_exempt
@require_http_methods(["POST"])
def add_gallery_image(request):
    """Add new gallery image via AJAX"""
    try:
        # Get form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'other')
        alt_text = request.POST.get('alt_text', '').strip()
        tags = request.POST.get('tags', '').strip()
        order = request.POST.get('order', 0)
        is_featured = request.POST.get('is_featured') == 'on'
        is_hero_image = request.POST.get('is_hero_image') == 'on'
        
        # Get uploaded file
        image_file = request.FILES.get('image')
        
        if not image_file:
            return JsonResponse({'success': False, 'error': 'No image file provided'})
        
        if not title:
            return JsonResponse({'success': False, 'error': 'Title is required'})
        
        # Auto-generate order if not provided or 0
        if not order or int(order) == 0:
            max_order = Gallery.objects.aggregate(max_order=Max('order'))['max_order'] or 0
            order = max_order + 1
        
        # Process tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Create gallery item
        gallery_item = Gallery.objects.create(
            title=title,
            description=description,
            category=category,
            alt_text=alt_text or f"{title} - AI Solution Hub Gallery",
            tags=tag_list,
            order=int(order),
            is_featured=is_featured,
            is_hero_image=is_hero_image,
            image=image_file
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Image uploaded successfully',
            'gallery_id': str(gallery_item.id)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_content_manager)
@csrf_exempt
@require_http_methods(["POST"])
def toggle_gallery_featured(request):
    """Toggle featured status of gallery image"""
    try:
        gallery_id = request.POST.get('gallery_id')
        if not gallery_id:
            return JsonResponse({'success': False, 'error': 'Gallery ID required'})
        
        gallery_item = get_object_or_404(Gallery, id=gallery_id)
        gallery_item.is_featured = not gallery_item.is_featured
        gallery_item.save()
        
        return JsonResponse({
            'success': True, 
            'is_featured': gallery_item.is_featured
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_content_manager)
@csrf_exempt
@require_http_methods(["POST"])
def delete_gallery_image(request):
    """Delete gallery image"""
    try:
        gallery_id = request.POST.get('gallery_id')
        if not gallery_id:
            return JsonResponse({'success': False, 'error': 'Gallery ID required'})
        
        gallery_item = get_object_or_404(Gallery, id=gallery_id)
        title = gallery_item.title
        gallery_item.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Image "{title}" deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_content_manager)
def testimonials(request):
    """Manage testimonials"""
    try:
        # Get filter parameters
        search = request.GET.get('search', '')
        rating = request.GET.get('rating', '')
        featured = request.GET.get('featured', '')
        verified = request.GET.get('verified', '')
        
        # Build queryset
        queryset = Testimonial.objects.all()
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(customer_name__icontains=search) |
                Q(company__icontains=search) |
                Q(review__icontains=search)
            )
        
        if rating:
            queryset = queryset.filter(rating=rating)
        
        if featured:
            queryset = queryset.filter(is_featured=(featured == 'yes'))
        
        if verified:
            queryset = queryset.filter(is_verified=(verified == 'yes'))
        
        # Order by featured first, then by created date
        queryset = queryset.order_by('-is_featured', '-created_at')
        
        # Pagination
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get('page')
        testimonials = paginator.get_page(page_number)
        
        context = {
            'testimonials': testimonials,
            'search': search,
            'rating': rating,
            'featured': featured,
            'verified': verified,
            'total_count': paginator.count,
        }
        
        return render(request, 'admin/admin_testimonials.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading testimonials: {str(e)}')
        return render(request, 'admin/admin_testimonials.html', {
            'testimonials': [],
            'search': '',
            'rating': '',
            'featured': '',
            'verified': '',
            'total_count': 0,
        })

@login_required
@user_passes_test(is_content_manager)
def articles(request):
    """Manage blog articles"""
    try:
        # Handle POST requests for creating/updating articles
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'create':
                # Create new article
                title = request.POST.get('title', '').strip()
                slug = request.POST.get('slug', '').strip()
                excerpt = request.POST.get('excerpt', '').strip()
                content = request.POST.get('content', '').strip()
                category = request.POST.get('category', '')
                featured_image = request.FILES.get('featured_image')
                featured_image_url = request.POST.get('featured_image_url', '').strip()
                is_published = request.POST.get('is_published') == 'on'
                is_featured = request.POST.get('is_featured') == 'on'
                
                if not title or not slug or not excerpt or not content or not category:
                    messages.error(request, 'Please fill in all required fields')
                else:
                    # Auto-generate slug if not provided
                    if not slug:
                        from django.utils.text import slugify
                        slug = slugify(title)
                    
                    # Check if slug is unique
                    if Article.objects.filter(slug=slug).exists():
                        slug = f"{slug}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                    
                    article = Article.objects.create(
                        title=title,
                        slug=slug,
                        excerpt=excerpt,
                        content=content,
                        category=category,
                        author=request.user,
                        featured_image=featured_image,
                        featured_image_url=featured_image_url if featured_image_url else None,
                        is_published=is_published,
                        is_featured=is_featured
                    )
                    
                    messages.success(request, f'Article "{title}" created successfully')
                    return redirect('admin:articles')
            
            elif action == 'update':
                # Update existing article
                article_id = request.POST.get('article_id')
                try:
                    article = Article.objects.get(id=article_id)
                    
                    article.title = request.POST.get('title', '').strip()
                    article.slug = request.POST.get('slug', '').strip()
                    article.excerpt = request.POST.get('excerpt', '').strip()
                    article.content = request.POST.get('content', '').strip()
                    article.category = request.POST.get('category', '')
                    article.is_published = request.POST.get('is_published') == 'on'
                    article.is_featured = request.POST.get('is_featured') == 'on'
                    
                    # Handle image updates
                    if 'featured_image' in request.FILES:
                        article.featured_image = request.FILES['featured_image']
                        article.featured_image_url = None  # Clear URL if file uploaded
                    elif request.POST.get('featured_image_url', '').strip():
                        article.featured_image_url = request.POST.get('featured_image_url', '').strip()
                        article.featured_image = None  # Clear file if URL provided
                    
                    article.save()
                    messages.success(request, f'Article "{article.title}" updated successfully')
                    return redirect('admin:articles')
                    
                except Article.DoesNotExist:
                    messages.error(request, 'Article not found')

            elif action == 'toggle_publish':
                # Toggle publish status quickly
                article_id = request.POST.get('article_id')
                try:
                    article = Article.objects.get(id=article_id)
                    article.is_published = not article.is_published
                    article.save()
                    state = 'published' if article.is_published else 'unpublished'
                    messages.success(request, f'Article "{article.title}" {state}')
                    return redirect('admin:articles')
                except Article.DoesNotExist:
                    messages.error(request, 'Article not found')
            
            elif action == 'delete':
                # Delete article
                article_id = request.POST.get('article_id')
                try:
                    article = Article.objects.get(id=article_id)
                    article_title = article.title
                    article.delete()
                    messages.success(request, f'Article "{article_title}" deleted successfully')
                    return redirect('admin:articles')
                except Article.DoesNotExist:
                    messages.error(request, 'Article not found')

            elif action == 'toggle_feature':
                # Toggle featured flag
                article_id = request.POST.get('article_id')
                try:
                    article = Article.objects.get(id=article_id)
                    article.is_featured = not article.is_featured
                    article.save()
                    state = 'featured' if article.is_featured else 'unfeatured'
                    messages.success(request, f'Article "{article.title}" {state}')
                    return redirect('admin:articles')
                except Article.DoesNotExist:
                    messages.error(request, 'Article not found')

            elif action == 'duplicate':
                # Duplicate article (as draft)
                article_id = request.POST.get('article_id')
                try:
                    original = Article.objects.get(id=article_id)
                    from django.utils.text import slugify
                    base_slug = slugify(f"{original.slug}-copy")
                    new_slug = base_slug
                    counter = 1
                    while Article.objects.filter(slug=new_slug).exists():
                        new_slug = f"{base_slug}-{counter}"
                        counter += 1
                    dup = Article.objects.create(
                        title=f"{original.title} (Copy)",
                        slug=new_slug,
                        excerpt=original.excerpt,
                        content=original.content,
                        author=request.user,
                        featured_image=original.featured_image if original.featured_image else None,
                        featured_image_url=original.featured_image_url,
                        tags=original.tags,
                        category=original.category,
                        is_published=False,
                        is_featured=original.is_featured,
                    )
                    messages.success(request, f'Article "{original.title}" duplicated')
                    return redirect('admin:articles')
                except Article.DoesNotExist:
                    messages.error(request, 'Article not found')
        
        # Get filter parameters
        search = request.GET.get('search', '')
        category = request.GET.get('category', '')
        status = request.GET.get('status', '')
        featured = request.GET.get('featured', '')
        
        # Build queryset
        queryset = Article.objects.select_related('author')
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(excerpt__icontains=search)
            )
        
        if category:
            queryset = queryset.filter(category=category)
        
        if status:
            queryset = queryset.filter(is_published=(status == 'published'))
        
        if featured:
            queryset = queryset.filter(is_featured=(featured == 'yes'))
        
        # Order by published date, then created date
        queryset = queryset.order_by('-published_at', '-created_at')
        
        # Pagination
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get('page')
        articles = paginator.get_page(page_number)
        
        context = {
            'articles': articles,
            'search': search,
            'category': category,
            'status': status,
            'featured': featured,
            'total_count': paginator.count,
        }
        
        return render(request, 'admin/admin_articles.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading articles: {str(e)}')
        return render(request, 'admin/admin_articles.html', {
            'articles': [],
            'search': '',
            'category': '',
            'status': '',
            'featured': '',
            'total_count': 0,
        })

@login_required
@user_passes_test(is_content_manager)
def services(request):
    """Manage services"""
    try:
        # Get filter parameters
        search = request.GET.get('search', '')
        pricing_tier = request.GET.get('pricing_tier', '')
        featured = request.GET.get('featured', '')
        
        # Build queryset
        queryset = Service.objects.all()
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        if pricing_tier:
            queryset = queryset.filter(pricing_tier=pricing_tier)
        
        if featured:
            queryset = queryset.filter(is_featured=(featured == 'yes'))
        
        # Order by order field, then by title
        queryset = queryset.order_by('order', 'title')
        
        # Pagination
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get('page')
        services = paginator.get_page(page_number)
        
        context = {
            'services': services,
            'search': search,
            'pricing_tier': pricing_tier,
            'featured': featured,
            'total_count': paginator.count,
        }
        
        return render(request, 'admin/admin_services.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading services: {str(e)}')
        return render(request, 'admin/admin_services.html', {
            'services': [],
            'search': '',
            'pricing_tier': '',
            'featured': '',
            'total_count': 0,
        })

@login_required
@user_passes_test(is_content_manager)
def past_solutions(request):
    """Manage past solutions/case studies"""
    try:
        # Get filter parameters
        search = request.GET.get('search', '')
        industry = request.GET.get('industry', '')
        featured = request.GET.get('featured', '')
        
        # Build queryset
        queryset = PastSolution.objects.all()
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(client_name__icontains=search) |
                Q(description__icontains=search)
            )
        
        if industry:
            queryset = queryset.filter(industry__icontains=industry)
        
        if featured:
            queryset = queryset.filter(is_featured=(featured == 'yes'))
        
        # Order by completion date
        queryset = queryset.order_by('-completion_date')
        
        # Pagination
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get('page')
        solutions = paginator.get_page(page_number)
        
        context = {
            'solutions': solutions,
            'search': search,
            'industry': industry,
            'featured': featured,
            'total_count': paginator.count,
        }
        
        return render(request, 'admin/admin_past_solutions.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading past solutions: {str(e)}')
        return render(request, 'admin/admin_past_solutions.html', {
            'solutions': [],
            'search': '',
            'industry': '',
            'featured': '',
            'total_count': 0,
        })

@login_required
@user_passes_test(is_super_admin)
def site_settings(request):
    """Manage site settings"""
    try:
        settings_obj = SiteSettings.get_settings()
        
        if request.method == 'POST':
            # Update settings
            settings_obj.site_name = request.POST.get('site_name', settings_obj.site_name)
            settings_obj.site_description = request.POST.get('site_description', settings_obj.site_description)
            settings_obj.contact_email = request.POST.get('contact_email', settings_obj.contact_email)
            settings_obj.contact_phone = request.POST.get('contact_phone', settings_obj.contact_phone)
            settings_obj.address = request.POST.get('address', settings_obj.address)
            settings_obj.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
            settings_obj.save()
            
            messages.success(request, 'Site settings updated successfully')
            return redirect('admin:site_settings')
        
        context = {
            'settings': settings_obj,
        }
        
        return render(request, 'admin/admin_site_settings.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading site settings: {str(e)}')
        return render(request, 'admin/admin_site_settings.html', {
            'settings': None,
        })

@login_required
@user_passes_test(is_super_admin)
def users(request):
    """Manage users and access"""
    try:
        # Get filter parameters
        search = request.GET.get('search', '')
        role = request.GET.get('role', '')
        status = request.GET.get('status', '')
        
        # Build queryset
        queryset = UserProfile.objects.select_related('user', 'role')
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        
        if role:
            queryset = queryset.filter(role__name=role)
        
        if status:
            queryset = queryset.filter(is_active=(status == 'active'))
        
        # Order by created date
        queryset = queryset.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get('page')
        users = paginator.get_page(page_number)
        
        # Get unique roles for filter dropdown
        roles = UserProfile.objects.values_list('role__name', flat=True).distinct().exclude(role__name__isnull=True)
        
        context = {
            'users': users,
            'roles': roles,
            'search': search,
            'role': role,
            'status': status,
            'total_count': paginator.count,
        }
        
        return render(request, 'admin/admin_users.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading users: {str(e)}')
        return render(request, 'admin/admin_users.html', {
            'users': [],
            'roles': [],
            'search': '',
            'role': '',
            'status': '',
            'total_count': 0,
        })

@login_required
@user_passes_test(is_super_admin)
def get_user_json(request, profile_id):
    """Return current user profile data as JSON for edit modal."""
    profile = get_object_or_404(UserProfile.objects.select_related('user', 'role'), id=profile_id)
    data = {
        'id': profile.id,
        'username': profile.user.username,
        'email': profile.user.email,
        'first_name': profile.user.first_name,
        'last_name': profile.user.last_name,
        'role': profile.role.name if profile.role else None,
        'department': profile.department or '',
        'is_active': profile.is_active,
        'last_login': profile.user.last_login.strftime('%Y-%m-%d %H:%M') if profile.user.last_login else None,
        'created_at': profile.created_at.strftime('%Y-%m-%d %H:%M'),
    }
    return JsonResponse({'ok': True, 'user': data})

@login_required
@user_passes_test(is_super_admin)
def create_user(request):
    """Create a new user and associated profile with role assignment."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    try:
        email = request.POST.get('email', '').strip().lower()
        role_name = request.POST.get('role', '').strip()
        department = request.POST.get('department', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        # If username is blank or missing, derive from email prefix
        username = request.POST.get('username', '').strip()
        if not username and email:
            username = email.split('@')[0]
        temp_password = request.POST.get('password', '')

        # Require email and role; username will be auto-generated when absent
        if not email or not role_name:
            return JsonResponse({'ok': False, 'error': 'Missing required fields'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'ok': False, 'error': 'Username already exists'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'ok': False, 'error': 'Email already exists'}, status=400)

        user = User.objects.create_user(username=username, email=email)
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if temp_password and len(temp_password) >= 8:
            user.set_password(temp_password)
        else:
            # set unusable password to force reset flow if implemented later
            user.set_unusable_password()
        user.is_active = True
        user.save()

        role = None
        if role_name:
            role = UserRole.objects.filter(name=role_name).first()

        profile = UserProfile.objects.create(
            user=user,
            role=role,
            department=department or None,
            is_active=True,
        )

        # Send invitation email
        try:
            login_url = request.build_absolute_uri('/admin/login/')
            if temp_password and len(temp_password) >= 8:
                # Send credentials email
                subject = 'Your AI Solution Hub Admin Access'
                message = (
                    f"Hello {first_name or username},\n\n"
                    f"An account has been created for you on the AI Solution Hub Admin Panel.\n\n"
                    f"Username: {username}\n"
                    f"Temporary Password: {temp_password}\n\n"
                    f"Login here: {login_url}\n\n"
                    f"For security, please change your password after logging in.\n\n"
                    f"If you did not expect this, please contact an administrator."
                )
                send_mail(subject, message, None, [email], fail_silently=False)
            else:
                # Trigger password reset email to let the user set their password securely
                reset_form = PasswordResetForm(data={'email': email})
                if reset_form.is_valid():
                    reset_form.save(request=request, use_https=request.is_secure())
        except Exception:
            # Do not fail user creation if email sending fails; the admin UI will still show success
            pass

        return JsonResponse({'ok': True, 'profile_id': profile.id})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(is_super_admin)
def edit_user(request, profile_id):
    """Edit existing user profile and role."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    try:
        profile = get_object_or_404(UserProfile, id=profile_id)
        user = profile.user

        # Basic fields
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        department = request.POST.get('department')
        role_name = request.POST.get('role')
        is_active = request.POST.get('is_active')
        new_password = request.POST.get('password')

        if first_name is not None:
            user.first_name = first_name.strip()
        if last_name is not None:
            user.last_name = last_name.strip()
        if email is not None:
            email = email.strip().lower()
            if User.objects.exclude(id=user.id).filter(email=email).exists():
                return JsonResponse({'ok': False, 'error': 'Email already in use'}, status=400)
            user.email = email
        if new_password:
            if len(new_password) < 8:
                return JsonResponse({'ok': False, 'error': 'Password too short'}, status=400)
            user.set_password(new_password)
        user.save()

        if department is not None:
            profile.department = department.strip() or None
        if role_name is not None:
            profile.role = UserRole.objects.filter(name=role_name).first()
        if is_active is not None:
            profile.is_active = (str(is_active).lower() in ['1', 'true', 'yes', 'on'])
            user.is_active = profile.is_active
            user.save()
        profile.save()

        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(is_super_admin)
def toggle_user_status(request, profile_id):
    """Toggle active status of a user/profile."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    try:
        profile = get_object_or_404(UserProfile, id=profile_id)
        profile.is_active = not profile.is_active
        profile.save()
        profile.user.is_active = profile.is_active
        profile.user.save()
        return JsonResponse({'ok': True, 'is_active': profile.is_active})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(is_super_admin)
def export_users_csv(request):
    """Export users to CSV with audit logging."""
    # Reuse filters from users()
    search = request.GET.get('search', '')
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')

    queryset = UserProfile.objects.select_related('user', 'role')
    if search:
        queryset = queryset.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    if role:
        queryset = queryset.filter(role__name=role)
    if status:
        queryset = queryset.filter(is_active=(status == 'active'))

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    writer = csv.writer(response)

    filter_summary = json.dumps({'search': search, 'role': role, 'status': status})
    writer.writerow([f'Filters: {filter_summary}'])
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Role', 'Department', 'Active', 'Last Login', 'Created'])
    for p in queryset.order_by('-created_at'):
        writer.writerow([
            p.user.username,
            p.user.email,
            p.user.first_name,
            p.user.last_name,
            p.role.name if p.role else '',
            p.department or '',
            'Yes' if p.is_active else 'No',
            p.user.last_login.strftime('%Y-%m-%d %H:%M') if p.user.last_login else '',
            p.created_at.strftime('%Y-%m-%d %H:%M'),
        ])

    try:
        ExportLog.objects.create(
            user=request.user,
            model='UserProfile',
            filter_summary=filter_summary
        )
    except Exception:
        pass

    return response

@login_required
@user_passes_test(is_analyst)
def audit_exports(request):
    """View audit logs and export history"""
    try:
        # Get filter parameters
        model = request.GET.get('model', '')
        user = request.GET.get('user', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Build queryset
        queryset = ExportLog.objects.select_related('user')
        
        # Apply filters
        if model:
            queryset = queryset.filter(model__icontains=model)
        
        if user:
            queryset = queryset.filter(user__username__icontains=user)
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Order by created date
        queryset = queryset.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get('page')
        audit_logs = paginator.get_page(page_number)
        
        # Get unique models for filter dropdown
        models = ExportLog.objects.values_list('model', flat=True).distinct().order_by('model')
        
        context = {
            'audit_logs': audit_logs,
            'models': models,
            'model': model,
            'user_filter': user,
            'date_from': date_from,
            'date_to': date_to,
            'total_count': paginator.count,
        }
        
        return render(request, 'admin/admin_audit_exports.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading audit logs: {str(e)}')
        return render(request, 'admin/admin_audit_exports.html', {
            'audit_logs': [],
            'models': [],
            'model': '',
            'user_filter': '',
            'date_from': '',
            'date_to': '',
            'total_count': 0,
        })

@login_required
@user_passes_test(is_analyst)
def reports(request):
    """Generate reports and analytics"""
    try:
        # Get date range
        date_from = request.GET.get('date_from', (timezone.now().date() - timedelta(days=30)).strftime('%Y-%m-%d'))
        date_to = request.GET.get('date_to', timezone.now().date().strftime('%Y-%m-%d'))
        
        # Convert to date objects
        from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        # Get data for the date range
        inquiries = Contact.objects.filter(created_at__date__range=[from_date, to_date])
        subscribers = NewsletterSubscriber.objects.filter(subscribed_at__date__range=[from_date, to_date])
        
        # Calculate metrics
        total_inquiries = inquiries.count()
        new_inquiries = inquiries.filter(status='new').count()
        contacted_inquiries = inquiries.filter(status='contacted').count()
        total_subscribers = subscribers.filter(is_active=True).count()
        
        # Top countries
        top_countries = inquiries.values('country').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Weekly data for charts
        weekly_data = []
        current_date = from_date
        while current_date <= to_date:
            week_inquiries = inquiries.filter(created_at__date=current_date).count()
            week_subscribers = subscribers.filter(subscribed_at__date=current_date).count()
            weekly_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'inquiries': week_inquiries,
                'subscribers': week_subscribers,
            })
            current_date += timedelta(days=1)
        
        context = {
            'date_from': date_from,
            'date_to': date_to,
            'total_inquiries': total_inquiries,
            'new_inquiries': new_inquiries,
            'contacted_inquiries': contacted_inquiries,
            'total_subscribers': total_subscribers,
            'top_countries': top_countries,
            'weekly_data': weekly_data,
        }
        
        return render(request, 'admin/admin_reports.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading reports: {str(e)}')
        return render(request, 'admin/admin_reports.html', {
            'date_from': (timezone.now().date() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'date_to': timezone.now().date().strftime('%Y-%m-%d'),
            'total_inquiries': 0,
            'new_inquiries': 0,
            'contacted_inquiries': 0,
            'total_subscribers': 0,
            'top_countries': [],
            'weekly_data': [],
        })

@login_required
@user_passes_test(is_analyst)
def export_reports_csv(request):
    """Export Reports data (inquiries, subscribers, top countries, daily series) as CSV for a date range"""
    # Parse date range with defaults matching the reports view
    date_from = request.GET.get('date_from', (timezone.now().date() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', timezone.now().date().strftime('%Y-%m-%d'))

    from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
    to_date = datetime.strptime(date_to, '%Y-%m-%d').date()

    inquiries = Contact.objects.filter(created_at__date__range=[from_date, to_date])
    subscribers = NewsletterSubscriber.objects.filter(subscribed_at__date__range=[from_date, to_date])

    total_inquiries = inquiries.count()
    new_inquiries = inquiries.filter(status='new').count()
    contacted_inquiries = inquiries.filter(status='contacted').count()
    total_subscribers = subscribers.filter(is_active=True).count()

    top_countries = list(
        inquiries.values('country').annotate(count=Count('id')).order_by('-count')[:10]
    )

    # Build daily time series
    daily_rows = []
    current_date = from_date
    while current_date <= to_date:
        day_inq = inquiries.filter(created_at__date=current_date).count()
        day_sub = subscribers.filter(subscribed_at__date=current_date).count()
        daily_rows.append((current_date.strftime('%Y-%m-%d'), day_inq, day_sub))
        current_date += timedelta(days=1)

    # Prepare CSV response
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="reports_{date_from}_to_{date_to}.csv"'
    response.write('\ufeff')  # BOM for Excel
    writer = csv.writer(response)

    # Summary section
    writer.writerow([f"AI Solution Hub Reports ({date_from} to {date_to})"])
    writer.writerow([])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total Inquiries", total_inquiries])
    writer.writerow(["New Inquiries", new_inquiries])
    writer.writerow(["Contacted Inquiries", contacted_inquiries])
    writer.writerow(["Active Subscribers", total_subscribers])
    writer.writerow([])

    # Top countries
    writer.writerow(["Top Countries"])
    writer.writerow(["Country", "Count"])
    for c in top_countries:
        writer.writerow([c.get('country') or 'Unknown', c.get('count', 0)])
    writer.writerow([])

    # Daily series
    writer.writerow(["Daily Breakdown"])
    writer.writerow(["Date", "Inquiries", "Subscribers"])
    for day, inq, sub in daily_rows:
        writer.writerow([day, inq, sub])

    return response

@login_required
@user_passes_test(is_admin_user)
def profile(request):
    """User profile management"""
    try:
        user_profile = request.user.profile
        
        if request.method == 'POST':
            # Update profile
            if 'update_profile' in request.POST:
                user_profile.user.first_name = request.POST.get('first_name', '')
                user_profile.user.last_name = request.POST.get('last_name', '')
                user_profile.user.email = request.POST.get('email', '')
                user_profile.phone = request.POST.get('phone', '')
                user_profile.bio = request.POST.get('bio', '')
                user_profile.user.save()
                user_profile.save()
                
                messages.success(request, 'Profile updated successfully')
                return redirect('admin:profile')
            
            # Change password
            if 'change_password' in request.POST:
                old_password = request.POST.get('old_password')
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                
                if not request.user.check_password(old_password):
                    messages.error(request, 'Current password is incorrect')
                elif new_password != confirm_password:
                    messages.error(request, 'New passwords do not match')
                elif len(new_password) < 8:
                    messages.error(request, 'Password must be at least 8 characters long')
                else:
                    request.user.set_password(new_password)
                    request.user.save()
                    messages.success(request, 'Password changed successfully')
                    return redirect('admin:profile')
        
        context = {
            'user_profile': user_profile,
        }
        
        return render(request, 'admin/admin_profile.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading profile: {str(e)}')
        return render(request, 'admin/admin_profile.html', {
            'user_profile': None,
        })

# Export functions
@login_required
@user_passes_test(is_admin_user)
def export_inquiries_csv(request):
    """Export inquiries to CSV"""
    try:
        # Get filter parameters from request
        search = request.GET.get('search', '')
        status = request.GET.get('status', '')
        country = request.GET.get('country', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Build queryset
        queryset = Contact.objects.all()
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(company__icontains=search) |
                Q(job_details__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="inquiries_export.csv"'
        response.write('\ufeff')  # BOM for Excel
        
        writer = csv.writer(response)
        
        # Write filter summary
        filter_summary = f"Search: {search}, Status: {status}, Country: {country}, From: {date_from}, To: {date_to}"
        writer.writerow([f"Export: {filter_summary}"])
        writer.writerow([])  # Empty row
        
        # Write headers
        writer.writerow([
            'Name', 'Email', 'Phone', 'Company', 'Country', 'Job Title', 
            'Job Details', 'Status', 'Notes', 'Created At'
        ])
        
        # Write data
        for contact in queryset:
            writer.writerow([
                contact.name,
                contact.email,
                contact.phone,
                contact.company,
                contact.country,
                contact.job_title,
                contact.job_details,
                contact.status,
                contact.notes or '',
                contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Log export
        ExportLog.objects.create(
            user=request.user,
            model='Contact',
            filter_summary=filter_summary
        )
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting inquiries: {str(e)}')
        return redirect('admin:inquiries_list')

@login_required
@user_passes_test(is_admin_user)
def export_subscribers_csv(request):
    """Export subscribers to CSV"""
    try:
        # Get filter parameters
        search = request.GET.get('search', '')
        status = request.GET.get('status', '')
        source = request.GET.get('source', '')
        
        # Build queryset
        queryset = NewsletterSubscriber.objects.all()
        
        # Apply filters
        if search:
            queryset = queryset.filter(email__icontains=search)
        
        if status:
            queryset = queryset.filter(is_active=(status == 'active'))
        
        if source:
            queryset = queryset.filter(source=source)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="subscribers_export.csv"'
        response.write('\ufeff')  # BOM for Excel
        
        writer = csv.writer(response)
        
        # Write filter summary
        filter_summary = f"Search: {search}, Status: {status}, Source: {source}"
        writer.writerow([f"Export: {filter_summary}"])
        writer.writerow([])  # Empty row
        
        # Write headers
        writer.writerow([
            'Email', 'Status', 'Source', 'Subscribed At', 'Unsubscribed At', 'IP Address'
        ])
        
        # Write data
        for subscriber in queryset:
            writer.writerow([
                subscriber.email,
                'Active' if subscriber.is_active else 'Inactive',
                subscriber.source,
                subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M:%S'),
                subscriber.unsubscribed_at.strftime('%Y-%m-%d %H:%M:%S') if subscriber.unsubscribed_at else '',
                subscriber.ip_address or ''
            ])
        
        # Log export
        ExportLog.objects.create(
            user=request.user,
            model='NewsletterSubscriber',
            filter_summary=filter_summary
        )
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting subscribers: {str(e)}')
        return redirect('admin:subscribers')

@login_required
@user_passes_test(is_admin_user)
def forms_list(request):
    """List all form submissions (Contact model), filterable by form_type, status, search, and date."""
    try:
        search = request.GET.get('search', '')
        form_type = request.GET.get('form_type', '')
        status = request.GET.get('status', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')

        queryset = Contact.objects.all()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(company__icontains=search) |
                Q(job_details__icontains=search) |
                Q(message__icontains=search) |
                Q(interest__icontains=search)
            )
        if form_type:
            queryset = queryset.filter(form_type=form_type)
        if status:
            queryset = queryset.filter(status=status)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        queryset = queryset.order_by('-created_at')
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get('page')
        forms = paginator.get_page(page_number)
        form_types = Contact.objects.values_list('form_type', flat=True).distinct()
        statuses = Contact.objects.values_list('status', flat=True).distinct()
        context = {
            'forms': forms,
            'form_types': form_types,
            'statuses': statuses,
            'search': search,
            'form_type': form_type,
            'status': status,
            'date_from': date_from,
            'date_to': date_to,
            'total_count': paginator.count,
        }
        return render(request, 'admin/admin_forms.html', context)
    except Exception as e:
        messages.error(request, f'Error loading forms: {str(e)}')
        return render(request, 'admin/admin_forms.html', {
            'forms': [],
            'form_types': [],
            'statuses': [],
            'search': '',
            'form_type': '',
            'status': '',
            'date_from': '',
            'date_to': '',
            'total_count': 0,
        })

@login_required
@user_passes_test(is_admin_user)
def form_detail(request, form_id):
    """Detail view for a specific form submission"""
    try:
        form_submission = get_object_or_404(Contact, id=form_id)
        
        if request.method == 'POST':
            # Handle status update
            new_status = request.POST.get('status')
            if new_status in ['new', 'in_progress', 'contacted', 'closed']:
                form_submission.status = new_status
                form_submission.save()
                messages.success(request, f'Form status updated to {new_status}')
                return redirect('admin:form_detail', form_id=form_id)
            
            # Handle notes update
            notes = request.POST.get('notes')
            if notes is not None:
                form_submission.notes = notes
                form_submission.save()
                messages.success(request, 'Notes updated successfully')
                return redirect('admin:form_detail', form_id=form_id)
        
        context = {
            'form_submission': form_submission,
        }
        
        return render(request, 'admin/admin_form_detail.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading form: {str(e)}')
        return redirect('admin:forms')

@login_required
@user_passes_test(is_admin_user)
def form_delete(request, form_id):
    """Delete a form submission"""
    if request.method == 'POST':
        try:
            form_submission = get_object_or_404(Contact, id=form_id)
            form_name = form_submission.name
            form_submission.delete()
            messages.success(request, f'Form submission from {form_name} deleted successfully')
            return redirect('admin:forms')
        except Exception as e:
            messages.error(request, f'Error deleting form: {str(e)}')
            return redirect('admin:forms')
    else:
        return redirect('admin:forms')
