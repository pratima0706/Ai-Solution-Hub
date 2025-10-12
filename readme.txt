AI Solution Hub - README

1) Overview
- Purpose: Central hub to explore, prototype, and manage AI-powered solutions for coursework, admin workflows, and demonstrations.
- Audience: Instructors, reviewers, admins, and contributors who manage or review AI solutions and content.
- Scope: Focuses on the admin panel for managing content and configuration; public-facing site is separate and must not be disrupted.

2) Key Features
- Secure Django-based admin panel for managing AI solution entries, inquiries, articles, events, gallery, and more
- User role management (superadmin, admin, content_manager, etc.)
- CSV data exports (contacts, solutions, newsletter, users, events, reports)
- Audit logging for critical admin actions
- Modular Django app structure for extensibility
- Email notifications and confirmations for form submissions
- Custom theming and dashboard analytics (KPI cards, charts, etc.)
- Environment-based configuration for safe local development

3) Tech Stack
- Language: Python 3.10+
- Backend: Django 5.2.5
- Database: SQLite (default, switchable)
- Email: SMTP (Gmail by default, configurable)
- Image handling: Pillow
- Frontend: Django templating, Tailwind CSS/vanilla CSS (check static/Static folders)
- Environment: dotenv (`python-dotenv`)

4) Project Structure (Django Example)
- AI_Solution_HubProject/              -> Django project root
    - AI_Solution_HubProject/          -> Main Django settings, URLs
    - Ai_SolutionApp/                  -> Main admin and public app (admin_views.py, models.py, etc.)
    - core/, operations/               -> Additional Django apps (if used)
    - Media/                           -> User-uploaded content/images
    - Static/, staticfiles/            -> Static files (admin CSS/JS, etc.)
    - requirements.txt                 -> Python dependencies
    - manage.py                        -> Django management script

5) Prerequisites
- Python 3.10 or higher
- pip (Python installer)
- Git (optional but recommended)
- Internet access to install dependencies

6) Setup (Windows PowerShell or macOS/Linux)
One-time setup:
  python -m venv myenv
  myenv\Scripts\activate  (or `source myenv/bin/activate` on macOS/Linux)
  pip install -r requirements.txt
  
- Copy `.env.example` to `.env` (create if missing) and set any secret keys/env variables needed for Django/email.

7) Running the App (Local)
- Run database migrations:
  python manage.py migrate
- Create a superuser for admin access:
  python manage.py createsuperuser
- Start development server:
  python manage.py runserver

- The admin panel is usually available at: http://localhost:8000/admin/
  (Custom admin at /admin/, custom dashboard, etc.)

8) Build & Deployment
- For deployment (e.g., Heroku, PythonAnywhere):
    - Set DEBUG=0
    - Set ALLOWED_HOSTS in `.env`
    - Configure static/media file serving as per hosting docs
    - Collect static: python manage.py collectstatic

9) Environment Variables (if used)
- Example .env file:
    SECRET_KEY=your_secret_key
    DEBUG=1
    EMAIL_HOST_USER=your_gmail@example.com
    EMAIL_HOST_PASSWORD=your_password
    ADMIN_EMAIL=where_admin_notifications_go@example.com
    
- Never commit secrets to public repos!

10) Admin Panel Usage
- Access: Visit /admin/ and login with superuser/admin credentials
- Content management for solutions, articles, events, users, gallery, etc.
- Use built-in user and role management for granular permissions
- Export data to CSV for reporting/auditing
- Make changes in dev/local/test environments before production; do NOT edit live when the public site is running

11) Management & Scripts
- Standard Django manage.py commands:
  - makemigrations/migrate
  - runserver/collectstatic
  - createsuperuser
  - shell/dbshell/test/loaddata/dumpdata
- Check `requirements.txt` for pip package list

12) Coding Standards
- Use clear, readable, and modular Django code
- PEP8 for Python code formatting
- Minimize logic in templates—keep it in views/models
- Leave comments/README updates for any non-obvious patterns

13) Testing
- Django tests can be run with:
  python manage.py test
- Add/extend tests in app/tests.py

14) Troubleshooting
- If static files not loading, run:
  python manage.py collectstatic
- Database issues: delete/recreate db.sqlite3 & rerun migrations
- SMTP/Email: check .env and Gmail 'App Passwords' if using Gmail

15) Contribution Workflow
- Create feature/bugfix branches
- Keep commits & PRs focused
- Ensure all code is tested before PR
- Do not merge with unresolved linter or test errors

16) Deployment Notes
- Ensure DEBUG=0 and all secrets/environment variables are set
- Use a dedicated production database/service for public deployments
- Set up daily/weekly routine data exports/backups for admin data

17) Maintenance
- Document any critical admin scripts, cron jobs, or new env vars
- Update this README whenever major architectural or workflow changes occur

18) Contact
- Maintainer: Add your name/contact here
- Course/Module: CET 333 Product Development - ISMT Level 6 (3rd Trimester)
