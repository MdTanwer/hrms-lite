import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.config.database import get_database
from app.config.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    """Create a test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_db():
    """Get test database instance"""
    # In a real implementation, you might want to use a separate test database
    db = await get_database()
    yield db
    
    # Cleanup test data
    if settings.debug:
        # Clean up test collections
        await db["employees"].delete_many({})
        await db["attendance"].delete_many({})


@pytest.fixture
def sample_employee_data():
    """Sample employee data for testing"""
    return {
        "employee_id": "TEST001",
        "full_name": "Test Employee",
        "email": "test.employee@company.com",
        "department": "Engineering",
        "position": "Test Developer",
        "salary": 60000.0,
        "start_date": "2024-01-01T00:00:00",
        "status": "active"
    }


@pytest.fixture
def sample_attendance_data():
    """Sample attendance data for testing"""
    return {
        "employee_id": "TEST001",
        "date": "2024-01-15T00:00:00",
        "status": "present",
        "marked_by": "admin",
        "notes": "On time"
    }
