from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
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
    Testimonial, Article, AdminDashboard, SiteSettings
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
    
    gallery_images = Gallery.objects.filter(is_featured=True).order_by('order')[:12]
    
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
    testimonials = Testimonial.objects.all().order_by('-created_at')
    
    # Filtering by rating
    rating_filter = request.GET.get('rating')
    if rating_filter:
        testimonials = testimonials.filter(rating=int(rating_filter))
    
    # Pagination
    paginator = Paginator(testimonials, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
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
    return render(request, 'ai_solution_app/admin_dashboard.html', context)

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
