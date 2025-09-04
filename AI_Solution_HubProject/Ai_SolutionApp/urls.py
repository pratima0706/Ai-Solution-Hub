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
    
    # Admin dashboard (protected)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/export-csv/', views.export_contacts_csv, name='export_contacts_csv'),
    path('admin-dashboard/stats/', views.get_dashboard_stats, name='get_dashboard_stats'),
    path('admin-dashboard/contact/<uuid:contact_id>/update-status/', views.update_contact_status, name='update_contact_status'),
    path('admin-dashboard/contact-analysis/', views.contact_analysis, name='contact_analysis'),
    path('admin-dashboard/user-management/', views.user_management, name='user_management'),
    path('admin-dashboard/gallery-management/', views.gallery_management, name='gallery_management'),
    path('admin-dashboard/testimonials-management/', views.testimonials_management, name='testimonials_management'),
    path('admin-dashboard/services-management/', views.services_management, name='services_management'),
    path('admin-dashboard/events-management/', views.events_management, name='events_management'),
    path('admin-dashboard/articles-management/', views.articles_management, name='articles_management'),
    path('admin-dashboard/past-solutions-management/', views.past_solutions_management, name='past_solutions_management'),
    path('admin-dashboard/profile/', views.admin_profile, name='admin_profile'),
    path('admin-dashboard/profile/edit/', views.edit_profile, name='edit_profile'),
    path('admin-dashboard/profile/change-password/', views.change_password, name='change_password'),
    path('admin-dashboard/update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),
]
