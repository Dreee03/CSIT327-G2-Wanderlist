# Copilot Instructions for Wanderlist

## Project Overview
Wanderlist is a Django-based web application for travel planning and user account management. The codebase is organized into Django apps, with `accounts` handling authentication and user-related features, and `wanderlist` providing core project configuration and Supabase integration.

## Architecture & Key Components
- **Django Structure**: Follows standard Django conventions. Main apps: `accounts/` (user management), `wanderlist/` (project settings, Supabase client).
- **Supabase Integration**: External database access is managed via `wanderlist/supabase_client.py`. Use this for any direct Supabase operations.
- **Templates & Static Files**: HTML templates are in `templates/`. Static assets (CSS, images, videos) are in `static/`.
- **Settings**: Project configuration is in `wanderlist/settings.py`. Environment variables are referenced via `.env.example`.

## Developer Workflows
- **Run Server**: Use `python manage.py runserver` from the project root.
- **Migrations**: Apply with `python manage.py migrate`. Create with `python manage.py makemigrations`.
- **Testing**: Run tests using `python manage.py test`.
- **Environment**: Activate the virtual environment in `env/Scripts/Activate.ps1` (Windows PowerShell).

## Patterns & Conventions
- **Forms**: User forms are defined in `accounts/forms.py`.
- **Views**: Business logic and request handling are in `accounts/views.py`.
- **Models**: Database models are in `accounts/models.py`.
- **URLs**: Route definitions are in `accounts/urls.py` and `wanderlist/urls.py`.
- **Supabase Usage**: Always use the client in `wanderlist/supabase_client.py` for Supabase operations.
- **Environment Variables**: Reference `.env.example` for required variables. Do not hardcode secrets.

## Integration Points
- **Supabase**: All database interactions outside Django ORM should use the Supabase client.
- **Django ORM**: Use Django models for local database operations.

## Examples
- To add a new user feature, update `accounts/models.py`, `accounts/forms.py`, and `accounts/views.py` as needed, then expose via `accounts/urls.py`.
- For new Supabase queries, extend `wanderlist/supabase_client.py` and import where needed.

## Additional Notes
- Keep business logic in views, not templates.
- Static and template files should be referenced using Django's `{% static %}` and `{% url %}` tags.
- Follow Django's recommended file structure for maintainability.

---
For questions about unclear patterns or missing documentation, ask for clarification or request examples from maintainers.
