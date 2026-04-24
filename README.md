# Personal Portfolio Website

A full-stack Django application serving as both a public portfolio and a private Content Management System (CMS). Built with Django 5.2, Django REST Framework, and PostgreSQL.

## Features

- **Dynamic Portfolio**: Automatically displays your profile, projects, skills, education, experience, and certificates
- **Admin Dashboard**: Protected CMS for managing all content via an intuitive web interface
- **REST API**: JSON API endpoints for dynamic frontend data fetching
- **Email-based Authentication**: Custom user model using email instead of username
- **Image Uploads**: Support for profile pictures, project screenshots, and certificate images via Cloudinary
- **Production Ready**: Configured for deployment on Render with PostgreSQL, Whitenoise, and Gunicorn

## Tech Stack

| Category | Technology |
|----------|------------|
| Backend | Django 5.2, Django REST Framework |
| Database | PostgreSQL (production), SQLite (development) |
| Frontend | HTML, CSS, JavaScript, jQuery |
| Authentication | Custom User Model with Email |
| File Storage | Cloudinary |
| Deployment | Render, Gunicorn, Whitenoise |
| Package Manager | Poetry |

## Project Structure

```
portfolio/
├── models.py          # Database models (Profile, Project, Skill, etc.)
├── views.py           # API views and dashboard logic
├── serializers.py     # DRF serializers for JSON conversion
├── urls.py           # URL routing
├── forms.py          # Authentication forms
└── management/       # Custom management commands

project/              # Django project settings
static/               # Static assets (CSS, JS)
templates/            # HTML templates
media/                # User-uploaded files
```

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry
- PostgreSQL (for production)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd personal-portfolio-website
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run migrations**
   ```bash
   poetry run python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   poetry run python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   poetry run python manage.py runserver
   ```

Visit `http://localhost:8000` for the portfolio and `http://localhost:8000/dashboard` for the admin panel.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Production |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | Yes |
| `CLOUDINARY_API_KEY` | Cloudinary API key | Yes |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | Yes |
| `DJANGO_SUPERUSER_EMAIL` | Auto-created admin email | Optional |
| `DJANGO_SUPERUSER_PASSWORD` | Auto-created admin password | Optional |

## Deployment

### Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Deploy automatically triggers on push

The `build.sh` script handles:
- Dependency installation via Poetry
- Static file collection
- Database migrations
- Auto-creation of superuser (if environment variables are set)

### Docker

```bash
docker build -t portfolio .
docker run -p 8000:8000 portfolio
```

## Models

- **CustomUser**: Email-based authentication
- **Profile**: Personal information and bio
- **Education**: Academic background
- **Experience**: Work history
- **Skill**: Technical skills with proficiency levels
- **Project**: Portfolio projects with images and links
- **Certificate**: Certifications and credentials
- **SocialLink**: Social media and contact links

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/portfolio/` | GET | Fetch all portfolio data |
| `/api/profile/` | GET/POST/PUT/DELETE | Profile CRUD operations |
| `/api/projects/` | GET/POST/PUT/DELETE | Projects CRUD operations |
| `/api/skills/` | GET/POST/PUT/DELETE | Skills CRUD operations |
| `/api/education/` | GET/POST/PUT/DELETE | Education CRUD operations |
| `/api/experience/` | GET/POST/PUT/DELETE | Experience CRUD operations |
| `/api/certificates/` | GET/POST/PUT/DELETE | Certificates CRUD operations |

## Security

- Superuser-only access to `/dashboard`
- CSRF protection on all forms
- Secure password hashing
- Environment-based configuration
- Whitenoise for secure static file serving

## License

This project is open source and available under the [MIT License](LICENSE).

## Author

**Jaswant** - [GitHub](https://github.com/Jas2005-ct)
