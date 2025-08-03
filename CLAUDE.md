# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

This is a Flask-based Prompt Management System that allows creating, versioning, and managing prompt definitions with a PostgreSQL database backend. The application serves both a web UI for prompt management and REST APIs for external consumption by services like the sn_agent application.

## Development Commands

### Running the Application

**Local Development:**
```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```
 
**Docker Development:**
```bash
# Build and run with Docker Compose (uses existing PostgreSQL on host)
docker-compose up -d

# Build image only
docker build -t prompt-app .

# View logs
docker logs <container-name>
```

### Database Setup

The application uses the existing PostgreSQL database `sootro_metadata` running on the host system (port 5432). The Docker configuration connects to the existing PostgreSQL container via the `log-analyzer_sootro-network`. Environment configuration is handled via `.env` file:

```env
DATABASE_URL=postgresql://sootro:dev_password@localhost:5432/sootro_metadata
FLASK_ENV=development
FLASK_DEBUG=True
```

### Testing and Health Check

- Health endpoint: `GET /health`
- API endpoints for testing:
  - `GET /api/getPersonaPrompts` - Returns active persona prompts
  - `GET /api/getAdvancedPrompts` - Returns active advanced prompts

## Architecture and Code Structure

### Core Architecture

**Three-Layer MVC Pattern:**
1. **Models** (`models.py`) - SQLAlchemy ORM models with Marshmallow serialization
2. **Views/Controllers** (`main.py`) - Flask routes for both web UI and API endpoints  
3. **Database Layer** (`database.py`) - Database initialization and configuration

### Key Components

**Database Models:**
- `PromptDef` - Main prompt definitions with type classification
- `PromptDefVer` - Version management with status workflow (draft → Active → Inactive)

**Business Logic Rules:**
- Only one version per prompt can be "Active" at a time
- Only "draft" versions can be edited
- Publishing a version automatically deactivates all other versions of the same prompt
- Version numbers are managed manually during creation

**Status Workflow:**
```
draft → Active (via publish) → Inactive (when new version published)
```

**Version Creation Workflow:**
1. **Initial Version**: Created with prompt definition using provided prompt value
2. **New Versions**: Created via "Create New Version" button with blank prompt value and draft status
3. **Auto-incrementing**: Version numbers automatically increment (v1, v2, v3, etc.)
4. **Redirect**: New versions automatically redirect to edit page for immediate content entry

### Key File Responsibilities

- `main.py` - Main Flask application with all routes (web UI + API endpoints)
- `models.py` - SQLAlchemy models and Marshmallow schemas for serialization
- `database.py` - Database configuration, initialization, and sample data creation
- `templates/` - Jinja2 HTML templates for web UI
- `static/` - CSS and JavaScript assets

### Database Schema Design

**Prompt Definition** (`prompt_def`):
- `id` (PK), `prompt_type` (persona prompt|advanced prompt), `createddate`

**Prompt Version** (`prompt_def_ver`):
- `id` (PK), `prompt_id` (FK), `prompt_value` (TEXT), `status`, `version`, `published_date`, `published_by`, `createddate`
- Constraint: status must be 'draft', 'Active', or 'Inactive'

### API Integration Pattern

The application is designed to serve the `sn_agent` application running on port 8081. API endpoints return arrays of prompt_value strings filtered by:
- Prompt type (persona vs advanced)
- Active status only

### Dependencies and Framework Choices

**Core Dependencies:**
- Flask 2.3.3 with SQLAlchemy 3.0.5 for web framework and ORM
- psycopg2-binary for PostgreSQL connectivity
- marshmallow + flask-marshmallow for API serialization
- python-dotenv for environment configuration
- Bootstrap 5.1.3 and Font Awesome 6.0.0 for UI (CDN-based)

**Design Decisions:**
- Uses Flask-SQLAlchemy ORM instead of raw SQL for database abstraction
- Marshmallow schemas enable clean API serialization
- Bootstrap provides responsive UI without custom CSS complexity
- Docker Compose simplifies development environment setup

### Error Handling Patterns

- Database operations wrapped in try/catch with rollback on failure
- Flash messages for user feedback in web UI
- JSON error responses for API endpoints
- 404 handling via `get_or_404()` for resource access

### Security Considerations

- Uses non-root user in Docker container
- Database connection via environment variables
- Basic input validation on form submissions
- Secret key placeholder (needs production replacement)