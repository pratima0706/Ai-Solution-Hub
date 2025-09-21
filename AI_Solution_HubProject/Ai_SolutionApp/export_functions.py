from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta, datetime
import csv
import json

from .models import (
    Contact, Service, PastSolution, Event, Gallery, Testimonial, 
    Article, NewsletterSubscriber, UserProfile, UserRole, ExportLog, SiteSettings
)
from django.contrib.auth.models import User

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

@login_required
@user_passes_test(is_content_manager)
def export_gallery_csv(request):
    """Export gallery to CSV"""
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
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="gallery_export.csv"'
        response.write('\ufeff')  # BOM for Excel
        
        writer = csv.writer(response)
        
        # Write filter summary
        filter_summary = f"Search: {search}, Category: {category}, Featured: {featured}"
        writer.writerow([f"Export: {filter_summary}"])
        writer.writerow([])  # Empty row
        
        # Write headers
        writer.writerow([
            'Title', 'Category', 'Description', 'Alt Text', 'Featured', 'Hero Image', 'Order', 'Tags', 'Created At'
        ])
        
        # Write data
        for item in queryset:
            writer.writerow([
                item.title,
                item.get_category_display(),
                item.description or '',
                item.alt_text or '',
                'Yes' if item.is_featured else 'No',
                'Yes' if item.is_hero_image else 'No',
                item.order,
                ', '.join(item.tags) if item.tags else '',
                item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Log export
        ExportLog.objects.create(
            user=request.user,
            model='Gallery',
            filter_summary=filter_summary
        )
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting gallery: {str(e)}')
        return redirect('djadmin:gallery')

@login_required
@user_passes_test(is_content_manager)
def export_testimonials_csv(request):
    """Export testimonials to CSV"""
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
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="testimonials_export.csv"'
        response.write('\ufeff')  # BOM for Excel
        
        writer = csv.writer(response)
        
        # Write filter summary
        filter_summary = f"Search: {search}, Rating: {rating}, Featured: {featured}, Verified: {verified}"
        writer.writerow([f"Export: {filter_summary}"])
        writer.writerow([])  # Empty row
        
        # Write headers
        writer.writerow([
            'Customer Name', 'Company', 'Job Title', 'Rating', 'Review', 'Featured', 'Verified', 'Created At'
        ])
        
        # Write data
        for testimonial in queryset:
            writer.writerow([
                testimonial.customer_name,
                testimonial.company,
                testimonial.job_title,
                testimonial.rating,
                testimonial.review,
                'Yes' if testimonial.is_featured else 'No',
                'Yes' if testimonial.is_verified else 'No',
                testimonial.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Log export
        ExportLog.objects.create(
            user=request.user,
            model='Testimonial',
            filter_summary=filter_summary
        )
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting testimonials: {str(e)}')
        return redirect('djadmin:testimonials')

@login_required
@user_passes_test(is_content_manager)
def export_articles_csv(request):
    """Export articles to CSV"""
    try:
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
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="articles_export.csv"'
        response.write('\ufeff')  # BOM for Excel
        
        writer = csv.writer(response)
        
        # Write filter summary
        filter_summary = f"Search: {search}, Category: {category}, Status: {status}, Featured: {featured}"
        writer.writerow([f"Export: {filter_summary}"])
        writer.writerow([])  # Empty row
        
        # Write headers
        writer.writerow([
            'Title', 'Slug', 'Author', 'Category', 'Excerpt', 'Published', 'Featured', 'Views', 'Created At', 'Published At'
        ])
        
        # Write data
        for article in queryset:
            writer.writerow([
                article.title,
                article.slug,
                article.author.get_full_name() or article.author.username,
                article.category,
                article.excerpt,
                'Yes' if article.is_published else 'No',
                'Yes' if article.is_featured else 'No',
                article.views_count,
                article.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                article.published_at.strftime('%Y-%m-%d %H:%M:%S') if article.published_at else ''
            ])
        
        # Log export
        ExportLog.objects.create(
            user=request.user,
            model='Article',
            filter_summary=filter_summary
        )
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting articles: {str(e)}')
        return redirect('djadmin:articles')

@login_required
@user_passes_test(is_content_manager)
def export_services_csv(request):
    """Export services to CSV"""
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
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="services_export.csv"'
        response.write('\ufeff')  # BOM for Excel
        
        writer = csv.writer(response)
        
        # Write filter summary
        filter_summary = f"Search: {search}, Pricing Tier: {pricing_tier}, Featured: {featured}"
        writer.writerow([f"Export: {filter_summary}"])
        writer.writerow([])  # Empty row
        
        # Write headers
        writer.writerow([
            'Title', 'Description', 'Icon', 'Pricing Tier', 'Featured', 'Order', 'Features', 'Created At'
        ])
        
        # Write data
        for service in queryset:
            writer.writerow([
                service.title,
                service.description,
                service.icon,
                service.get_pricing_tier_display(),
                'Yes' if service.is_featured else 'No',
                service.order,
                ', '.join(service.features) if service.features else '',
                service.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Log export
        ExportLog.objects.create(
            user=request.user,
            model='Service',
            filter_summary=filter_summary
        )
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting services: {str(e)}')
        return redirect('djadmin:services')

@login_required
@user_passes_test(is_content_manager)
def export_past_solutions_csv(request):
    """Export past solutions to CSV"""
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
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="past_solutions_export.csv"'
        response.write('\ufeff')  # BOM for Excel
        
        writer = csv.writer(response)
        
        # Write filter summary
        filter_summary = f"Search: {search}, Industry: {industry}, Featured: {featured}"
        writer.writerow([f"Export: {filter_summary}"])
        writer.writerow([])  # Empty row
        
        # Write headers
        writer.writerow([
            'Title', 'Client Name', 'Industry', 'Description', 'Challenge', 'Solution', 'Results', 'Technologies', 'Featured', 'Completion Date', 'Created At'
        ])
        
        # Write data
        for solution in queryset:
            writer.writerow([
                solution.title,
                solution.client_name,
                solution.industry,
                solution.description,
                solution.challenge,
                solution.solution,
                solution.results,
                ', '.join(solution.technologies_used) if solution.technologies_used else '',
                'Yes' if solution.is_featured else 'No',
                solution.completion_date.strftime('%Y-%m-%d'),
                solution.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Log export
        ExportLog.objects.create(
            user=request.user,
            model='PastSolution',
            filter_summary=filter_summary
        )
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting past solutions: {str(e)}')
        return redirect('djadmin:past_solutions')
