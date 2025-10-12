from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Service, PastSolution, Event, Article

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['ai_solution_app:home', 'ai_solution_app:services', 'ai_solution_app:past_solutions', 
                'ai_solution_app:events_gallery', 'ai_solution_app:customer_feedback', 
                'ai_solution_app:articles_blog', 'ai_solution_app:about_us', 'ai_solution_app:contact_us']

    def location(self, item):
        return reverse(item)

class ServiceSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return Service.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

class PastSolutionSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return PastSolution.objects.filter(is_featured=True)

    def lastmod(self, obj):
        return obj.updated_at

class EventSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Event.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

class ArticleSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
