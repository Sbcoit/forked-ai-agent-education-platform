# Unit Tests - CrewAI Agent Builder Platform Backend

This directory contains comprehensive unit tests for the CrewAI Agent Builder Platform backend API.

## 🗂️ **Test Organization**

Our tests are organized into logical categories for better maintainability:

```
unit_tests/
├── 📁 auth/                    # Authentication & user management tests
│   └── test_authentication.py # Complete auth system testing (20 tests)
├── 📁 api/                     # API endpoint tests
│   ├── test_scenarios.py       # Scenario CRUD operations
│   ├── test_agents.py          # Agent management & marketplace
│   └── test_simulations.py     # Simulation workflow testing
├── 📁 core/                    # Core functionality tests  
│   ├── test_health.py          # Health check endpoints
│   └── test_root.py            # Root API endpoints
├── conftest.py                 # Shared test configuration & fixtures
└── README.md                   # This documentation
```

## 🚀 **Running Tests**

### **All Tests**
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run with coverage report
python -m pytest --cov=. --cov-report=html
```

### **Specific Test Categories**
```bash
# Authentication tests only
python -m pytest auth/ -v

# API endpoint tests only  
python -m pytest api/ -v

# Core functionality tests only
python -m pytest core/ -v

# Specific test file
python -m pytest auth/test_authentication.py -v
```

### **Parallel Testing**
```bash
# Run tests in parallel (faster execution)
python -m pytest -n auto
```

## 🔧 **Test Configuration**

### **Database Setup**
- **Primary**: Neon PostgreSQL (`EdTechPlatfrom_TestBase`)
- **Schema**: Automatically created/updated via `conftest.py`
- **Data**: Preserved between test runs for inspection
- **Isolation**: Each test uses fresh fixtures

### **Test Fixtures**
Our `conftest.py` provides comprehensive fixtures:

#### **Database Fixtures**
- `test_db` - Test database setup
- `client` - FastAPI test client
- `db_session` - Database session for direct queries

#### **Data Fixtures**
- `sample_user` - Basic user for testing
- `sample_scenario` - Test business scenario
- `sample_agent` - Test AI agent
- `sample_simulation` - Test simulation session

#### **Authentication Fixtures**
- `sample_user_with_password` - User with hashed password
- `authenticated_user` - User with valid JWT token
- `admin_user` - Admin user with elevated permissions

#### **Request Data Fixtures**
- `valid_scenario_data` - Valid POST data for scenarios
- `valid_agent_data` - Valid POST data for agents
- `valid_simulation_data` - Valid POST data for simulations
- `valid_chat_message` - Valid chat message format

## 📊 **Test Coverage**

### **Authentication System (20 tests)**
- ✅ User registration with validation
- ✅ JWT login/logout with security
- ✅ Password management (change, hashing)
- ✅ Profile management (public/private)
- ✅ Role-based access control
- ✅ Admin user management functions

### **API Endpoints (55+ tests)**
- ✅ Scenario CRUD operations
- ✅ Agent marketplace functionality
- ✅ Simulation workflow management
- ✅ Error handling & validation
- ✅ Data persistence & relationships

### **Core Functionality (10+ tests)**
- ✅ Health check monitoring
- ✅ Root API responses
- ✅ CORS and security headers
- ✅ Database connectivity

## 🎯 **Test Quality Standards**

### **Best Practices**
- **Isolation**: Each test is independent
- **Cleanup**: Fixtures handle setup/teardown
- **Realistic Data**: Tests use representative data
- **Error Cases**: Both success and failure scenarios tested
- **Performance**: Tests run efficiently in parallel

### **Naming Conventions**
- Test files: `test_<feature>.py`
- Test classes: `Test<FeatureName>`
- Test methods: `test_<action>_<expected_result>`

### **Documentation**
- Every test has descriptive docstrings
- Complex tests include inline comments
- Fixtures are well-documented

## 🔍 **Debugging Tests**

### **Failed Test Investigation**
```bash
# Run specific failing test with detailed output
python -m pytest auth/test_authentication.py::TestUserAuthentication::test_login_success -v -s

# Run with debugger on failures
python -m pytest --pdb auth/test_authentication.py

# Show test execution time
python -m pytest --durations=10
```

### **Database Inspection**
Since test data is preserved, you can inspect the test database directly:
- **Database**: `EdTechPlatfrom_TestBase` on Neon PostgreSQL  
- **Tables**: All tables created with test data
- **Users**: Sample users with various roles and configurations

## 🚀 **Adding New Tests**

### **New Test File**
1. Create in appropriate folder (`auth/`, `api/`, or `core/`)
2. Follow naming convention: `test_<feature>.py`
3. Import fixtures from `conftest.py`
4. Use appropriate test classes and methods

### **Example Test Structure**
```python
import pytest
from fastapi import status

class TestNewFeature:
    \"\"\"Test cases for new feature\"\"\"
    
    def test_feature_success(self, client, sample_user):
        \"\"\"Test successful feature operation\"\"\"
        response = client.get(f"/new-endpoint/{sample_user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
    
    def test_feature_validation_error(self, client):
        \"\"\"Test feature with invalid input\"\"\"
        response = client.post("/new-endpoint", json={})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
```

## 📈 **Continuous Integration**

These tests are designed to run in CI/CD environments:
- **Fast execution**: Optimized for parallel testing
- **Reliable**: Stable fixtures and data handling  
- **Comprehensive**: High coverage of critical paths
- **Informative**: Clear failure messages and reporting

## 🎉 **Current Status**

**✅ 85+ Tests Passing**
- Authentication: 20/20 ✅
- Scenarios: 15+ ✅  
- Agents: 20+ ✅
- Simulations: 20+ ✅
- Core: 10+ ✅

**🔧 Database Schema**: Fully migrated and tested
**🚀 Production Ready**: All critical paths covered
**📊 Coverage**: High coverage of authentication and API layers 