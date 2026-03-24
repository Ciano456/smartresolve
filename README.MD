# SmartResolve

SmartResolve is an internal support platform for managing incidents, service requests, change requests, access requests, and report or data requests.

The project is being built as a Django-based ticketing system for internal use, with support for user management, role-based access, ticket tracking, reporting, notifications. 

## Current Status

The project is currently in early development.

Completed so far:
- Django project setup
- custom user model
- custom user manager
- initial migrations
- admin access
- base settings cleanup
- static and media configuration

In progress:
- foundation and repo setup
- documentation
- CI setup

Not started yet:
- full authentication flow
- groups and role permissions
- ticket models and workflows
- dashboard reporting
- notifications

## Tech Stack

- Python
- Django
- SQLite for local development
- Pytest / Django test tools
- Ruff and Black listed in requirements for code quality

## Project Structure

- `smartresolve/` main project settings and URL configuration
- `accounts/` custom user model and account-related logic
- `tickets/` ticketing models and workflow
- `adminportal/` internal admin UI
- `dashboard/` reporting and dashboard features
- `notifications/` notification logic
- `ml/` future AI-related features

## Local Setup

### 1. Clone the project

```bash
git clone https://github.com/Ciano456/smartresolve.git
cd smartresolve
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

On macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Set up environment variables

Create a `.env` file in the project root.

Use `.env.example` as the reference.

Example values:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
```

## Database Setup

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Create an Admin User

```bash
python manage.py createsuperuser
```

Because the project uses a custom user model, login is based on email.

## Run the Development Server

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/admin/
```

## Running Checks and Tests

Run Django system checks:

```bash
python manage.py check
```

Check for missing migrations:

```bash
python manage.py makemigrations --check --dry-run
```

Run tests:

```bash
python manage.py test
```

## Development Approach

This project is being built in phases.

### Sprint 1
- foundation and repo setup
- custom user model
- settings cleanup
- admin validation
- environment setup
- documentation
- CI

### Sprint 2
- login and logout
- groups and roles
- permission helpers
- account/profile page

### Sprint 3 onward
- user administration
- ticket master data
- ticket workflows
- staff queue
- notifications
- dashboard reporting
- deployment preparation

## Branch Strategy

- `main` for stable code only
- `develop` for integration work
- `feature/<name>` for new features
- `hotfix/<name>` for urgent fixes

Example branch names:
- `feature/custom-user-model`
- `feature/admin-user-management`
- `feature/ticket-models`

## Notes

This is an internal-use project and is still under active development. The initial focus is on building a stable foundation before moving into ticket workflows and reporting features.
