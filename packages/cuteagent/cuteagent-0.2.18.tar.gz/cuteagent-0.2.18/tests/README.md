# 🧪 CuteAgent Test Suite

This directory contains the comprehensive test suite for CuteAgent, organized by test type and purpose.

## 📁 Directory Structure

```
tests/
├── README.md                    # This file
├── __init__.py                  # Test package initialization
├── test_cuteagent.py           # Legacy basic tests
├── run_tests.py                # Test runner script
│
├── mock/                       # Mock tests (no API required)
│   └── test_station_agent_mock.py
│
├── real_api/                   # Real API tests
│   └── test_station_agent_real.py
│
├── integration/                # Integration tests
│   ├── test_station_agent.py
│   ├── test_sync_functionality.py
│   └── test_server_status.py
│
└── examples/                   # Test examples and demos
    ├── sync_pattern_example.py
    ├── langgraph_integration_example.py
    └── usage_example.py
```

## 🧪 Test Categories

### 1. **Mock Tests** (`mock/`)
- **Purpose**: Test StationAgent logic without real API calls
- **Requirements**: No external dependencies
- **Speed**: Fast (< 5 seconds)
- **Coverage**: 100% pass rate expected

```bash
# Run mock tests only
python tests/run_tests.py mock
```

### 2. **Real API Tests** (`real_api/`)
- **Purpose**: Test against actual SharedState API
- **Requirements**: Valid API token and network access
- **Speed**: Moderate (10-30 seconds)  
- **Coverage**: End-to-end validation

```bash
# Run real API tests
python tests/run_tests.py real dev-token-123
```

### 3. **Integration Tests** (`integration/`)
- **Purpose**: Test component interactions and workflows
- **Requirements**: Varies by test
- **Coverage**: Cross-component functionality

### 4. **Examples** (`examples/`)
- **Purpose**: Demonstration code and usage patterns
- **Requirements**: May need API access
- **Usage**: Reference implementations

## 🚀 Running Tests

### Quick Start

```bash
# From project root
cd cuteagent

# Run all mock tests (fast, no API needed)
python tests/run_tests.py mock

# Run real API tests (requires token)
python tests/run_tests.py real dev-token-123

# Run both mock and real tests
python tests/run_tests.py all dev-token-123
```

### Individual Test Files

```bash
# Run specific test files directly
python tests/mock/test_station_agent_mock.py
python tests/real_api/test_station_agent_real.py
python tests/integration/test_sync_functionality.py

# Run examples
python tests/examples/usage_example.py
```

## 📊 Test Coverage

### StationAgent Features Tested

- ✅ **Initialization**: Automatic state loading
- ✅ **State Management**: get, set, push, pull, sync operations  
- ✅ **Server Coordination**: load, unload, availability
- ✅ **Reserved Variables**: Protection and validation
- ✅ **Error Handling**: Network retries, authentication
- ✅ **LangGraph Integration**: State sync patterns
- ✅ **Complex Data**: Nested objects, arrays, floats

### Test Statistics (Last Run)

```
Mock Tests:     25/25 passed (100.0%)
Real API Tests: 27/27 passed (100.0%)
Integration:    Various (see individual files)
```

## 🛠️ Writing New Tests

### Test File Naming

- **Mock tests**: `test_*_mock.py` in `mock/`
- **Real API tests**: `test_*_real.py` in `real_api/`
- **Integration tests**: `test_*.py` in `integration/`
- **Examples**: `*_example.py` in `examples/`

### Test Structure Template

```python
#!/usr/bin/env python3
"""
Test description

This test validates [what it tests] for [component/feature].
"""

import unittest
from unittest.mock import patch, Mock
from cuteagent import StationAgent

class TestYourFeature(unittest.TestCase):
    """Test suite for your feature."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Your setup code
        
    def test_specific_functionality(self):
        """Test specific functionality."""
        # Arrange
        # Act  
        # Assert
        
if __name__ == "__main__":
    unittest.main()
```

### Mock Test Guidelines

- Use `unittest.mock` for external dependencies
- Mock API calls with appropriate responses
- Test edge cases and error conditions
- Focus on logic validation, not API behavior

### Real API Test Guidelines

- Use actual API endpoints with test data
- Clean up test data after each test
- Handle network issues gracefully
- Validate end-to-end functionality

## 🔧 Configuration

### Environment Variables

```bash
# Required for real API tests
export SHARED_STATE_TOKEN="your-api-token"
export SHARED_STATE_URL="https://your-api.amazonaws.com/prod"

# Optional for specific tests
export HITL_TOKEN="your-hitl-token" 
export OPENAI_API_KEY="your-openai-key"
```

### Test Data Management

- **Mock tests**: Use predefined test data
- **Real API tests**: Generate unique identifiers per test run
- **Cleanup**: Always clean up test data in `tearDown()` or `cleanup()`

## 📈 Continuous Integration

Tests are automatically run in CI/CD pipeline:

1. **Pre-commit**: Mock tests run on every commit
2. **Pull Request**: Full test suite runs on PR creation
3. **Release**: Comprehensive validation before deployment

### GitHub Actions

```yaml
# .github/workflows/test.yml
- name: Run Mock Tests
  run: python tests/run_tests.py mock

- name: Run Real API Tests  
  run: python tests/run_tests.py real ${{ secrets.SHARED_STATE_TOKEN }}
```

## 🐛 Debugging Failed Tests

### Common Issues

1. **API Token**: Ensure `SHARED_STATE_TOKEN` is valid
2. **Network**: Check connectivity to API endpoints
3. **Dependencies**: Install requirements with `pip install -r requirements.txt`
4. **Python Path**: Run from project root directory

### Debug Mode

```bash
# Run with verbose output
python tests/run_tests.py mock --verbose

# Run single test with debugging
python -m pytest tests/mock/test_station_agent_mock.py::TestStationAgentMock::test_initialization -v
```

### Test Results

Test results are saved automatically:
- **Location**: `tests/results/`
- **Format**: JSON with detailed test info
- **Retention**: Results from last 5 runs kept

## 📚 Resources

- **CuteAgent Documentation**: [../README.md](../README.md)
- **API Reference**: [../docs/api_reference.md](../docs/api_reference.md)
- **LangGraph Integration**: [../docs/langgraph_integration.md](../docs/langgraph_integration.md)
- **Testing Best Practices**: Follow project cursor rules in `.cursorrules`

---

**Happy Testing! 🧪** 

For questions or issues with tests, check the individual test files or refer to the main documentation. 