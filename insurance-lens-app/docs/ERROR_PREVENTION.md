# Error Prevention Strategy

## Post-Mortem: Schema Mismatch Errors (Oct 19, 2024)

### What Happened
We encountered 3 runtime errors that bypassed our type safety measures:
1. Missing required field `question_type` in `AnswerResponse`
2. Attempting to pass non-existent field `highlighted_clauses`
3. Wrong enum value `QuestionType.POLICY` (should be `POLICY_SPECIFIC`)

### Why Our Safety Measures Failed

#### Pydantic: Runtime-Only
- ✅ **What it catches**: Invalid data at runtime when models are instantiated
- ❌ **What it misses**: Missing fields in YOUR code before running
- 💡 **Lesson**: Pydantic is a safety net, not a development tool

#### mypy: Not Run
- ✅ **What it would catch**: Missing fields, wrong types, enum errors
- ❌ **Why it failed us**: We didn't run it during development
- 💡 **Lesson**: Tools only help if you use them!

#### IDE Warnings: Ignored
- ✅ **What it showed**: Probably highlighted the errors
- ❌ **Why we missed it**: Moving too fast, not paying attention
- 💡 **Lesson**: IDE warnings are there for a reason

---

## Prevention Strategy

### 1. **Pre-Commit Hooks** ⭐ HIGHEST PRIORITY

Install and configure pre-commit to run checks automatically:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
```

**What to check**:
- `mypy` for type checking
- `ruff` for linting
- `black` for formatting
- Custom script to validate Pydantic schema usage

### 2. **mypy Integration** ⭐ HIGH PRIORITY

#### Setup mypy configuration:

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Pydantic plugin
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

#### Run mypy regularly:
```bash
# Check specific files
mypy app/api/routes/policies.py

# Check entire project
mypy app/

# In CI/CD
mypy app/ --strict
```

### 3. **Schema-First Development Checklist** ⭐ MEDIUM PRIORITY

**BEFORE writing any code that uses a Pydantic model:**

- [ ] Open the schema file
- [ ] Read ALL field names and types
- [ ] Write them down or keep schema file open in split view
- [ ] Use IDE autocomplete (Ctrl+Space) to verify field names
- [ ] Test with minimal example IMMEDIATELY

**Example workflow:**
```python
# 1. Open and READ schema
from app.models.schemas import AnswerResponse

# 2. Check what fields it needs (use IDE autocomplete or read file)
# Required: answer, question_type, citations, web_sources, confidence

# 3. Create response with ALL fields
response = AnswerResponse(
    answer="...",
    question_type=QuestionType.POLICY_SPECIFIC,  # ← Check enum values!
    citations=[],
    web_sources=[],
    confidence=0.0
)

# 4. Test immediately
print(response.model_dump_json())
```

### 4. **Test-Driven Development (TDD)** ⭐ MEDIUM PRIORITY

Write tests BEFORE implementation:

```python
# tests/test_api_routes.py
def test_ask_question_response_schema():
    """Test that ask_question returns correct schema"""
    response = client.post(
        "/api/v1/api/policies/{policy_id}/ask",
        json={"question": "Test question"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all required fields
    assert "answer" in data
    assert "question_type" in data
    assert "citations" in data
    assert "web_sources" in data
    assert "confidence" in data
    
    # Verify types
    assert isinstance(data["answer"], str)
    assert data["question_type"] in ["policy_specific", "general_insurance"]
```

**Benefits**:
- Catches schema mismatches immediately
- Documents expected behavior
- Prevents regressions

### 5. **Schema Validation Utilities** ⭐ LOW PRIORITY (Nice to have)

Create helper functions to validate schema compatibility:

```python
# app/utils/schema_validator.py
from typing import Type, get_type_hints
from pydantic import BaseModel

def validate_model_instantiation(model_class: Type[BaseModel], data: dict) -> list[str]:
    """
    Check if data dict can instantiate model without actually instantiating it.
    Returns list of missing required fields.
    """
    required_fields = {
        name: field_info 
        for name, field_info in model_class.model_fields.items()
        if field_info.is_required()
    }
    
    missing = []
    for field_name in required_fields:
        if field_name not in data:
            missing.append(field_name)
    
    return missing

# Usage in route:
missing = validate_model_instantiation(AnswerResponse, {
    "answer": result.answer,
    "citations": result.citations,
    # ...
})
if missing:
    raise ValueError(f"Missing required fields: {missing}")
```

### 6. **CI/CD Pipeline** ⭐ HIGH PRIORITY (for production)

Automate all checks:

```yaml
# .github/workflows/test.yml
name: Test and Type Check

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
      
      - name: Run mypy
        run: uv run mypy app/ --strict
      
      - name: Run tests
        run: uv run pytest
      
      - name: Run linter
        run: uv run ruff check app/
```

### 7. **Development Workflow Changes**

#### Instead of:
1. Write all code
2. Test at the end
3. Fix errors

#### Do this:
1. **Read schema** ✅
2. Write **minimal** code
3. **Test immediately** ✅
4. Then expand

**Micro-iteration workflow:**
```python
# Step 1: Minimal version
def ask_question(policy_id: str, request: QuestionRequest):
    # Just return a dummy response to test schema
    return AnswerResponse(
        answer="test",
        question_type=QuestionType.POLICY_SPECIFIC,
        citations=[],
        web_sources=[],
        confidence=0.0
    )

# Step 2: Test it works
# $ curl ...

# Step 3: Now add real logic
def ask_question(policy_id: str, request: QuestionRequest):
    result = await policy_service.answer_question(policy_id, request)
    return AnswerResponse(
        answer=result.answer,
        question_type=QuestionType.POLICY_SPECIFIC,
        citations=result.citations,
        web_sources=[],
        confidence=result.confidence
    )
```

---

## Checklist for Future Features

When implementing new features:

- [ ] Run `mypy app/` before committing
- [ ] Check IDE for any yellow/red underlines
- [ ] Read schemas before using them
- [ ] Test each component immediately (unit test or manual test)
- [ ] Use autocomplete to verify field names
- [ ] Write test case first (TDD)

---

## Tools to Install

### Essential (Do Now)
```bash
# Type checking
pip install mypy

# Linting
pip install ruff

# Testing
pip install pytest pytest-asyncio

# Run checks
mypy app/
ruff check app/
pytest
```

### Recommended (Do Soon)
```bash
# Pre-commit hooks
pip install pre-commit

# Code formatting
pip install black

# Coverage reporting
pip install pytest-cov
```

### Optional (Do Later)
```bash
# API testing
pip install httpx pytest-httpx

# Property-based testing
pip install hypothesis

# Contract testing
pip install schemathesis
```

---

## Summary

### Why It Happened
1. Schema and implementation were separated in time
2. No automated validation between writing and testing
3. Didn't run type checker
4. Tested too late

### Key Takeaways
1. **mypy is useless if you don't run it** - Run it after every significant change
2. **Pydantic validates data, not code** - It catches runtime errors, not development errors
3. **IDE warnings matter** - Yellow squiggles are your friends
4. **Test immediately** - Don't write 100 lines before testing
5. **Read schemas first** - Always check the contract before implementing

### Action Items for This Project

**Do Today:**
- [ ] Run `mypy app/` and fix any issues
- [ ] Add mypy to development workflow
- [ ] Create simple test cases for existing endpoints

**Do This Week:**
- [ ] Set up pre-commit hooks
- [ ] Write tests for critical paths
- [ ] Document workflow in README

**Do Before Production:**
- [ ] Set up CI/CD pipeline
- [ ] Add comprehensive test suite
- [ ] Enable strict type checking

