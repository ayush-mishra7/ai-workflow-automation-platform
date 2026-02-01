# AI Workflow Automation Platform 🚀

> A production-ready workflow automation platform that lets you build, execute, and monitor complex multi-step workflows with the power of asynchronous task processing.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.3-green.svg)](https://docs.celeryproject.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 🎯 Why I Built This

As a developer, I've always been fascinated by automation and how it can transform tedious, repetitive tasks into seamless, background processes. I wanted to create something that not only showcases modern backend development practices but also solves a real problem: **orchestrating complex workflows without manual intervention**.

Whether it's processing data pipelines, running AI inference models, sending notifications, or coordinating multiple services, this platform handles it all asynchronously with proper error handling, retry logic, and real-time tracking.

This project is my answer to the question: *"How do we build reliable, scalable automation systems that just work?"*

---

## ✨ What It Does

Imagine you need to:
1. Fetch customer data from an API
2. Clean and transform that data
3. Run AI sentiment analysis
4. Send results via email

Instead of running these steps manually or writing custom scripts, you simply **define a workflow** with these steps, hit "start," and watch it execute in the background. The platform handles:

- ✅ **Sequential execution** of each step
- ✅ **Automatic retries** if something fails (with exponential backoff)
- ✅ **Real-time progress tracking** with detailed logs
- ✅ **State persistence** so you never lose progress
- ✅ **User isolation** so everyone's workflows stay private

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│              (curl, Postman, Frontend Apps)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST + JWT Auth
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django REST API                           │
│  ┌──────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │   accounts   │  │    workflows    │  │  Swagger UI   │  │
│  │  (JWT Auth)  │  │  (CRUD + Exec)  │  │  (API Docs)   │  │
│  └──────────────┘  └─────────────────┘  └───────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌──────────┐   ┌─────────┐   ┌──────────┐
    │PostgreSQL│   │  Redis  │   │  Celery  │
    │ (Models) │   │(Broker) │   │ (Worker) │
    └──────────┘   └─────────┘   └──────────┘
```

The platform follows a **microservices-inspired architecture** where each component has a clear responsibility:

- **Django REST API**: Handles HTTP requests, authentication, and business logic
- **PostgreSQL**: Stores workflows, executions, and logs with ACID guarantees
- **Redis**: Acts as message broker and result backend for Celery
- **Celery Workers**: Execute workflows asynchronously in the background

---

## 🛠️ Tech Stack

### Backend Framework
- **Python 3.11** - Modern Python with performance improvements
- **Django 4.2** - Robust web framework with ORM and admin interface
- **Django REST Framework** - Powerful toolkit for building Web APIs

### Database & Caching
- **PostgreSQL 15** - Production-grade relational database
- **Redis 7** - In-memory data store for caching and message brokering

### Task Queue
- **Celery 5.3** - Distributed task queue for async processing
- **django-celery-beat** - Periodic task scheduler (optional)

### Authentication
- **djangorestframework-simplejwt** - JWT authentication for stateless API security

### API Documentation
- **drf-yasg** - Automatic Swagger/OpenAPI documentation generation

### DevOps & Deployment
- **Docker** - Containerization for consistent environments
- **Docker Compose** - Multi-container orchestration
- **Gunicorn** - Production WSGI server

### Testing
- **pytest** - Modern testing framework
- **pytest-django** - Django integration for pytest
- **pytest-cov** - Code coverage reporting

---

## 🎨 Key Features

### 1. **JWT-Based Authentication** 🔐
- Secure user registration and login
- Token-based authentication (no sessions needed)
- Automatic token refresh mechanism
- Password hashing with Django's built-in security

### 2. **Workflow Management** 📋
- Create workflows with multiple ordered steps
- Four built-in step types:
  - `data_fetch` - Fetch data from external sources
  - `data_process` - Transform and clean data
  - `ai_inference` - Run AI/ML models
  - `notify_user` - Send notifications
- JSON-based step configuration for flexibility
- Full CRUD operations via REST API

### 3. **Asynchronous Execution** ⚡
- Background task processing with Celery
- Non-blocking workflow execution
- Concurrent workflow support
- Real-time status updates

### 4. **Robust Error Handling** 🛡️
- Automatic retry with exponential backoff (60s, 120s, 240s)
- Idempotent task design (safe to retry)
- Detailed error messages and stack traces
- Graceful failure recovery

### 5. **State Persistence** 💾
- Progress saved after each step
- Resume from last successful step on retry
- Complete execution history
- Step-level timing and duration tracking

### 6. **Real-Time Monitoring** 📊
- Track workflow execution status (CREATED/RUNNING/SUCCESS/FAILED)
- View detailed logs for each step
- Monitor current step progress
- Access execution history

### 7. **User Isolation** 👥
- Each user can only access their own workflows
- Custom permission classes
- Secure data separation
- Multi-tenant ready

### 8. **Interactive API Documentation** 📚
- Auto-generated Swagger UI
- Try-it-out functionality
- Request/response examples
- Authentication integration

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git (for cloning)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ayush-mishra7/ai-workflow-automation-platform.git
   cd ai-workflow-automation-platform
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings (optional for local dev)
   ```

3. **Build and start services**
   ```bash
   docker-compose up --build -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose run --rm web python manage.py makemigrations
   docker-compose run --rm web python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   docker-compose run --rm web python manage.py createsuperuser
   ```

6. **Access the application**
   - **API Documentation**: http://localhost:8000/api/docs/
   - **Django Admin**: http://localhost:8000/admin/
   - **API Base URL**: http://localhost:8000/api/

---

## 📖 Usage Guide

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

**Response:**
```json
{
  "user": {
    "id": "uuid-here",
    "username": "john",
    "email": "john@example.com"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "User registered successfully"
}
```

### 2. Create a Workflow

```bash
curl -X POST http://localhost:8000/api/workflows/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Customer Analytics Pipeline",
    "description": "Process customer data and generate insights",
    "steps": [
      {
        "type": "data_fetch",
        "name": "Fetch Customer Data",
        "config": {
          "source": "customer_database",
          "delay": 2
        }
      },
      {
        "type": "data_process",
        "name": "Clean Data",
        "config": {
          "operation": "normalize",
          "delay": 3
        }
      },
      {
        "type": "ai_inference",
        "name": "Sentiment Analysis",
        "config": {
          "model": "sentiment_v2",
          "delay": 5
        }
      },
      {
        "type": "notify_user",
        "name": "Send Report",
        "config": {
          "channel": "email",
          "recipient": "admin@company.com",
          "delay": 1
        }
      }
    ]
  }'
```

### 3. Start Workflow Execution

```bash
curl -X POST http://localhost:8000/api/workflows/{workflow_id}/start/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "execution_id": "execution-uuid",
  "task_id": "celery-task-id",
  "status": "CREATED",
  "message": "Workflow execution started"
}
```

### 4. Check Execution Status

```bash
curl -X GET http://localhost:8000/api/workflows/{workflow_id}/status/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": "execution-uuid",
  "status": "SUCCESS",
  "current_step": 4,
  "started_at": "2026-02-01T10:30:00Z",
  "finished_at": "2026-02-01T10:30:11Z",
  "logs": [
    {
      "step_name": "Fetch Customer Data",
      "status": "SUCCESS",
      "message": "Successfully fetched data from customer_database",
      "duration_seconds": 2.01
    },
    // ... more logs
  ]
}
```

---

## 🧪 Testing

The platform includes a comprehensive test suite with **17 automated tests** covering:
- Model creation and validation
- API endpoints and authentication
- Celery task execution
- Error handling and retry logic
- User isolation and permissions

### Run Tests

```bash
# Run all tests
docker-compose run --rm web python manage.py test

# Run with pytest
docker-compose run --rm web pytest -v

# Run with coverage
docker-compose run --rm web pytest --cov=workflows --cov=accounts
```

**Test Results:**
```
Ran 17 tests in 9.709s
OK
```

---

## 📁 Project Structure

```
ai-workflow-automation-platform/
├── config/                     # Django project settings
│   ├── settings.py            # Main configuration
│   ├── urls.py                # Root URL routing
│   ├── celery.py              # Celery configuration
│   └── exceptions.py          # Custom error handlers
│
├── accounts/                   # Authentication app
│   ├── models.py              # User model with UUID
│   ├── serializers.py         # Auth serializers
│   ├── views.py               # Registration & login
│   └── urls.py                # Auth endpoints
│
├── workflows/                  # Core workflow app
│   ├── models.py              # Workflow, Execution, Log models
│   ├── serializers.py         # Workflow serializers
│   ├── views.py               # Workflow ViewSets
│   ├── tasks.py               # Celery tasks (main logic)
│   ├── permissions.py         # Custom permissions
│   ├── admin.py               # Admin interface
│   ├── tests.py               # Test suite
│   └── urls.py                # Workflow endpoints
│
├── docker-compose.yml          # Multi-container setup
├── Dockerfile                  # Docker image definition
├── requirements.txt            # Python dependencies
├── manage.py                   # Django CLI
├── pytest.ini                  # Test configuration
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=workflow_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

---

## 🌐 Production Deployment

### Deployment Platforms

This platform is ready to deploy on:

- **AWS EC2** - Full control with Nginx + Gunicorn
- **Render** - Easy deployment with managed services
- **Railway** - Automatic deployments from GitHub
- **DigitalOcean** - App Platform or Droplets
- **Heroku** - With PostgreSQL and Redis add-ons

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Use managed PostgreSQL (AWS RDS, etc.)
- [ ] Use managed Redis (AWS ElastiCache, etc.)
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS for frontend
- [ ] Scale Celery workers based on load
- [ ] Set up logging (CloudWatch, Datadog)
- [ ] Configure database backups
- [ ] Implement rate limiting
- [ ] Add monitoring and alerts

### Gunicorn Configuration

```bash
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers $((2 * $(nproc) + 1)) \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-workflow-automation-platform.git

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

---

## 📝 API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/auth/register/` | POST | Register new user | No |
| `/api/auth/login/` | POST | Login user | No |
| `/api/auth/token/refresh/` | POST | Refresh JWT token | No |
| `/api/workflows/` | GET | List workflows | Yes |
| `/api/workflows/` | POST | Create workflow | Yes |
| `/api/workflows/{id}/` | GET | Get workflow details | Yes |
| `/api/workflows/{id}/` | PUT/PATCH | Update workflow | Yes |
| `/api/workflows/{id}/` | DELETE | Delete workflow | Yes |
| `/api/workflows/{id}/start/` | POST | Start execution | Yes |
| `/api/workflows/{id}/status/` | GET | Get latest status | Yes |
| `/api/workflows/{id}/executions/` | GET | List executions | Yes |

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL status
docker-compose ps db

# View database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U postgres -d workflow_db
```

### Celery Tasks Not Running

```bash
# Check Celery worker logs
docker-compose logs -f celery

# Verify Redis connection
docker-compose exec redis redis-cli ping

# Check task queue
docker-compose exec redis redis-cli -n 0 KEYS '*'
```

### Port Already in Use

```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Restart
docker-compose up --build
```

---

## 📊 Performance

- **API Response Time**: ~100-300ms
- **Workflow Execution**: Sequential with minimal overhead (~0.9%)
- **Database Queries**: Optimized with select_related and prefetch_related
- **Concurrent Workflows**: Supports multiple simultaneous executions

---

## 🔒 Security

- **JWT Authentication**: Stateless, secure token-based auth
- **Password Hashing**: Django's PBKDF2 algorithm
- **SQL Injection**: Protected by Django ORM
- **XSS Protection**: DRF serializer validation
- **CORS**: Configurable allowed origins
- **User Isolation**: Custom permission classes

---

## 👨‍💻 Author

**Ayush Mishra**

- GitHub: [@ayush-mishra7](https://github.com/ayush-mishra7)
- Email: ayush963ash@gmail.com

---

## 🙏 Acknowledgments

- Django and DRF communities for excellent documentation
- Celery team for robust task queue implementation
- PostgreSQL and Redis teams for reliable data storage
- Docker for making deployment a breeze

---

## 🌟 Star This Project

If you find this project useful, please consider giving it a star ⭐ on GitHub. It helps others discover it!

---

**Built with ❤️ and lots of ☕**
