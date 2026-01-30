// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the HRMS database
db = db.getSiblingDB('hrms_lite');

// Create collections with validation rules
db.createCollection('employees', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['employee_id', 'full_name', 'email', 'department', 'position', 'salary', 'start_date', 'status'],
      properties: {
        employee_id: {
          bsonType: 'string',
          pattern: '^EMP\\d{3,}$',
          description: 'Employee ID must start with EMP followed by numbers'
        },
        full_name: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 100,
          description: 'Full name must be between 2 and 100 characters'
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
          description: 'Must be a valid email address'
        },
        department: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 50,
          description: 'Department must be between 2 and 50 characters'
        },
        position: {
          bsonType: 'string',
          minLength: 2,
          maxLength: 100,
          description: 'Position must be between 2 and 100 characters'
        },
        salary: {
          bsonType: 'double',
          minimum: 0,
          description: 'Salary must be a positive number'
        },
        start_date: {
          bsonType: 'date',
          description: 'Start date must be a valid date'
        },
        status: {
          bsonType: 'string',
          enum: ['active', 'inactive', 'on-leave'],
          description: 'Status must be one of: active, inactive, on-leave'
        }
      }
    }
  }
});

db.createCollection('attendance', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['employee_id', 'date', 'status', 'marked_by', 'marked_at'],
      properties: {
        employee_id: {
          bsonType: 'string',
          description: 'Employee ID reference'
        },
        date: {
          bsonType: 'date',
          description: 'Attendance date'
        },
        status: {
          bsonType: 'string',
          enum: ['present', 'absent'],
          description: 'Status must be either present or absent'
        },
        marked_by: {
          bsonType: 'string',
          description: 'Who marked the attendance'
        },
        marked_at: {
          bsonType: 'date',
          description: 'When attendance was marked'
        },
        notes: {
          bsonType: 'string',
          maxLength: 500,
          description: 'Optional notes (max 500 characters)'
        }
      }
    }
  }
});

// Create indexes for better performance
db.employees.createIndex({ 'employee_id': 1 }, { unique: true });
db.employees.createIndex({ 'email': 1 }, { unique: true });
db.employees.createIndex({ 'department': 1 });
db.employees.createIndex({ 'status': 1 });
db.employees.createIndex({ 'full_name': 'text', 'position': 'text' });

db.attendance.createIndex({ 'employee_id': 1, 'date': 1 }, { unique: true });
db.attendance.createIndex({ 'date': 1 });
db.attendance.createIndex({ 'status': 1 });
db.attendance.createIndex({ 'marked_at': -1 });

// Insert sample data (optional - for development)
if (db.employees.countDocuments() === 0) {
  // Sample employees
  db.employees.insertMany([
    {
      employee_id: 'EMP001',
      full_name: 'John Doe',
      email: 'john.doe@company.com',
      department: 'Engineering',
      position: 'Senior Developer',
      salary: 75000,
      start_date: new Date('2022-01-15'),
      status: 'active',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      employee_id: 'EMP002',
      full_name: 'Jane Smith',
      email: 'jane.smith@company.com',
      department: 'HR',
      position: 'HR Manager',
      salary: 65000,
      start_date: new Date('2021-06-01'),
      status: 'active',
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      employee_id: 'EMP003',
      full_name: 'Mike Johnson',
      email: 'mike.johnson@company.com',
      department: 'Sales',
      position: 'Sales Representative',
      salary: 55000,
      start_date: new Date('2023-03-10'),
      status: 'on-leave',
      created_at: new Date(),
      updated_at: new Date()
    }
  ]);

  // Sample attendance records
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  db.attendance.insertMany([
    {
      employee_id: 'EMP001',
      date: today,
      status: 'present',
      marked_by: 'admin',
      marked_at: new Date(),
      notes: 'On time'
    },
    {
      employee_id: 'EMP002',
      date: today,
      status: 'present',
      marked_by: 'admin',
      marked_at: new Date(),
      notes: 'Regular day'
    },
    {
      employee_id: 'EMP003',
      date: today,
      status: 'absent',
      marked_by: 'admin',
      marked_at: new Date(),
      notes: 'On leave'
    },
    {
      employee_id: 'EMP001',
      date: yesterday,
      status: 'present',
      marked_by: 'admin',
      marked_at: new Date(yesterday),
      notes: 'Productive day'
    },
    {
      employee_id: 'EMP002',
      date: yesterday,
      status: 'present',
      marked_by: 'admin',
      marked_at: new Date(yesterday),
      notes: 'Good performance'
    }
  ]);
}

print('HRMS Lite database initialized successfully!');
