from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache
from django.contrib.sessions.models import Session
import json
import csv
from datetime import datetime, timedelta
from .models import (
    Contact, Service, PastSolution, Event, Gallery, 
    Testimonial, Article, AdminDashboard, SiteSettings, UserProfile, UserRole, NewsletterSubscriber
)
from .forms import ContactForm, NewsletterForm, DemoRequestForm, EventRegistrationForm

def home(request):
    """Home page view with featured content and gallery images"""
    context = {
        'services': Service.objects.filter(is_featured=True)[:6],
        'solutions': PastSolution.objects.filter(is_featured=True)[:3],
        'testimonials': Testimonial.objects.filter(is_featured=True)[:3],
        'events': Event.objects.filter(is_featured=True, start_date__gte=timezone.now())[:3],
        'articles': Article.objects.filter(is_featured=True, is_published=True)[:2],
        'gallery_images': Gallery.objects.filter(is_featured=True).order_by('order', '-created_at')[:8],
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/home.html', context)

def services(request):
    """Services page view"""
    services_qs = Service.objects.all().order_by('order', 'title')
    paginator = Paginator(services_qs, 6)  # 2 x 3 grid per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
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
    
    # Get featured solutions for case studies section
    featured_solutions = PastSolution.objects.filter(is_featured=True).order_by('-completion_date')[:3]
    
    context = {
        'page_obj': page_obj,
        'solutions': solutions_list,
        'featured_solutions': featured_solutions,
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
    """Events and gallery page view with enhanced image support"""
    upcoming_events = Event.objects.filter(
        start_date__gte=timezone.now()
    ).order_by('start_date')[:6]
    
    past_events = Event.objects.filter(
        start_date__lt=timezone.now()
    ).order_by('-start_date')[:6]
    
    # Get all gallery images with pagination
    gallery_images = Gallery.objects.all().order_by('order', '-created_at')
    
    # Pagination for gallery
    paginator = Paginator(gallery_images, 12)
    page_number = request.GET.get('page')
    gallery_page = paginator.get_page(page_number)
    
    # Get featured images for carousel
    featured_images = Gallery.objects.filter(is_featured=True).order_by('order', '-created_at')[:8]
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'gallery_images': gallery_page,
        'featured_images': featured_images,
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
    
    # Pass registration form to template
    registration_form = EventRegistrationForm(initial={'form_type': 'event'})
    
    context = {
        'event': event,
        'related_events': related_events,
        'gallery_images': gallery_images,
        'site_settings': SiteSettings.get_settings(),
        'registration_form': registration_form,
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
                messages.success(request, 'Thank you! Your testimonial has been submitted and will appear on our website after a short review by our team.')
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
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.form_type = 'contact'  # Ensure form_type is set
            contact.save()
            
            # Add success message
            from django.contrib import messages
            messages.success(request, 'Thank you for your inquiry! We will get back to you within 24 hours.')
            
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
                    'AI Solution Hub <contact@aisolutionhub.com>',
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
                    'AI Solution Hub <contact@aisolutionhub.com>',
                    [admin_email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't fail the form submission
                print(f"Failed to send admin email: {e}")
            
            return redirect('/contact/')
        # No messages.error here; errors will be shown inline in the template
    else:
        form = ContactForm(initial={'form_type': 'contact'})
    
    context = {
        'form': form,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/contact_us.html', context)

def schedule_demo(request):
    """Handle Schedule Demo form submissions (AJAX or normal POST)"""
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['form_type'] = 'demo'
        form = ContactForm(post_data, request.FILES)
        if form.is_valid():
            contact = form.save()
            if request.is_ajax() or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Thank you! Your demo request has been submitted.'})
            else:
                return redirect('home')
        else:
            if request.is_ajax() or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            # No messages.error here; errors will be shown inline
    else:
        form = ContactForm(initial={'form_type': 'demo'})
    return render(request, 'ai_solution_app/home.html', {'form': form})

def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'ai_solution_app/404.html', status=404)

def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'ai_solution_app/500.html', status=500)

def newsletter_subscribe(request):
    """Newsletter subscription view"""
    form = NewsletterForm(request.POST)
    
    if form.is_valid():
        try:
            subscriber = form.save(request=request)
            return JsonResponse({
                'success': True,
                'message': 'Thank you for subscribing to our newsletter!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            })
    else:
        errors = form.errors.get('email', [])
        return JsonResponse({
            'success': False,
            'message': errors[0] if errors else 'Please enter a valid email address.'
        })

def custom_login(request):
    """Custom login view with rate limiting and remember me functionality"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember')
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f"login_attempts:{client_ip}"
        attempt = cache.get(cache_key, {"count": 0, "blocked_until": None})

        # Block if currently within cooldown
        now = timezone.now()
        if attempt.get("blocked_until") and now < attempt["blocked_until"]:
            remaining = int((attempt["blocked_until"] - now).total_seconds())
            messages.error(request, f'Too many attempts. Try again in {remaining}s.')
            return render(request, 'admin/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Reset attempt counter on success
            cache.delete(cache_key)
            
            # Handle remember me functionality
            if remember_me:
                # Set session to expire in 30 days
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
            else:
                # Set session to expire when browser closes
                request.session.set_expiry(0)
            
            messages.success(request, 'Login successful! Welcome to AI Solution Hub.')
            return redirect('/admin/')
        else:
            # Increment attempts and set cooldown when threshold reached
            attempt["count"] = int(attempt.get("count", 0)) + 1
            if attempt["count"] >= 5:
                attempt["count"] = 0
                attempt["blocked_until"] = now + timedelta(seconds=60)
            cache.set(cache_key, attempt, timeout=120)
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'admin/login.html')

def demo_request(request):
    """Demo request page view with form handling"""
    if request.method == 'POST':
        form = DemoRequestForm(request.POST)
        if form.is_valid():
            # Set form_type to 'demo' for demo requests
            demo = form.save(commit=False)
            demo.form_type = 'demo'
            demo.job_title = form.cleaned_data.get('interest', 'Demo Request')
            demo.job_details = form.cleaned_data.get('message', 'Demo request submitted')
            demo.save()
            
            # Send confirmation email to customer
            try:
                customer_subject = f'Thank you for your demo request, {demo.name}!'
                customer_message = f"""
Dear {demo.name},

Thank you for requesting a demo of our AI solutions! We have received your request and our team will contact you within 24-48 hours to schedule your personalized demonstration.

Request Details:
- Interest: {demo.interest}
- Company: {demo.company}
- Country: {demo.country}
- Message: {demo.message or 'No additional message provided'}

We look forward to showing you how our AI solutions can benefit your business.

Best regards,
AI Solution Hub Team
                """
                
                send_mail(
                    customer_subject,
                    customer_message,
                    'AI Solution Hub <contact@aisolutionhub.com>',
                    [demo.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't fail the form submission
                print(f"Failed to send customer email: {e}")
            
            # Send notification email to admin
            try:
                admin_subject = f'New Demo Request from {demo.name} - {demo.company}'
                admin_message = f"""
New demo request received:

Name: {demo.name}
Email: {demo.email}
Phone: {demo.phone}
Company: {demo.company}
Country: {demo.country}
Interest: {demo.interest}
Message: {demo.message or 'No additional message provided'}
Status: {demo.status}
Created: {demo.created_at}

Please review and respond within 24-48 hours.
                """
                
                # Send to admin email
                admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@aisolutionhub.com')
                send_mail(
                    admin_subject,
                    admin_message,
                    'AI Solution Hub <contact@aisolutionhub.com>',
                    [admin_email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't fail the form submission
                print(f"Failed to send admin email: {e}")
            
            return redirect('ai_solution_app:demo_request_success')
        # No messages.error here; errors will be shown inline
    else:
        form = DemoRequestForm(initial={'form_type': 'demo'})
    
    context = {
        'form': form,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/demo_request.html', context)

def demo_request_success(request):
    """Demo request success page"""
    context = {
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/demo_request_success.html', context)

def custom_logout(request):
    """Custom logout view that directly redirects to login page"""
    from django.contrib.auth import logout
    
    # Logout the user
    logout(request)
    
    # Redirect directly to login page
    return redirect('/accounts/login/')

def event_register(request, event_id):
    """Event registration view with enhanced functionality"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            if not event.registration_open:
                messages.error(request, 'Registration for this event is closed or full.')
                return redirect('ai_solution_app:event_detail', event_id=event.id)

            registration = form.save(commit=False)
            registration.form_type = 'event'
            registration.event = event
            registration.job_title = f"Event Registration: {event.title}"
            registration.job_details = f"Registered for event: {event.title} (ID: {event.id})"
            registration.interest = 'promotional_events'  # Set interest for event registrations
            registration.save()

            # Increment event participants
            event.current_participants += 1
            event.save()

            # Send confirmation email to customer
            try:
                customer_subject = f'Event Registration Confirmed: {event.title}'
                customer_message = f"""
Dear {registration.name},

Thank you for registering for our event "{event.title}"!

Event Details:
- Date: {event.start_date.strftime('%B %d, %Y at %I:%M %p')}
- Location: {event.location if event.location else 'Virtual Event'}
- Event Type: {event.event_type.title()}

We look forward to seeing you at the event. You will receive a reminder email closer to the event date.

Best regards,
AI Solution Hub Team
                """
                
                send_mail(
                    customer_subject,
                    customer_message,
                    'AI Solution Hub <contact@aisolutionhub.com>',
                    [registration.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send customer email: {e}")
            
            # Send notification email to admin
            try:
                admin_subject = f'New Event Registration: {event.title} - {registration.name}'
                admin_message = f"""
New event registration received:

Event: {event.title}
Name: {registration.name}
Email: {registration.email}
Phone: {registration.phone}
Country: {registration.country}
Registration Date: {registration.created_at}

Total participants for this event: {event.current_participants}
                """
                
                admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@aisolutionhub.com')
                send_mail(
                    admin_subject,
                    admin_message,
                    'AI Solution Hub <contact@aisolutionhub.com>',
                    [admin_email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send admin email: {e}")
            
            return redirect('ai_solution_app:event_registration_success', event_id=event.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EventRegistrationForm(initial={'form_type': 'event'})
    
    context = {
        'form': form,
        'event': event,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/event_detail.html', context)

def event_registration_success(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    context = {
        'event': event,
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'ai_solution_app/event_registration_success.html', context)

