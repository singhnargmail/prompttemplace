# Prompt Management System

A comprehensive Python Flask application for managing prompt definitions and versions with PostgreSQL database integration.

## Features

- **Prompt Definition Management**: Create and manage different types of prompts (Persona Prompt, Advanced Prompt)
- **Version Control**: Multiple versions per prompt with draft/active/inactive status management
- **Web UI**: Complete web interface for managing prompts and versions
- **REST API**: External API endpoints for consuming active prompts
- **Database Integration**: PostgreSQL database with proper relationships and constraints
- **Docker Support**: Full containerization with Docker and Docker Compose

## Database Schema

### Tables

#### prompt_def
- `id` (Primary Key, Auto-generated)
- `prompt_type` (VARCHAR(255)) - Values: 'persona prompt' or 'advanced prompt'
- `createddate` (DATETIME) - Default: current timestamp

#### prompt_def_ver
- `id` (Primary Key, Auto-generated)
- `prompt_id` (Foreign Key → prompt_def.id)
- `prompt_value` (TEXT) - The actual prompt content
- `status` (VARCHAR(50)) - Values: 'draft', 'Active', 'Inactive' (Default: 'draft')
- `published_date` (DATETIME) - Set when published
- `published_by` (VARCHAR(255)) - User who published the version
- `createddate` (DATETIME) - Default: current timestamp
- `version` (INTEGER) - Version number

### Business Rules

1. One prompt_def can have multiple prompt_def_ver records
2. Only one prompt_def_ver can be in 'Active' status per prompt_def
3. New prompt_def_ver records are created in 'draft' status
4. Only 'draft' versions can be edited
5. Publishing a version sets it to 'Active' and all others to 'Inactive'

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- Docker (optional, for containerized deployment)

## Installation & Setup

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PromptTemplates
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your database configuration
   ```

5. **Set up PostgreSQL database**
   - Ensure PostgreSQL is running
   - Create database named 'sootro-postgres'
   - Update DATABASE_URL in .env file

6. **Run the application**
   ```bash
   python main.py
   ```

### Option 2: Docker Deployment

1. **Using existing PostgreSQL container**
   ```bash
   # If you already have sootro-postgres running on Docker
   docker build -t prompt-app .
   docker run -p 5000:5000 --network <your-postgres-network> prompt-app
   ```

2. **Using Docker Compose (includes PostgreSQL)**
   ```bash
   docker-compose up -d
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/sootro-postgres
FLASK_ENV=development
FLASK_DEBUG=True
```

### Database Connection

The application expects a PostgreSQL database running with the name `sootro-postgres`. Update the connection string in `.env` file as needed.

## Usage

### Web Interface

Access the web application at `http://localhost:5000`

#### Features:
- **Homepage**: View all prompt definitions
- **Create Prompt**: Create new prompt definitions with initial versions
- **Prompt Details**: View all versions of a specific prompt
- **Version Details**: View and edit individual prompt versions
- **Publishing**: Publish draft versions to make them active

#### Workflow:
1. Create a new prompt definition (persona prompt or advanced prompt)
2. Initial version is created in 'draft' status
3. Edit the prompt value as needed while in draft
4. Publish the version to make it active (deactivates other versions)
5. Create new versions for updates

### API Endpoints

#### For External Services (sn_agent app on port 8081)

**Get Active Persona Prompts**
```http
GET /api/getPersonaPrompts
```
Returns: Array of prompt_value strings where status='Active' and prompt_type='persona prompt'

**Get Active Advanced Prompts**
```http
GET /api/getAdvancedPrompts
```
Returns: Array of prompt_value strings where status='Active' and prompt_type='advanced prompt'

**Health Check**
```http
GET /health
```
Returns: Application health status

#### Example API Responses

```json
// GET /api/getPersonaPrompts
[
  "You are a helpful AI assistant specialized in providing clear and concise responses.",
  "You are an expert AI assistant with deep knowledge across multiple domains."
]

// GET /api/getAdvancedPrompts
[
  "Advanced prompt: Analyze the given context and provide detailed insights with supporting evidence."
]

// GET /health
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Project Structure

```
.
├── main.py                 # Main Flask application
├── models.py              # Database models and schemas
├── database.py            # Database configuration and initialization
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
├── Dockerfile            # Docker container configuration
├── docker-compose.yml    # Docker Compose configuration
├── .dockerignore         # Docker ignore file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── prompt_detail.html # Prompt details page
│   ├── version_detail.html # Version details page
│   ├── create_prompt.html # Create prompt form
│   └── edit_version.html  # Edit version form
├── static/               # Static files (CSS, JS)
│   ├── css/
│   └── js/
└── README.md            # This file
```

## API Integration

The sn_agent application running on Docker port 8081 can consume the prompt data using:

```python
import requests

# Get persona prompts
response = requests.get('http://localhost:5000/api/getPersonaPrompts')
persona_prompts = response.json()

# Get advanced prompts
response = requests.get('http://localhost:5000/api/getAdvancedPrompts')
advanced_prompts = response.json()
```

## Development

### Adding New Features

1. **Database Changes**: Update models in `models.py`
2. **API Endpoints**: Add routes in `main.py`
3. **UI Changes**: Update templates in `templates/`
4. **Styling**: Add CSS in `static/css/`

### Database Migrations

For schema changes, consider using Flask-Migrate:

```bash
pip install Flask-Migrate
# Add migration commands to your application
```

## Security Considerations

- Update the SECRET_KEY in production
- Use environment variables for sensitive configuration
- Implement proper authentication if needed
- Validate all user inputs
- Use HTTPS in production

## Monitoring

- Health check endpoint: `/health`
- Application logs are printed to stdout
- Database connection status is validated on startup

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check DATABASE_URL in .env file
   - Ensure database 'sootro-postgres' exists

2. **Port Already in Use**
   - Change port in main.py or docker-compose.yml
   - Kill existing processes using the port

3. **Module Import Errors**
   - Ensure virtual environment is activated
   - Install all requirements: `pip install -r requirements.txt`

### Logs

Check application logs for detailed error information:
```bash
# Local development
python main.py

# Docker
docker logs <container-name>
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

## License

This project is licensed under the MIT License.