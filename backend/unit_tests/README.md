# Unit Tests for CrewAI Agent Builder Platform Backend

This directory contains comprehensive unit tests for all API endpoints in the CrewAI Agent Builder Platform backend.

## Database Testing Options

We provide two database testing configurations:

### Option 1: SQLite (Default - Fast & Simple)
- ✅ **Fast**: In-memory database, tests run in milliseconds
- ✅ **No Dependencies**: Works anywhere without setup
- ✅ **Isolated**: Each test gets fresh database
- ✅ **CI/CD Friendly**: Perfect for GitHub Actions, Docker
- ❌ **Different from Production**: SQLite vs PostgreSQL differences

### Option 2: PostgreSQL (Production-like)
- ✅ **Production Accurate**: Same database as production
- ✅ **Full Feature Testing**: All PostgreSQL features available
- ✅ **Real Constraints**: Actual foreign keys, types, etc.
- ❌ **Slower**: Database creation/teardown overhead
- ❌ **Requires Setup**: Need PostgreSQL server running

## Quick Start

### SQLite Testing (Default)
```bash
# Install dependencies
pip install pytest httpx

# Run all tests
python -m pytest unit_tests/ -v
```

### PostgreSQL Testing
```bash
# Option A: Use Docker (Recommended)
python unit_tests/test_with_postgres.py full

# Option B: Use existing PostgreSQL
# 1. Ensure PostgreSQL is running
# 2. Set environment variables
export POSTGRES_USER=your_user
export POSTGRES_PASSWORD=your_password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

# 3. Run tests
python unit_tests/test_with_postgres.py setup
python -m pytest unit_tests/ -v
python unit_tests/test_with_postgres.py restore
```

## Test Structure

The tests are organized into separate files by functionality:

- `conftest.py` - SQLite test configuration (default)
- `conftest_postgres.py` - PostgreSQL test configuration
- `test_root.py` - Tests for the root endpoint (/)
- `test_health.py` - Tests for the health check endpoint (/health/)
- `test_scenarios.py` - Tests for scenario management endpoints
- `test_agents.py` - Tests for agent management endpoints (CRUD operations)
- `test_simulations.py` - Tests for simulation management endpoints
- `test_with_postgres.py` - Helper script for PostgreSQL testing
- `docker-compose.test.yml` - Docker PostgreSQL for testing

## Test Coverage

### Root & Health Endpoints
- `GET /` - Root endpoint
- `GET /health/` - Health check endpoint

### Scenario Management
- `POST /scenarios/` - Create scenario
- `GET /scenarios/` - List all scenarios
- `GET /scenarios/{scenario_id}` - Get specific scenario

### Agent Management
- `POST /agents/` - Create agent
- `GET /agents/` - List all agents
- `GET /agents/{agent_id}` - Get specific agent
- `PUT /agents/{agent_id}` - Update agent
- `DELETE /agents/{agent_id}` - Delete agent
- `GET /agents/user/{user_id}` - Get user's agents

### Simulation Management
- `POST /simulations/` - Start simulation
- `POST /simulations/{simulation_id}/chat/` - Chat with crew
- `GET /simulations/{simulation_id}/history/` - Get simulation history
- `POST /simulations/{simulation_id}/complete/` - Complete simulation

## Running Tests

### SQLite Tests (Default)

```bash
# Run all tests
python -m pytest unit_tests/ -v

# Run specific test files
python -m pytest unit_tests/test_scenarios.py -v
python -m pytest unit_tests/test_agents.py -v
python -m pytest unit_tests/test_simulations.py -v

# With coverage report
python -m pytest unit_tests/ --cov=. --cov-report=html
```

### PostgreSQL Tests

#### Using Docker (Recommended)
```bash
# Complete workflow: start DB + run tests + cleanup
python unit_tests/test_with_postgres.py full

# Step by step
python unit_tests/test_with_postgres.py start-db    # Start PostgreSQL container
python unit_tests/test_with_postgres.py setup      # Switch to PostgreSQL config
python -m pytest unit_tests/ -v                   # Run tests
python unit_tests/test_with_postgres.py restore    # Restore SQLite config
python unit_tests/test_with_postgres.py stop-db    # Stop container
```

#### Using Existing PostgreSQL
```bash
# Set environment variables
export POSTGRES_USER=your_user
export POSTGRES_PASSWORD=your_password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

# Switch to PostgreSQL testing
python unit_tests/test_with_postgres.py setup

# Run tests
python -m pytest unit_tests/ -v

# Restore SQLite testing
python unit_tests/test_with_postgres.py restore
```

### Run Specific Test Classes or Methods

```bash
# Run specific test class
python -m pytest unit_tests/test_agents.py::TestAgentEndpoints -v

# Run specific test method
python -m pytest unit_tests/test_agents.py::TestAgentEndpoints::test_create_agent_success -v
```

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
python -m pytest unit_tests/ -n auto
```

## When to Use Which Database

### Use SQLite When:
- ⚡ **Fast feedback** during development
- 🚀 **CI/CD pipelines** (GitHub Actions, etc.)
- 🏃‍♂️ **Quick local testing**
- 📦 **No external dependencies** needed
- 🧪 **Unit testing** focused on business logic

### Use PostgreSQL When:
- 🎯 **Integration testing** with exact production behavior
- 🔧 **Testing PostgreSQL-specific features** (JSON operators, arrays, etc.)
- 🐛 **Debugging database-related issues**
- ✅ **Pre-deployment testing** to catch DB-specific bugs
- 📊 **Performance testing** with realistic database behavior

## Test Features

### Fixtures
- `test_db` - Fresh database for each test
- `client` - FastAPI test client
- `db_session` - Database session for direct DB operations
- `sample_user` - Test user for user-related tests
- `sample_scenario` - Test scenario for scenario-related tests
- `sample_agent` - Test agent for agent-related tests
- `sample_simulation` - Test simulation for simulation-related tests
- `valid_*_data` - Valid data fixtures for POST requests

### Test Categories
- **Success Cases** - Valid inputs and expected successful responses
- **Error Cases** - Invalid inputs and expected error responses
- **Edge Cases** - Boundary conditions and unusual scenarios
- **Integration Tests** - End-to-end workflow testing
- **Data Validation** - Type checking and format validation

## Environment Variables

### SQLite (Default)
No environment variables needed.

### PostgreSQL
```bash
POSTGRES_HOST=localhost      # PostgreSQL host
POSTGRES_PORT=5432          # PostgreSQL port
POSTGRES_USER=postgres      # PostgreSQL username
POSTGRES_PASSWORD=password  # PostgreSQL password
```

## Test Examples

### Creating a New Test

```python
def test_new_endpoint(self, client, sample_user):
    """Test description"""
    # Arrange
    test_data = {"field": "value"}
    
    # Act
    response = client.post("/new-endpoint/", json=test_data)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["field"] == test_data["field"]
```

### Testing Error Cases

```python
def test_endpoint_not_found(self, client):
    """Test endpoint with non-existent resource"""
    response = client.get("/endpoint/999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Resource not found"
```

## Continuous Integration

### GitHub Actions Example
```yaml
# SQLite (fast)
- name: Run SQLite Tests
  run: python -m pytest unit_tests/ -v

# PostgreSQL (comprehensive) 
- name: Run PostgreSQL Tests  
  run: python unit_tests/test_with_postgres.py full
```

## Adding New Tests

When adding new endpoints or modifying existing ones:

1. Create tests in the appropriate test file
2. Add fixtures to `conftest.py` if needed
3. Test both success and error cases
4. Include edge cases and boundary conditions
5. Verify data types and structure
6. Test integration workflows where applicable
7. Consider testing with both SQLite and PostgreSQL for critical features

## Best Practices

1. **Arrange-Act-Assert** pattern
2. **Descriptive test names** that explain what's being tested
3. **Test one thing at a time** - focused, atomic tests
4. **Use fixtures** for common setup
5. **Test error cases** not just success cases
6. **Verify response structure** and data types
7. **Test edge cases** and boundary conditions
8. **Choose appropriate database** for test type

## Troubleshooting

### Common Issues

1. **Import errors** - Ensure all dependencies are installed
2. **Database errors** - Check if PostgreSQL is running (for PostgreSQL tests)
3. **Test isolation** - Each test gets a fresh database
4. **Path issues** - Run tests from the backend directory
5. **Port conflicts** - PostgreSQL Docker uses port 5433 to avoid conflicts

### Debug Mode

```bash
# Run with debugging
python -m pytest unit_tests/ -v -s --tb=short

# Run with pdb on failure
python -m pytest unit_tests/ --pdb

# PostgreSQL connection test
python unit_tests/test_with_postgres.py start-db
python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5433, user='test_user', password='test_password', database='postgres')
print('✅ PostgreSQL connection successful')
conn.close()
"
```

## Test Reports

Generate HTML coverage reports:

```bash
python -m pytest unit_tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in your browser
```

Generate JUnit XML reports for CI:

```bash
python -m pytest unit_tests/ --junitxml=test-results.xml
```

## Performance Comparison

| Aspect | SQLite | PostgreSQL |
|--------|--------|------------|
| **Test Speed** | ~2-5 seconds | ~30-60 seconds |
| **Setup Time** | Instant | ~10 seconds |
| **Memory Usage** | Low | Medium |
| **Dependencies** | None | PostgreSQL server |
| **CI/CD** | Perfect | Good with Docker |
| **Production Accuracy** | ~85% | 100% |

## Recommendation

- **Daily Development**: Use SQLite for fast feedback
- **Pre-merge/PR**: Run both SQLite and PostgreSQL tests
- **CI/CD**: SQLite for speed, PostgreSQL for critical paths
- **Debugging DB Issues**: Always use PostgreSQL 