# Blackjack Counter Tests

This directory contains the test suite for the Blackjack Counter application.

## Test Structure

```
tests/
├── unit/                      # Unit tests for individual modules
│   ├── test_game_state.py    # Tests for GameState class
│   ├── test_card_counter.py  # Tests for WongHalvesCounter class
│   ├── test_basic_strategy.py # Tests for BasicStrategy class
│   └── test_fixtures/        # Test YAML configuration files
├── integration/              # Integration tests
│   ├── test_game_flow.py    # Tests for complete game scenarios
│   └── test_config_loading.py # Tests for configuration file loading
└── conftest.py              # Shared pytest fixtures

```

## Running Tests

### Install dependencies
```bash
pip install -e ".[dev]"
```

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run specific test categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Specific test file
pytest tests/unit/test_game_state.py

# Specific test method
pytest tests/unit/test_game_state.py::TestGameState::test_initialization
```

### Run with verbose output
```bash
pytest -v
```

## Test Coverage

The test suite covers:

1. **GameState**: All methods for managing player/dealer hands
2. **WongHalvesCounter**: Card counting logic, true count calculations, betting suggestions
3. **BasicStrategy**: Decision making for all hand types (hard, soft, pairs)
4. **Integration**: Complete game flows, configuration loading, edge cases

## Writing New Tests

When adding new features:

1. Add unit tests for new classes/methods
2. Update integration tests if the feature affects game flow
3. Add test fixtures for any new configuration formats
4. Ensure all tests pass before committing

## Test Conventions

- Use descriptive test names that explain what is being tested
- Group related tests in classes
- Use pytest fixtures for common test data
- Mark tests appropriately (unit, integration, slow)
- Mock external dependencies (file I/O) in unit tests
- Test both happy paths and error cases