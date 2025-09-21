from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from Ai_SolutionApp.models import Contact, Event


class Command(BaseCommand):
    help = 'Send reminder emails to event participants before events start'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days before event to send reminder (default: 1)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )

    def handle(self, *args, **options):
        days_before = options['days']
        dry_run = options['dry_run']
        
        # Calculate the target date
        target_date = timezone.now().date() + timedelta(days=days_before)
        
        # Find events starting on the target date
        events = Event.objects.filter(
            start_date__date=target_date,
            start_date__gt=timezone.now()  # Only future events
        )
        
        if not events.exists():
            self.stdout.write(
                self.style.WARNING(f'No events found starting on {target_date}')
            )
            return
        
        total_reminders = 0
        
        for event in events:
            # Find all event registrations for this event that haven't received reminders
            registrations = Contact.objects.filter(
                form_type='event',
                event=event,
                reminder_sent=False
            )
            
            if not registrations.exists():
                self.stdout.write(
                    self.style.WARNING(f'No pending reminders for event: {event.title}')
                )
                continue
            
            self.stdout.write(f'Processing event: {event.title}')
            self.stdout.write(f'Found {registrations.count()} participants to remind')
            
            for registration in registrations:
                if dry_run:
                    self.stdout.write(
                        f'[DRY RUN] Would send reminder to: {registration.email} for event: {event.title}'
                    )
                else:
                    try:
                        # Send reminder email
                        subject = f'Reminder: {event.title} starts tomorrow!'
                        message = f"""
Dear {registration.name},

This is a friendly reminder that you are registered for our event:

Event: {event.title}
Date: {event.start_date.strftime('%B %d, %Y at %I:%M %p')}
Location: {event.location if event.location else 'Virtual Event'}
Event Type: {event.event_type.title()}

We look forward to seeing you at the event!

Best regards,
AI Solution Hub Team
                        """
                        
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [registration.email],
                            fail_silently=False,
                        )
                        
                        # Mark reminder as sent
                        registration.reminder_sent = True
                        registration.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'Reminder sent to: {registration.email}')
                        )
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to send reminder to {registration.email}: {str(e)}')
                        )
                
                total_reminders += 1
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'[DRY RUN] Would send {total_reminders} reminder emails')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully processed {total_reminders} reminder emails')
            )
