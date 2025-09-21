from django.urls import path
from . import views

app_name = 'ai_solution_app'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('services/<uuid:service_id>/', views.service_detail, name='service_detail'),
    path('past-solutions/', views.past_solutions, name='past_solutions'),
    path('past-solutions/<uuid:solution_id>/', views.solution_detail, name='solution_detail'),
    path('events-gallery/', views.events_gallery, name='events_gallery'),
    path('events/<uuid:event_id>/', views.event_detail, name='event_detail'),
    path('customer-feedback/', views.customer_feedback, name='customer_feedback'),
    path('articles/', views.articles_blog, name='articles_blog'),
    path('articles/<slug:article_slug>/', views.article_detail, name='article_detail'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    
    # Newsletter subscription
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Admin dashboard (protected) - will be rebuilt
    # path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('schedule-demo/', views.schedule_demo, name='schedule_demo'),
    path('demo-request/', views.demo_request, name='demo_request'),
    path('demo-request/success/', views.demo_request_success, name='demo_request_success'),
    path('event/<uuid:event_id>/register/', views.event_register, name='event_register'),
    path('event/<uuid:event_id>/registration-success/', views.event_registration_success, name='event_registration_success'),
]
