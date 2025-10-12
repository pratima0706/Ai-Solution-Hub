"""
URL configuration for AI_Solution_HubProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from Ai_SolutionApp.admin import custom_admin_site
from Ai_SolutionApp import views
from Ai_SolutionApp.sitemap import StaticViewSitemap, ServiceSitemap, PastSolutionSitemap, EventSitemap, ArticleSitemap

def robots_txt(request):
    """Serve robots.txt to fix 404 error"""
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /django-admin/
Sitemap: https://aisolutionhub.com/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')

def chrome_devtools_json(request):
    """Handle Chrome DevTools requests to prevent 404 errors"""
    return HttpResponse('{}', content_type='application/json')

def favicon_ico(request):
    """Handle favicon.ico requests to prevent 404 errors"""
    return HttpResponse('', content_type='image/x-icon')

# Sitemap configuration
sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'solutions': PastSolutionSitemap,
    'events': EventSitemap,
    'articles': ArticleSitemap,
}

urlpatterns = [
    # Fix 404 errors
    path('robots.txt', robots_txt, name='robots_txt'),
    path('.well-known/appspecific/com.chrome.devtools.json', chrome_devtools_json, name='chrome_devtools'),
    path('favicon.ico', favicon_ico, name='favicon'),
    
    # Sitemap for SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # Custom Admin Panel
    path('admin/', include('Ai_SolutionApp.admin_urls')),
    # Legacy admin-dashboard redirect for backward compatibility
    path('admin-dashboard/', lambda request: redirect('/admin/')),
    # Django Admin (fallback)
    path('django-admin/', admin.site.urls),
    path('', include('Ai_SolutionApp.urls')),
    # Authentication URLs
    path('accounts/login/', views.custom_login, name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    # Password reset URLs (using Django default templates for now)
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
