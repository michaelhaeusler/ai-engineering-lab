# Automation Summary: Type Checking & Code Quality

This document summarizes all automated checks in the InsuranceLens project.

## 🎯 What Runs Automatically?

### 1. VS Code Integration (Real-time)

**Triggers**: As you type and save files

**What runs**:
- ✅ `mypy` - Shows type errors inline
- ✅ `ruff` - Shows linting errors
- ✅ Auto-formatting on save

**Status**: ✅ Configured in `.vscode/settings.json`

**How to check**:
1. Open any `.py` file
2. Look at "Problems" panel (Cmd+Shift+M)
3. Should see mypy/ruff errors listed

**Result**: Red squiggly lines under errors, auto-fix on save

---

### 2. Makefile Commands (On Demand)

**Triggers**: When you manually run `make` commands

**Available commands**:
```bash
make mypy        # Type check only
make lint        # Lint only
make format      # Format code
make check       # Type check + lint
make test        # Run tests
make all         # Format + check + test
```

**Status**: ✅ Configured in `backend/Makefile`

**Result**: Detailed error reports in terminal

---

## 📊 Comparison Table

| Method | When | Speed | Detail Level | Auto-runs? |
|--------|------|-------|--------------|------------|
| **VS Code** | Real-time | Fast | Medium | ✅ Yes |
| **Makefile** | Manual | Medium | Highest | ❌ No |
| **Manual mypy** | Manual | Medium | Highest | ❌ No |

---

## 🔄 Recommended Workflow

### While Coding:
1. **VS Code shows errors** → Fix them as you go
2. Save file → **Auto-format** happens

### Before Committing:
1. Review "Problems" panel in VS Code
2. **Run checks** → `make check` (type check + lint)
3. Fix any errors that appear
4. `git add` and `git commit`

### Before Pushing:
```bash
cd backend/
make all  # Full check: format + type check + lint + test
git push
```

---

## 🛠️ What Each Tool Checks

### mypy (Type Checking)
- ✅ Function return types
- ✅ Variable types
- ✅ Function argument types
- ✅ Pydantic model usage
- ✅ Generic type parameters (`Dict[str, Any]`)
- ✅ Optional vs non-optional types

**Example errors caught**:
```python
# Missing return type
def process_data(data):  # ❌ mypy error
    return data

# Wrong type
user: User = "not a user"  # ❌ mypy error

# Missing field
response = AnswerResponse(answer="test")  # ❌ missing required fields
```

### ruff (Linting)
- ✅ Unused imports
- ✅ Undefined variables
- ✅ Code style issues
- ✅ Potential bugs (e.g., mutable default arguments)
- ✅ Import sorting

**Example errors caught**:
```python
import os  # ❌ unused import

def func(x=[]):  # ❌ mutable default argument
    pass

if x = 5:  # ❌ assignment instead of comparison
    pass
```

### bandit (Security)
- ✅ Hardcoded secrets
- ✅ SQL injection risks
- ✅ Insecure cryptography
- ✅ Dangerous function calls

**Example errors caught**:
```python
password = "hardcoded123"  # ❌ hardcoded password
eval(user_input)  # ❌ dangerous eval
```

---

## 🚫 What to Do When Checks Fail

### VS Code Shows Many Errors

1. Focus on **mypy errors** first (type issues)
2. Then fix **ruff errors** (style/linting)
3. Run `make format` to auto-fix many issues
4. Check "Problems" panel again

### Make Check Fails

```bash
# See detailed errors
make mypy

# Fix issues in the files mentioned
# Run again to verify
make mypy
```

---

## 📈 Gradually Increasing Strictness

We start with **lenient** settings and gradually tighten:

**Phase 1 (Current)**: Basic type checking
- Allow functions without type hints
- Warn about type issues
- Focus on critical errors

**Phase 2 (Soon)**: Stricter checking
- Require return type annotations
- Require parameter type annotations
- Disallow `Any` types

**Phase 3 (Production)**: Full strict mode
- All functions must have complete type hints
- No escape hatches (`type: ignore` must be justified)
- Maximum type safety

**Configuration**: See `backend/pyproject.toml` → `[tool.mypy]`

---

## 🎓 Learning from Errors

### Good Error Messages

mypy provides helpful errors:
```
app/services/answer_generator.py:33: error: Function is missing a return type annotation  [no-untyped-def]
```

**How to read**:
- `app/services/answer_generator.py:33` - Where
- `error:` - Severity
- `Function is missing a return type annotation` - What's wrong
- `[no-untyped-def]` - Error code

**How to fix**:
```python
# Before
def process_data(data):
    return data

# After
def process_data(data: str) -> str:
    return data
```

---

## 🔧 Troubleshooting

### "pre-commit not running"
```bash
cd backend/
uv run pre-commit install
```

### "VS Code not showing errors"
1. Check Python interpreter: `backend/.venv/bin/python`
2. Reload window: Cmd+Shift+P → "Reload Window"
3. Check extensions: Python and Ruff installed

### "Too many errors"
Start small:
```bash
# Check one file
uv run mypy app/services/answer_generator.py

# Fix errors in that file
# Then move to next file
```

### "`make check` fails"
1. Read the error messages carefully
2. Fix the issues shown
3. Run `make check` again to verify
4. Once passing, commit your changes

---

## ✅ Verification Checklist

- [ ] VS Code shows type errors in "Problems" panel
- [ ] Makefile commands work: `make mypy`, `make check`
- [ ] Understand error messages
- [ ] Run `make check` before every commit

---

## 📚 Additional Resources

- [MYPY_SETUP.md](./MYPY_SETUP.md) - Detailed mypy setup guide
- [ERROR_PREVENTION.md](./ERROR_PREVENTION.md) - How we prevent schema mismatches
- [python-rule.mdc](../.cursor/rules/python-rule.mdc) - Python best practices
- [general-rule.mdc](../.cursor/rules/general-rule.mdc) - General development rules

