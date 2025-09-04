from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import json
import csv
from datetime import datetime, timedelta
from .models import (
    Contact, Service, PastSolution, Event, Gallery, 
    Testimonial, Article, AdminDashboard, SiteSettings, UserProfile, UserRole
)
from .forms import ContactForm

def home(request):
    """Home page view with featured content"""
    context = {
        'services': Service.objects.filter(is_featured=True)[:6],
        'solutions': PastSolution.objects.filter(is_featured=True)[:3],
        'testimonials': Testimonial.objects.filter(is_featured=True)[:3],
        'events': Event.objects.filter(is_featured=True, start_date__gte=timezone.now())[:3],
        'articles': Article.objects.filter(is_featured=True, is_published=True)[:2],
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/home.html', context)

def services(request):
    """Services page view"""
    services_list = Service.objects.all().order_by('order', 'title')
    context = {
        'services': services_list,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/services.html', context)

def service_detail(request, service_id):
    """Individual service detail view"""
    service = get_object_or_404(Service, id=service_id)
    related_services = Service.objects.filter(
        pricing_tier=service.pricing_tier
    ).exclude(id=service.id)[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/service_detail.html', context)

def past_solutions(request):
    """Past solutions/case studies page view"""
    solutions_list = PastSolution.objects.all().order_by('-completion_date')
    
    # Filtering
    industry = request.GET.get('industry')
    if industry:
        solutions_list = solutions_list.filter(industry__icontains=industry)
    
    # Pagination
    paginator = Paginator(solutions_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique industries for filter
    industries = PastSolution.objects.values_list('industry', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'industries': industries,
        'selected_industry': industry,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/past_solutions.html', context)

def solution_detail(request, solution_id):
    """Individual solution detail view"""
    solution = get_object_or_404(PastSolution, id=solution_id)
    related_solutions = PastSolution.objects.filter(
        industry=solution.industry
    ).exclude(id=solution.id)[:3]
    
    context = {
        'solution': solution,
        'related_solutions': related_solutions,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/solution_detail.html', context)

def events_gallery(request):
    """Events and gallery page view"""
    upcoming_events = Event.objects.filter(
        start_date__gte=timezone.now()
    ).order_by('start_date')[:6]
    
    past_events = Event.objects.filter(
        start_date__lt=timezone.now()
    ).order_by('-start_date')[:6]
    
    gallery_images = Gallery.objects.filter(is_featured=True).order_by('order', '-created_at')[:12]
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'gallery_images': gallery_images,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/events_gallery.html', context)

def event_detail(request, event_id):
    """Individual event detail view"""
    event = get_object_or_404(Event, id=event_id)
    related_events = Event.objects.filter(
        event_type=event.event_type
    ).exclude(id=event.id)[:3]
    
    gallery_images = Gallery.objects.filter(event=event).order_by('order')
    
    context = {
        'event': event,
        'related_events': related_events,
        'gallery_images': gallery_images,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/event_detail.html', context)

def customer_feedback(request):
    """Customer feedback/testimonials page view"""
    if request.method == 'POST':
        # Handle testimonial form submission
        customer_name = request.POST.get('customer_name', '')
        company = request.POST.get('company', '')
        job_title = request.POST.get('job_title', '')
        rating = request.POST.get('rating', '')
        review = request.POST.get('review', '')
        project_name = request.POST.get('project_name', '')
        industry = request.POST.get('industry', '')
        
        if customer_name and rating and review:
            try:
                testimonial = Testimonial.objects.create(
                    customer_name=customer_name,
                    company=company,
                    job_title=job_title,
                    rating=int(rating),
                    review=review,
                    is_verified=False  # New testimonials need admin approval
                )
                messages.success(request, 'Thank you for your feedback! Your testimonial has been submitted and will be reviewed by our team.')
            except Exception as e:
                messages.error(request, 'There was an error submitting your testimonial. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        
        return redirect('ai_solution_app:customer_feedback')
    
    # Get all verified testimonials for display
    testimonials = Testimonial.objects.filter(is_verified=True).order_by('-created_at')
    featured_testimonials = testimonials.filter(is_featured=True)
    
    # Filtering by rating
    rating_filter = request.GET.get('rating')
    if rating_filter:
        testimonials = testimonials.filter(rating=int(rating_filter))
    
    # Pagination
    paginator = Paginator(testimonials, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'testimonials': testimonials,
        'featured_testimonials': featured_testimonials,
        'page_obj': page_obj,
        'rating_filter': rating_filter,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/customer_feedback.html', context)

def articles_blog(request):
    """Articles/blog page view"""
    articles = Article.objects.filter(is_published=True).order_by('-published_at')
    
    # Category filter
    category = request.GET.get('category')
    if category:
        articles = articles.filter(category=category)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Article.objects.filter(is_published=True).values_list('category', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category,
        'search_query': search_query,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/articles_blog.html', context)

def article_detail(request, article_slug):
    """Individual article detail view"""
    article = get_object_or_404(Article, slug=article_slug, is_published=True)
    
    # Increment view count
    article.views_count += 1
    article.save(update_fields=['views_count'])
    
    # Related articles
    related_articles = Article.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(id=article.id)[:3]
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/article_detail.html', context)

def about_us(request):
    """About us page view"""
    context = {
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/about_us.html', context)

def contact_us(request):
    """Contact us page view with form handling"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            
            # Send confirmation email to customer
            try:
                customer_subject = f'Thank you for contacting AI Solution Hub, {contact.name}!'
                customer_message = f"""
Dear {contact.name},

Thank you for reaching out to AI Solution Hub! We have received your inquiry and our team will review it carefully.

Inquiry Details:
- Company: {contact.company}
- Job Title: {contact.job_title}
- Country: {contact.country}
- Inquiry: {contact.job_details[:100]}{'...' if len(contact.job_details) > 100 else ''}

We will get back to you within 24 hours with a detailed response and next steps.

Best regards,
AI Solution Hub Team
                """
                
                send_mail(
                    customer_subject,
                    customer_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [contact.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't fail the form submission
                print(f"Failed to send customer email: {e}")
            
            # Send notification email to admin
            try:
                admin_subject = f'New Contact Inquiry from {contact.name} - {contact.company}'
                admin_message = f"""
New contact inquiry received:

Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone}
Company: {contact.company}
Country: {contact.country}
Job Title: {contact.job_title}
Job Details: {contact.job_details}
Status: {contact.status}
Created: {contact.created_at}

Please review and respond within 24 hours.
                """
                
                # Send to admin email (you can configure this in settings)
                admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@aisolutionhub.com')
                send_mail(
                    admin_subject,
                    admin_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin_email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't fail the form submission
                print(f"Failed to send admin email: {e}")
            
            messages.success(
                request, 
                f'Thank you {contact.name}! Your inquiry has been submitted successfully. We have sent a confirmation email to {contact.email}. We will get back to you within 24 hours.'
            )
            return redirect('contact_us')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/contact_us.html', context)

@login_required
def admin_dashboard(request):
    """Admin dashboard view with analytics and contact management"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff privileges required.')
        return redirect('home')
    
    # Get contact statistics
    total_contacts = Contact.objects.count()
    new_contacts = Contact.objects.filter(status='new').count()
    in_progress_contacts = Contact.objects.filter(status='in_progress').count()
    contacted_contacts = Contact.objects.filter(status='contacted').count()
    
    # Weekly contact trend
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    weekly_contacts = Contact.objects.filter(
        created_at__date__gte=week_ago
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Recent contacts
    recent_contacts = Contact.objects.all().order_by('-created_at')[:10]
    
    # Get or create dashboard configuration
    dashboard_config, created = AdminDashboard.objects.get_or_create(
        pk=AdminDashboard.objects.first().pk if AdminDashboard.objects.exists() else None
    )
    
    context = {
        'total_contacts': total_contacts,
        'new_contacts': new_contacts,
        'in_progress_contacts': in_progress_contacts,
        'contacted_contacts': contacted_contacts,
        'weekly_contacts': list(weekly_contacts),
        'recent_contacts': recent_contacts,
        'dashboard_config': dashboard_config,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'admin/index.html', context)

@login_required
@require_http_methods(["POST"])
def update_contact_status(request, contact_id):
    """Update contact status via AJAX"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        contact = get_object_or_404(Contact, id=contact_id)
        new_status = request.POST.get('status')
        
        if new_status in ['new', 'in_progress', 'contacted', 'closed']:
            contact.status = new_status
            contact.save()
            return JsonResponse({'success': True, 'new_status': new_status})
        else:
            return JsonResponse({'error': 'Invalid status'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def export_contacts_csv(request):
    """Export contacts to CSV with filtering"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('admin_dashboard')
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    country_filter = request.GET.get('country', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Build queryset with filters
    contacts = Contact.objects.all()
    
    if status_filter:
        contacts = contacts.filter(status=status_filter)
    if country_filter:
        contacts = contacts.filter(country__icontains=country_filter)
    if date_from:
        contacts = contacts.filter(created_at__date__gte=date_from)
    if date_to:
        contacts = contacts.filter(created_at__date__lte=date_to)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="contacts_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # Write CSV with UTF-8 BOM for Excel compatibility
    response.write('\ufeff')
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Name', 'Email', 'Phone', 'Company', 'Country', 
        'Job Title', 'Job Details', 'Status', 'Created At', 'Notes'
    ])
    
    # Write data
    for contact in contacts:
        writer.writerow([
            contact.name, contact.email, contact.phone, contact.company,
            contact.country, contact.job_title, contact.job_details,
            contact.status, contact.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            contact.notes or ''
        ])
    
    return response

@login_required
def get_dashboard_stats(request):
    """Get dashboard statistics for AJAX updates"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get real-time statistics
    total_contacts = Contact.objects.count()
    new_contacts = Contact.objects.filter(status='new').count()
    
    # Weekly trend data
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    weekly_data = []
    
    for i in range(7):
        date = week_ago + timedelta(days=i)
        count = Contact.objects.filter(created_at__date=date).count()
        weekly_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return JsonResponse({
        'total_contacts': total_contacts,
        'new_contacts': new_contacts,
        'weekly_data': weekly_data
    })

def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'ai_solution_app/404.html', status=404)

def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'ai_solution_app/500.html', status=500)

@login_required
def contact_analysis(request):
    """Contact analysis dashboard with detailed analytics"""
    # Get date range from request
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get contact statistics
    total_contacts = Contact.objects.count()
    recent_contacts = Contact.objects.filter(created_at__gte=start_date)
    
    # Status breakdown
    status_stats = Contact.objects.values('status').annotate(count=Count('id'))
    
    # Country breakdown
    country_stats = Contact.objects.values('country').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Daily contact trends
    daily_trends = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        count = Contact.objects.filter(created_at__date=date.date()).count()
        daily_trends.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Company analysis
    company_stats = Contact.objects.values('company').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Response time analysis (mock data for demo)
    response_times = {
        'avg_first_response': '2.5 hours',
        'avg_resolution': '24 hours',
        'sla_breaches': 3
    }
    
    context = {
        'total_contacts': total_contacts,
        'recent_contacts_count': recent_contacts.count(),
        'status_stats': status_stats,
        'country_stats': country_stats,
        'daily_trends': daily_trends,
        'company_stats': company_stats,
        'response_times': response_times,
        'days': days,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'admin/contact_analysis.html', context)

@login_required
def user_management(request):
    """User management dashboard for creating and managing admin users"""
    from django.contrib.auth.models import User
    from .models import UserRole, UserProfile
    
    if request.method == 'POST':
        # Handle user creation
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role_id = request.POST.get('role')
        department = request.POST.get('department')
        phone = request.POST.get('phone')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            
            # Create profile
            role = UserRole.objects.get(id=role_id) if role_id else None
            UserProfile.objects.create(
                user=user,
                role=role,
                department=department,
                phone=phone,
                is_active=True
            )
            
            messages.success(request, f'User "{username}" created successfully!')
            return redirect('/admin-dashboard/user-management/')
            
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    
    # Get all users with their profiles
    users = User.objects.select_related('profile').all()
    roles = UserRole.objects.all()
    
    # Get user statistics
    total_users = users.count()
    active_users = users.filter(profile__is_active=True).count()
    role_stats = UserProfile.objects.values('role__name').annotate(count=Count('id'))
    
    context = {
        'users': users,
        'roles': roles,
        'total_users': total_users,
        'active_users': active_users,
        'role_stats': role_stats
    }
    
    return render(request, 'admin/user_management.html', context)

@login_required
def gallery_management(request):
    """Gallery management with image upload functionality"""
    from .models import Gallery
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    import os
    
    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        
        if action == 'upload' and 'image' in request.FILES:
            # Handle image upload
            image = request.FILES['image']
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            category = request.POST.get('category', 'general')
            is_featured = 'is_featured' in request.POST
            
            # Save the image
            gallery_item = Gallery.objects.create(
                title=title,
                description=description,
                category=category,
                is_featured=is_featured,
                image=image
            )
            messages.success(request, f'Image "{title}" uploaded successfully!')
            return redirect('/admin-dashboard/gallery-management/')
            
        elif action == 'feature' and item_id:
            # Feature/unfeature image
            try:
                gallery_item = Gallery.objects.get(id=item_id)
                gallery_item.is_featured = True
                gallery_item.save()
                messages.success(request, f'Image "{gallery_item.title}" featured!')
            except Gallery.DoesNotExist:
                messages.error(request, 'Image not found!')
            return redirect('/admin-dashboard/gallery-management/')
            
        elif action == 'unfeature' and item_id:
            # Unfeature image
            try:
                gallery_item = Gallery.objects.get(id=item_id)
                gallery_item.is_featured = False
                gallery_item.save()
                messages.success(request, f'Image "{gallery_item.title}" unfeatured!')
            except Gallery.DoesNotExist:
                messages.error(request, 'Image not found!')
            return redirect('/admin-dashboard/gallery-management/')
            
        elif action == 'delete' and item_id:
            # Delete image
            try:
                gallery_item = Gallery.objects.get(id=item_id)
                title = gallery_item.title
                # Delete the file from storage
                if gallery_item.image:
                    gallery_item.image.delete()
                gallery_item.delete()
                messages.success(request, f'Image "{title}" deleted!')
            except Gallery.DoesNotExist:
                messages.error(request, 'Image not found!')
            return redirect('/admin-dashboard/gallery-management/')
    
    # Get gallery items
    gallery_items = Gallery.objects.all().order_by('-created_at')
    categories = Gallery.objects.values_list('category', flat=True).distinct()
    
    context = {
        'gallery_items': gallery_items,
        'categories': categories,
        'total_images': gallery_items.count(),
        'featured_images': gallery_items.filter(is_featured=True).count()
    }
    
    return render(request, 'admin/gallery_management.html', context)

@login_required
def testimonials_management(request):
    """Testimonials management with approval system"""
    from .models import Testimonial
    
    if request.method == 'POST':
        testimonial_id = request.POST.get('testimonial_id')
        action = request.POST.get('action')
        
        try:
            testimonial = Testimonial.objects.get(id=testimonial_id)
            
            if action == 'approve':
                testimonial.is_verified = True
                testimonial.save()
                messages.success(request, f'Testimonial from {testimonial.customer_name} approved!')
            elif action == 'reject':
                testimonial.is_verified = False
                testimonial.save()
                messages.warning(request, f'Testimonial from {testimonial.customer_name} rejected!')
            elif action == 'feature':
                testimonial.is_featured = not testimonial.is_featured
                testimonial.save()
                status = 'featured' if testimonial.is_featured else 'unfeatured'
                messages.info(request, f'Testimonial from {testimonial.customer_name} {status}!')
            elif action == 'delete':
                testimonial.delete()
                messages.error(request, f'Testimonial from {testimonial.customer_name} deleted!')
                
        except Testimonial.DoesNotExist:
            messages.error(request, 'Testimonial not found!')
        
        return redirect('/admin-dashboard/testimonials-management/')
    
    # Get testimonials
    all_testimonials = Testimonial.objects.all().order_by('-created_at')
    pending_testimonials = all_testimonials.filter(is_verified=False)
    approved_testimonials = all_testimonials.filter(is_verified=True)
    featured_testimonials = all_testimonials.filter(is_featured=True)
    
    context = {
        'all_testimonials': all_testimonials,
        'pending_testimonials': pending_testimonials,
        'approved_testimonials': approved_testimonials,
        'featured_testimonials': featured_testimonials,
        'total_testimonials': all_testimonials.count(),
        'pending_count': pending_testimonials.count(),
        'approved_count': approved_testimonials.count(),
        'featured_count': featured_testimonials.count()
    }
    
    return render(request, 'admin/testimonials_management.html', context)

@login_required
def services_management(request):
    """Services management with CRUD operations"""
    from .models import Service
    
    if request.method == 'POST':
        action = request.POST.get('action')
        service_id = request.POST.get('service_id')
        
        if action == 'create':
            # Create new service
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            pricing_tier = request.POST.get('pricing_tier', 'basic')
            is_featured = 'is_featured' in request.POST
            
            try:
                service = Service.objects.create(
                    title=title,
                    description=description,
                    pricing_tier=pricing_tier,
                    is_featured=is_featured
                )
                messages.success(request, f'Service "{title}" created successfully!')
            except Exception as e:
                messages.error(request, f'Error creating service: {str(e)}')
            return redirect('/admin-dashboard/services-management/')
            
        elif action == 'update' and service_id:
            # Update service
            try:
                service = Service.objects.get(id=service_id)
                service.title = request.POST.get('title', service.title)
                service.description = request.POST.get('description', service.description)
                service.pricing_tier = request.POST.get('pricing_tier', service.pricing_tier)
                service.is_featured = 'is_featured' in request.POST

                service.save()
                messages.success(request, f'Service "{service.title}" updated successfully!')
            except Service.DoesNotExist:
                messages.error(request, 'Service not found!')
            return redirect('/admin-dashboard/services-management/')
            
        elif action == 'delete' and service_id:
            # Delete service
            try:
                service = Service.objects.get(id=service_id)
                title = service.title
                service.delete()
                messages.success(request, f'Service "{title}" deleted!')
            except Service.DoesNotExist:
                messages.error(request, 'Service not found!')
            return redirect('/admin-dashboard/services-management/')
    
    # Get all services
    services = Service.objects.all().order_by('order', 'title')
    
    context = {
        'services': services,
        'total_services': services.count(),
        'active_services': services.count(),
        'featured_services': services.filter(is_featured=True).count()
    }
    
    return render(request, 'admin/services_management.html', context)

@login_required
def events_management(request):
    """Events management with CRUD operations"""
    from .models import Event
    
    if request.method == 'POST':
        action = request.POST.get('action')
        event_id = request.POST.get('event_id')
        
        if action == 'create':
            # Create new event
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            start_date = request.POST.get('start_date', '')
            end_date = request.POST.get('end_date', '')
            location = request.POST.get('location', '')
            is_featured = 'is_featured' in request.POST
            is_upcoming = 'is_upcoming' in request.POST
            
            try:
                event = Event.objects.create(
                    title=title,
                    description=description,
                    start_date=start_date,
                    end_date=end_date,
                    location=location,
                    is_featured=is_featured,
                    is_upcoming=is_upcoming
                )
                messages.success(request, f'Event "{title}" created successfully!')
            except Exception as e:
                messages.error(request, f'Error creating event: {str(e)}')
            return redirect('/admin-dashboard/events-management/')
            
        elif action == 'update' and event_id:
            # Update event
            try:
                event = Event.objects.get(id=event_id)
                event.title = request.POST.get('title', event.title)
                event.description = request.POST.get('description', event.description)
                event.start_date = request.POST.get('start_date', event.start_date)
                event.end_date = request.POST.get('end_date', event.end_date)
                event.location = request.POST.get('location', event.location)
                event.is_featured = 'is_featured' in request.POST
                event.is_upcoming = 'is_upcoming' in request.POST
                event.save()
                messages.success(request, f'Event "{event.title}" updated successfully!')
            except Event.DoesNotExist:
                messages.error(request, 'Event not found!')
            return redirect('/admin-dashboard/events-management/')
            
        elif action == 'delete' and event_id:
            # Delete event
            try:
                event = Event.objects.get(id=event_id)
                title = event.title
                event.delete()
                messages.success(request, f'Event "{title}" deleted!')
            except Event.DoesNotExist:
                messages.error(request, 'Event not found!')
            return redirect('/admin-dashboard/events-management/')
    
    # Get all events
    events = Event.objects.all().order_by('-start_date')
    upcoming_events = events.filter(start_date__gte=timezone.now())
    past_events = events.filter(start_date__lt=timezone.now())
    
    context = {
        'events': events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'total_events': events.count(),
        'upcoming_count': upcoming_events.count(),
        'featured_events': events.filter(is_featured=True).count()
    }
    
    return render(request, 'admin/events_management.html', context)

@login_required
def articles_management(request):
    """Articles management with CRUD operations"""
    from .models import Article
    
    if request.method == 'POST':
        action = request.POST.get('action')
        article_id = request.POST.get('article_id')
        
        if action == 'create':
            # Create new article
            title = request.POST.get('title', '')
            content = request.POST.get('content', '')
            excerpt = request.POST.get('excerpt', '')
            author = request.POST.get('author', '')
            is_featured = 'is_featured' in request.POST
            is_published = 'is_published' in request.POST
            
            try:
                article = Article.objects.create(
                    title=title,
                    content=content,
                    excerpt=excerpt,
                    author=author,
                    is_featured=is_featured,
                    is_published=is_published
                )
                messages.success(request, f'Article "{title}" created successfully!')
            except Exception as e:
                messages.error(request, f'Error creating article: {str(e)}')
            return redirect('/admin-dashboard/articles-management/')
            
        elif action == 'update' and article_id:
            # Update article
            try:
                article = Article.objects.get(id=article_id)
                article.title = request.POST.get('title', article.title)
                article.content = request.POST.get('content', article.content)
                article.excerpt = request.POST.get('excerpt', article.excerpt)
                article.author = request.POST.get('author', article.author)
                article.is_featured = 'is_featured' in request.POST
                article.is_published = 'is_published' in request.POST
                article.save()
                messages.success(request, f'Article "{article.title}" updated successfully!')
            except Article.DoesNotExist:
                messages.error(request, 'Article not found!')
            return redirect('/admin-dashboard/articles-management/')
            
        elif action == 'delete' and article_id:
            # Delete article
            try:
                article = Article.objects.get(id=article_id)
                title = article.title
                article.delete()
                messages.success(request, f'Article "{title}" deleted!')
            except Article.DoesNotExist:
                messages.error(request, 'Article not found!')
            return redirect('/admin-dashboard/articles-management/')
    
    # Get all articles
    articles = Article.objects.all().order_by('-created_at')
    published_articles = articles.filter(is_published=True)
    
    context = {
        'articles': articles,
        'published_articles': published_articles,
        'total_articles': articles.count(),
        'published_count': published_articles.count(),
        'featured_articles': articles.filter(is_featured=True).count()
    }
    
    return render(request, 'admin/articles_management.html', context)

@login_required
def past_solutions_management(request):
    """Past solutions management with CRUD operations"""
    from .models import PastSolution
    
    if request.method == 'POST':
        action = request.POST.get('action')
        solution_id = request.POST.get('solution_id')
        
        if action == 'create':
            # Create new past solution
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            client_name = request.POST.get('client_name', '')
            industry = request.POST.get('industry', '')
            is_featured = 'is_featured' in request.POST
            is_active = 'is_active' in request.POST
            
            try:
                solution = PastSolution.objects.create(
                    title=title,
                    description=description,
                    client_name=client_name,
                    industry=industry,
                    is_featured=is_featured
                )
                messages.success(request, f'Past solution "{title}" created successfully!')
            except Exception as e:
                messages.error(request, f'Error creating past solution: {str(e)}')
            return redirect('/admin-dashboard/past-solutions-management/')
            
        elif action == 'update' and solution_id:
            # Update past solution
            try:
                solution = PastSolution.objects.get(id=solution_id)
                solution.title = request.POST.get('title', solution.title)
                solution.description = request.POST.get('description', solution.description)
                solution.client_name = request.POST.get('client_name', solution.client_name)
                solution.industry = request.POST.get('industry', solution.industry)
                solution.is_featured = 'is_featured' in request.POST
                solution.save()
                messages.success(request, f'Past solution "{solution.title}" updated successfully!')
            except PastSolution.DoesNotExist:
                messages.error(request, 'Past solution not found!')
            return redirect('/admin-dashboard/past-solutions-management/')
            
        elif action == 'delete' and solution_id:
            # Delete past solution
            try:
                solution = PastSolution.objects.get(id=solution_id)
                title = solution.title
                solution.delete()
                messages.success(request, f'Past solution "{title}" deleted!')
            except PastSolution.DoesNotExist:
                messages.error(request, 'Past solution not found!')
            return redirect('/admin-dashboard/past-solutions-management/')
    
    # Get all past solutions
    solutions = PastSolution.objects.all().order_by('-created_at')
    
    context = {
        'solutions': solutions,
        'total_solutions': solutions.count(),
        'featured_solutions': solutions.filter(is_featured=True).count()
    }
    
    return render(request, 'admin/past_solutions_management.html', context)

@login_required
def admin_profile(request):
    """Admin profile page with user information and settings"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            # Update user profile information
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            
            # Update profile information
            profile.phone = request.POST.get('phone', profile.phone)
            profile.department = request.POST.get('department', profile.department)
            profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('admin_profile')
            
        elif action == 'change_password':
            # Handle password change
            form = PasswordChangeForm(user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Password changed successfully!')
                return redirect('admin_profile')
            else:
                # Add form errors to messages
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Password {field}: {error}')
                return redirect('admin_profile')
    
    # Get user statistics
    user_stats = {
        'contacts_created': Contact.objects.count(),
        'testimonials_managed': Testimonial.objects.count(),
        'articles_created': Article.objects.filter(author=user).count(),
        'services_managed': Service.objects.count(),
        'events_managed': Event.objects.count(),
        'gallery_items': Gallery.objects.count(),
    }
    
    # Get recent activity
    recent_contacts = Contact.objects.all().order_by('-created_at')[:5]
    recent_testimonials = Testimonial.objects.all().order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'profile': profile,
        'user_stats': user_stats,
        'recent_contacts': recent_contacts,
        'recent_testimonials': recent_testimonials,
        'password_form': PasswordChangeForm(user),
        'roles': UserRole.objects.all(),
    }
    
    return render(request, 'admin/admin_profile.html', context)

@login_required
def edit_profile(request):
    """Edit profile page - display form for editing profile information"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            # Update user profile information
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            
            # Update profile information
            profile.phone = request.POST.get('phone', profile.phone)
            profile.department = request.POST.get('department', profile.department)
            profile.bio = request.POST.get('bio', profile.bio)
            profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('admin_profile')
    
    context = {
        'user': user,
        'profile': profile,
    }
    
    return render(request, 'admin/edit_profile.html', context)

@login_required
def change_password(request):
    """Change password page - display form for changing password"""
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'change_password':
            # Handle password change
            form = PasswordChangeForm(user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Password changed successfully!')
                return redirect('admin_profile')
            else:
                # Add form errors to messages
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Password {field}: {error}')
                return redirect('change_password')
    
    context = {
        'user': user,
        'password_form': PasswordChangeForm(user),
    }
    
    return render(request, 'admin/change_password.html', context)

@login_required
def update_profile_picture(request):
    """AJAX endpoint to update profile picture"""
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        try:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile picture updated successfully!',
                'image_url': profile.profile_picture.url
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating profile picture: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'No image provided'
    })


def custom_logout(request):
    """Custom logout view that directly redirects to login page"""
    from django.contrib.auth import logout
    
    # Logout the user
    logout(request)
    
    # Redirect directly to login page
    return redirect('/accounts/login/')
