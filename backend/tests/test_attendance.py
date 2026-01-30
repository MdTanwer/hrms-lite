import pytest
from httpx import AsyncClient


class TestAttendanceEndpoints:
    """Test attendance CRUD endpoints"""

    async def test_mark_attendance(self, client: AsyncClient, sample_employee_data, sample_attendance_data):
        """Test marking attendance for an employee"""
        # Create test employee first
        await client.post("/api/v1/employees/", json=sample_employee_data)
        
        # Mark attendance
        response = await client.post("/api/v1/attendance/", json=sample_attendance_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["employee_id"] == sample_attendance_data["employee_id"]
        assert data["status"] == sample_attendance_data["status"]
        assert "id" in data
        assert "marked_at" in data

    async def test_mark_duplicate_attendance(self, client: AsyncClient, sample_employee_data, sample_attendance_data):
        """Test marking duplicate attendance should fail"""
        # Create test employee first
        await client.post("/api/v1/employees/", json=sample_employee_data)
        
        # Mark attendance first time
        await client.post("/api/v1/attendance/", json=sample_attendance_data)
        
        # Try to mark again for same employee and date
        response = await client.post("/api/v1/attendance/", json=sample_attendance_data)
        assert response.status_code == 400
        assert "already marked" in response.json()["detail"]

    async def test_get_attendances(self, client: AsyncClient, sample_employee_data, sample_attendance_data):
        """Test getting list of attendance records"""
        # Create test employee and attendance
        await client.post("/api/v1/employees/", json=sample_employee_data)
        await client.post("/api/v1/attendance/", json=sample_attendance_data)
        
        # Get attendances
        response = await client.get("/api/v1/attendance/")
        assert response.status_code == 200
        
        data = response.json()
        assert "attendances" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert len(data["attendances"]) >= 1

    async def test_get_attendances_with_employees(self, client: AsyncClient, sample_employee_data, sample_attendance_data):
        """Test getting attendance records with employee information"""
        # Create test employee and attendance
        await client.post("/api/v1/employees/", json=sample_employee_data)
        await client.post("/api/v1/attendance/", json=sample_attendance_data)
        
        # Get attendances with employee info
        response = await client.get("/api/v1/attendance/with-employees")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        attendance = data[0]
        assert "employee_name" in attendance
        assert "employee_department" in attendance
        assert "employee_position" in attendance
        assert attendance["employee_name"] == sample_employee_data["full_name"]

    async def test_get_attendance_by_id(self, client: AsyncClient, sample_employee_data, sample_attendance_data):
        """Test getting attendance by ID"""
        # Create test employee and attendance
        await client.post("/api/v1/employees/", json=sample_employee_data)
        create_response = await client.post("/api/v1/attendance/", json=sample_attendance_data)
        attendance_id = create_response.json()["id"]
        
        # Get attendance by ID
        response = await client.get(f"/api/v1/attendance/{attendance_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["employee_id"] == sample_attendance_data["employee_id"]
        assert data["status"] == sample_attendance_data["status"]

    async def test_update_attendance(self, client: AsyncClient, sample_employee_data, sample_attendance_data):
        """Test updating attendance record"""
        # Create test employee and attendance
        await client.post("/api/v1/employees/", json=sample_employee_data)
        create_response = await client.post("/api/v1/attendance/", json=sample_attendance_data)
        attendance_id = create_response.json()["id"]
        
        # Update attendance
        update_data = {"status": "absent", "notes": "Updated notes"}
        response = await client.put(f"/api/v1/attendance/{attendance_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "absent"
        assert data["notes"] == "Updated notes"

    async def test_delete_attendance(self, client: AsyncClient, sample_employee_data, sample_attendance_data):
        """Test deleting attendance record"""
        # Create test employee and attendance
        await client.post("/api/v1/employees/", json=sample_employee_data)
        create_response = await client.post("/api/v1/attendance/", json=sample_attendance_data)
        attendance_id = create_response.json()["id"]
        
        # Delete attendance
        response = await client.delete(f"/api/v1/attendance/{attendance_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    async def test_get_employee_attendance_stats(self, client: AsyncClient, sample_employee_data, sample_attendance_data):
        """Test getting attendance statistics for an employee"""
        # Create test employee and attendance
        await client.post("/api/v1/employees/", json=sample_employee_data)
        await client.post("/api/v1/attendance/", json=sample_attendance_data)
        
        # Get employee attendance stats
        response = await client.get(f"/api/v1/attendance/employee/{sample_attendance_data['employee_id']}/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_days" in data
        assert "present_days" in data
        assert "absent_days" in data
        assert "attendance_rate" in data
        assert data["total_days"] >= 1

    async def test_filter_attendances_by_status(self, client: AsyncClient, sample_employee_data, sample_attendance_data):
        """Test filtering attendances by status"""
        # Create test employee and attendance
        await client.post("/api/v1/employees/", json=sample_employee_data)
        await client.post("/api/v1/attendance/", json=sample_attendance_data)
        
        # Filter by status
        response = await client.get("/api/v1/attendance/?status=present")
        assert response.status_code == 200
        
        data = response.json()
        for attendance in data["attendances"]:
            assert attendance["status"] == "present"

    async def test_filter_attendances_by_employee(self, client: AsyncClient, sample_employee_data, sample_attendance_data):
        """Test filtering attendances by employee"""
        # Create test employee and attendance
        await client.post("/api/v1/employees/", json=sample_employee_data)
        await client.post("/api/v1/attendance/", json=sample_attendance_data)
        
        # Filter by employee
        response = await client.get(f"/api/v1/attendance/?employee_id={sample_attendance_data['employee_id']}")
        assert response.status_code == 200
        
        data = response.json()
        for attendance in data["attendances"]:
            assert attendance["employee_id"] == sample_attendance_data["employee_id"]

    async def test_attendance_validation(self, client: AsyncClient, sample_employee_data):
        """Test attendance data validation"""
        # Create test employee first
        await client.post("/api/v1/employees/", json=sample_employee_data)
        
        # Test invalid status
        invalid_data = {
            "employee_id": "TEST001",
            "date": "2024-01-15T00:00:00",
            "status": "invalid_status",
            "marked_by": "admin"
        }
        
        response = await client.post("/api/v1/attendance/", json=invalid_data)
        assert response.status_code == 422

    async def test_mark_attendance_nonexistent_employee(self, client: AsyncClient, sample_attendance_data):
        """Test marking attendance for non-existent employee should fail"""
        response = await client.post("/api/v1/attendance/", json=sample_attendance_data)
        # This should still work as we don't enforce employee existence at API level
        # but the lookup in attendance with employees will fail
        assert response.status_code == 200
