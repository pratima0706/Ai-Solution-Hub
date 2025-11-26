# AI Solution Hub

**Author:** Pratima Neupane

---

## Overview
AI Solution Hub is a comprehensive, full-stack Django application designed to manage, demonstrate, 
and audit AI-powered solutions, events, articles, and related business content. 
This platform features a modern, responsive interface, powerful admin tools, 
and secure, role-based user management, making it ideal for organizations, teams, 
or academic projects requiring scalable content, data integrity, and advanced business workflows.

---

## Key Highlights
- **Custom Admin Dashboard:** Interactive analytics, KPIs, recent activities, and audit logs.
- **Advanced Role Management:** Granular permissions (Superadmin, Admin, Content Manager, Analyst) using extended `UserProfile` and `UserRole` models.
- **Data Exports with Audit Logging:** Export filtered data directly to CSV; every export and admin activity is audit-logged for accountability.
- **Beautiful Public Site:** Modern landing page, filterable AI solution showcase, event and gallery sections, scalable article/blog features, and more—all mobile-first.
- **Robust Forms & Notifications:** Strong form validation (anti-spam, dynamic validation), email confirmation/alerts, and seamless workflows for contacts, demo requests, and event registration.
- **Developer Friendly:** Modular Django apps, clear project structure, testable code, and easy theming/extension for fast developer onboarding.

---

## Technologies Used
- **Backend:** Django 5.x, Python 3.10+
- **Frontend:** Django Templates, Tailwind CSS, Vanilla JS
- **Database:** SQLite (pluggable to PostgreSQL, MySQL)
- **Media Handling:** Pillow for optimized image uploads
- **Security:** Custom RBAC, Django best practices, dotenv
- **Deployment Ready:** Static/media-ready, WhiteNoise, .env for config

---

## Feature Overview
- **Admin Panel:**
    - Dashboard analytics (KPIs, visual summaries, activity logs)
    - Manage AI solutions, users, articles, testimonials, forms, events, gallery, newsletters
    - Role-based views and permissions
    - Filtered and auditable CSV data exports
- **Public-Facing Site:**
    - Responsive homepage, services, articles, gallery, events, contact forms
    - JS-powered carousels, modal galleries, filter/search UIs
    - Accessible, production-grade forms with user feedback
    - Live newsletter signup, contact inquiries, demo/event registration

---

## Why This Project Stands Out
- **End-to-End Engineering:** Full design and implementation of complex admin workflows, rich-data CMS, and secure, modern web UIs—all from scratch.
- **Production-Grade Best Practices:** Audit logging, email notifications, modularity, JS enhancements, and robust validation.
- **Professional Polish:** Theming, interactive UI/UX, clean responsive design, and standards-focused development—ready for real deployment, demonstration, or extension.

---

## Quick Start
```bash
# Clone and enter the project
$ git clone https://github.com/pratimaneupane/ai-solution-hub.git
$ cd AI-Solution\ Hub/AI_Solution_HubProject

# Setup virtual environment and install dependencies
$ python -m venv myenv
$ myenv\Scripts\activate   # Win
$ source myenv/bin/activate  # Mac/Linux
$ pip install -r requirements.txt

# Setup .env, run migrations, and create admin
$ cp .env.example .env
$ python manage.py migrate
$ python manage.py createsuperuser

# Start the server
$ python manage.py runserver
```
Visit `http://localhost:8000/admin/` to start exploring.

---

## Project Structure
```
AI_Solution_HubProject/
  ├── AI_Solution_HubProject/    # Django config, templates
  ├── Ai_SolutionApp/           # Main app: models, views, admin, forms, templates
  ├── core/, operations/        # Additional apps (optional modules)
  ├── Static/                   # Tailwind/JS/images
  ├── Media/                    # Uploaded media
  ├── requirements.txt, manage.py
```

---

---

## Testing
Run all integrated Django tests:
```
python manage.py test
```

---

## Deployment Notes
- Use `.env` for all secrets, SMTP, and production settings
- `DEBUG=0`, set `ALLOWED_HOSTS`, and run `python manage.py collectstatic` for production
- Supports quick deployment to Heroku, PythonAnywhere, or on-prem servers

---

## Contact & Links
**Project by:** Pratima Neupane  
**LinkedIn:** www.linkedin.com/in/pratima-neupane-3aa307365
**Email:** pratimaneupane0706@gmail.com  
**GitHub:** https://github.com/pratima0706

---

> *Developed for CET 333 Product Development – ISMT Level 6 (3rd Trimester).*
> 
> _AI Solution Hub demonstrates mastery of Django, security, role-based admin, modern UI/UX, exportable data, and scalable app design._
