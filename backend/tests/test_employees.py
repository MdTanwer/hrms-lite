import pytest
from httpx import AsyncClient


class TestEmployeeEndpoints:
    """Test employee CRUD endpoints"""

    async def test_create_employee(self, client: AsyncClient, sample_employee_data):
        """Test creating a new employee"""
        response = await client.post("/api/v1/employees/", json=sample_employee_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["employee_id"] == sample_employee_data["employee_id"]
        assert data["email"] == sample_employee_data["email"]
        assert "id" in data
        assert "created_at" in data

    async def test_create_duplicate_employee_id(self, client: AsyncClient, sample_employee_data):
        """Test creating employee with duplicate ID should fail"""
        # Create first employee
        await client.post("/api/v1/employees/", json=sample_employee_data)
        
        # Try to create duplicate
        response = await client.post("/api/v1/employees/", json=sample_employee_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_create_duplicate_email(self, client: AsyncClient, sample_employee_data):
        """Test creating employee with duplicate email should fail"""
        # Create first employee
        await client.post("/api/v1/employees/", json=sample_employee_data)
        
        # Try to create with different ID but same email
        duplicate_data = sample_employee_data.copy()
        duplicate_data["employee_id"] = "TEST002"
        response = await client.post("/api/v1/employees/", json=duplicate_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_get_employees(self, client: AsyncClient, sample_employee_data):
        """Test getting list of employees"""
        # Create test employee
        await client.post("/api/v1/employees/", json=sample_employee_data)
        
        # Get employees
        response = await client.get("/api/v1/employees/")
        assert response.status_code == 200
        
        data = response.json()
        assert "employees" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert len(data["employees"]) >= 1

    async def test_get_employee_by_id(self, client: AsyncClient, sample_employee_data):
        """Test getting employee by ID"""
        # Create test employee
        create_response = await client.post("/api/v1/employees/", json=sample_employee_data)
        employee_id = create_response.json()["id"]
        
        # Get employee by ID
        response = await client.get(f"/api/v1/employees/{employee_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["employee_id"] == sample_employee_data["employee_id"]
        assert data["email"] == sample_employee_data["email"]

    async def test_get_nonexistent_employee(self, client: AsyncClient):
        """Test getting non-existent employee should return 404"""
        response = await client.get("/api/v1/employees/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_update_employee(self, client: AsyncClient, sample_employee_data):
        """Test updating employee"""
        # Create test employee
        create_response = await client.post("/api/v1/employees/", json=sample_employee_data)
        employee_id = create_response.json()["id"]
        
        # Update employee
        update_data = {"full_name": "Updated Name", "salary": 70000.0}
        response = await client.put(f"/api/v1/employees/{employee_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["salary"] == 70000.0

    async def test_delete_employee(self, client: AsyncClient, sample_employee_data):
        """Test deleting employee"""
        # Create test employee
        create_response = await client.post("/api/v1/employees/", json=sample_employee_data)
        employee_id = create_response.json()["id"]
        
        # Delete employee
        response = await client.delete(f"/api/v1/employees/{employee_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    async def test_get_employee_stats(self, client: AsyncClient, sample_employee_data):
        """Test getting employee statistics"""
        # Create test employee
        await client.post("/api/v1/employees/", json=sample_employee_data)
        
        # Get stats
        response = await client.get("/api/v1/employees/stats/overview")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_employees" in data
        assert "active_employees" in data
        assert "total_departments" in data
        assert "department_breakdown" in data
        assert data["total_employees"] >= 1

    async def test_employee_validation(self, client: AsyncClient):
        """Test employee data validation"""
        # Test invalid email
        invalid_data = {
            "employee_id": "TEST001",
            "full_name": "Test Employee",
            "email": "invalid-email",
            "department": "Engineering",
            "position": "Developer",
            "salary": 60000.0,
            "start_date": "2024-01-01T00:00:00",
            "status": "active"
        }
        
        response = await client.post("/api/v1/employees/", json=invalid_data)
        assert response.status_code == 422

    async def test_filter_employees_by_department(self, client: AsyncClient, sample_employee_data):
        """Test filtering employees by department"""
        # Create test employee
        await client.post("/api/v1/employees/", json=sample_employee_data)
        
        # Filter by department
        response = await client.get("/api/v1/employees/?department=Engineering")
        assert response.status_code == 200
        
        data = response.json()
        for employee in data["employees"]:
            assert employee["department"] == "Engineering"

    async def test_search_employees(self, client: AsyncClient, sample_employee_data):
        """Test searching employees"""
        # Create test employee
        await client.post("/api/v1/employees/", json=sample_employee_data)
        
        # Search employee
        response = await client.get("/api/v1/employees/?search=Test")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["employees"]) >= 1
        for employee in data["employees"]:
            assert "Test" in employee["full_name"] or "Test" in employee["employee_id"]
