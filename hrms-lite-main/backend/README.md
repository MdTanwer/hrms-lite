# HRMS Lite Backend

A production-grade FastAPI backend for the HRMS Lite application, providing RESTful APIs for employee management and attendance tracking.

## 🚀 Features

### Core Functionality
- **Employee Management**: CRUD operations for employee records
- **Attendance Tracking**: Mark and manage employee attendance
- **Dashboard Statistics**: Comprehensive analytics and reporting
- **Data Validation**: Robust input validation with Pydantic
- **Error Handling**: Comprehensive error management
- **Database Integration**: MongoDB with async support (Motor)

### Production Features
- **Async/Await**: Full async support for high performance
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **CORS Support**: Configurable cross-origin resource sharing
- **Environment Configuration**: Pydantic settings management
- **Docker Support**: Production-ready containerization
- **Testing**: Comprehensive test suite with pytest
- **Code Quality**: Type hints, linting, and formatting

## 📋 Requirements

- Python 3.11+
- MongoDB 5.0+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start MongoDB**
   ```bash
   # Using Docker
   docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password mongo:7.0
   
   # Or install locally
   # Follow MongoDB installation guide for your OS
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Development

1. **Using Docker Compose (Recommended)**
   ```bash
   docker-compose up -d
   ```

2. **Build and run manually**
   ```bash
   docker build -t hrms-backend .
   docker run -p 8000:8000 --env-file .env hrms-backend
   ```

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Environment configuration
│   │   └── database.py         # MongoDB connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── employee.py         # Employee Pydantic models
│   │   └── attendance.py       # Attendance Pydantic models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── employee.py         # Request/Response schemas
│   │   └── attendance.py       # Request/Response schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependency injection
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # Main API router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── employees.py    # Employee endpoints
│   │           ├── attendance.py   # Attendance endpoints
│   │           └── dashboard.py    # Dashboard endpoints
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py             # Base CRUD operations
│   │   ├── employee.py         # Employee CRUD
│   │   └── attendance.py       # Attendance CRUD
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py         # Security utilities
│   │   └── exceptions.py       # Custom exceptions
│   ├── utils/
│   │   ├── __init__.py
│   │   └── validators.py       # Custom validators
│   └── middleware/
│       ├── __init__.py
│       ├── cors.py             # CORS configuration
│       └── error_handler.py    # Error handling
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_employees.py
│   └── test_attendance.py
├── .env.example
├── .env
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DB_NAME` | Database name | `hrms_lite` |
| `APP_NAME` | Application name | `HRMS Lite Backend` |
| `DEBUG` | Debug mode | `False` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `["http://localhost:3000"]` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_employees.py

# Run with verbose output
pytest -v
```

### Test Coverage

The test suite covers:
- Employee CRUD operations
- Attendance CRUD operations
- Data validation
- Error handling
- API endpoints
- Database operations

## 📊 API Endpoints

### Employees
- `GET /api/v1/employees/` - List employees (with pagination, filtering)
- `POST /api/v1/employees/` - Create employee
- `GET /api/v1/employees/{id}` - Get employee by ID
- `PUT /api/v1/employees/{id}` - Update employee
- `DELETE /api/v1/employees/{id}` - Delete employee
- `GET /api/v1/employees/stats/overview` - Employee statistics

### Attendance
- `GET /api/v1/attendance/` - List attendance records
- `POST /api/v1/attendance/` - Mark attendance
- `GET /api/v1/attendance/with-employees` - Attendance with employee info
- `GET /api/v1/attendance/{id}` - Get attendance by ID
- `PUT /api/v1/attendance/{id}` - Update attendance
- `DELETE /api/v1/attendance/{id}` - Delete attendance
- `GET /api/v1/attendance/employee/{employee_id}/stats` - Employee attendance stats

### Dashboard
- `GET /api/v1/dashboard/overview` - Complete dashboard overview
- `GET /api/v1/dashboard/attendance/daily` - Daily attendance stats
- `GET /api/v1/dashboard/attendance/summary` - Attendance summary
- `GET /api/v1/dashboard/department/attendance` - Department attendance stats

## 🔒 Security Features

- **Input Validation**: Comprehensive Pydantic validation
- **Data Sanitization**: Custom validators for business logic
- **Error Handling**: Secure error responses
- **CORS Protection**: Configurable origin restrictions
- **JWT Support**: Ready for authentication implementation

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set production environment variables
   export DEBUG=False
   export SECRET_KEY=your-production-secret-key
   export MONGODB_URL=mongodb://your-production-db
   ```

2. **Using Docker**
   ```bash
   docker build -t hrms-backend:latest .
   docker run -d --name hrms-backend -p 8000:8000 --env-file .env hrms-backend:latest
   ```

3. **Using Docker Compose**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

### Health Checks

- **Health Endpoint**: `GET /health`
- **Docker Health Check**: Automatic container health monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the test files for usage examples

## 🔄 Version History

- **v1.0.0** - Initial release with core HRMS functionality
  - Employee management
  - Attendance tracking
  - Dashboard statistics
  - Production-ready features
