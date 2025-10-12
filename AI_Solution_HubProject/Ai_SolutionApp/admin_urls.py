from django.urls import path
from . import admin_views
from .admin import custom_admin_site

app_name = 'admin'

urlpatterns = [
    # Login
    path('login/', custom_admin_site.login, name='login'),
    
    # Dashboard
    path('', admin_views.admin_dashboard, name='dashboard'),
    path('kpi-summary/', admin_views.kpi_summary, name='kpi_summary'),
    
    # Inquiries
    path('inquiries/', admin_views.inquiries_list, name='inquiries_list'),
    path('inquiries/<uuid:inquiry_id>/', admin_views.inquiry_detail, name='inquiry_detail'),
    path('inquiries/export/', admin_views.export_inquiries_csv, name='export_inquiries_csv'),
    
    # Subscribers
    path('subscribers/', admin_views.subscribers, name='subscribers'),
    path('subscribers/export/', admin_views.export_subscribers_csv, name='export_subscribers_csv'),
    
    # Content Management
    path('events/', admin_views.events, name='events'),
    path('events/export/', admin_views.export_events_csv, name='export_events_csv'),
    path('gallery/', admin_views.gallery, name='gallery'),
    path('gallery/add/', admin_views.add_gallery_image, name='add_gallery_image'),
    path('gallery/toggle-featured/', admin_views.toggle_gallery_featured, name='toggle_gallery_featured'),
    path('gallery/delete/', admin_views.delete_gallery_image, name='delete_gallery_image'),
    path('gallery/export/', admin_views.export_gallery_csv, name='export_gallery_csv'),
    path('testimonials/', admin_views.testimonials, name='testimonials'),
    path('testimonials/export/', admin_views.export_testimonials_csv, name='export_testimonials_csv'),
    path('articles/', admin_views.articles, name='articles'),
    path('articles/export/', admin_views.export_articles_csv, name='export_articles_csv'),
    path('services/', admin_views.services, name='services'),
    path('services/export/', admin_views.export_services_csv, name='export_services_csv'),
    path('past-solutions/', admin_views.past_solutions, name='past_solutions'),
    path('past-solutions/export/', admin_views.export_past_solutions_csv, name='export_past_solutions_csv'),
    
    # Pages (remove this)
    # path('pages/', admin_views.site_settings, name='pages'),
    # Add Forms
    path('forms/', admin_views.forms_list, name='forms'),
    path('forms/<uuid:form_id>/', admin_views.form_detail, name='form_detail'),
    path('forms/<uuid:form_id>/delete/', admin_views.form_delete, name='form_delete'),
    
    # Management
    path('site-settings/', admin_views.site_settings, name='site_settings'),
    path('users/', admin_views.users, name='users'),
    path('users/create/', admin_views.create_user, name='create_user'),
    path('users/<int:profile_id>/edit/', admin_views.edit_user, name='edit_user'),
    path('users/<int:profile_id>/json/', admin_views.get_user_json, name='get_user_json'),
    path('users/<int:profile_id>/toggle-status/', admin_views.toggle_user_status, name='toggle_user_status'),
    path('users/export/', admin_views.export_users_csv, name='export_users_csv'),
    path('audit-exports/', admin_views.audit_exports, name='audit_exports'),
    path('reports/', admin_views.reports, name='reports'),
    path('reports/export/csv/', admin_views.export_reports_csv, name='export_reports_csv'),
    
    # Profile
    path('profile/', admin_views.profile, name='profile'),
    
    # Notifications
    path('notifications/count/', admin_views.notifications_count, name='notifications_count'),
    path('notifications/list/', admin_views.notifications_list, name='notifications_list'),
]
