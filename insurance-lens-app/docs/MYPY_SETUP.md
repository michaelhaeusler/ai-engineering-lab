# Automated mypy Type Checking Setup

This guide explains how mypy is set up to run automatically in the InsuranceLens project.

## 🎯 Goal

Ensure type checking runs automatically to catch errors early, without needing manual intervention for every check.

---

## 🔧 Setup Methods

### 1. **VS Code Integration** ⭐ RECOMMENDED

**What it does**: Shows mypy errors directly in your editor as you type.

**Setup**: Already configured in `.vscode/settings.json` (this file is local only, not in git)

**How it works**:
- Red squiggly lines appear under type errors as you type
- Hover over errors to see details
- Errors show in the "Problems" panel (Cmd+Shift+M on Mac)
- Auto-formats code on save with ruff

**Requirements**:
- VS Code with Python extension installed
- Ruff extension installed (`charliermarsh.ruff`)

**Check it's working**:
1. Open any Python file in `backend/app/`
2. Look at bottom status bar - should show "mypy"
3. Open "Problems" panel (Cmd+Shift+M on Mac)
4. Should see type errors listed there

**If not working**:
1. Check Python interpreter is set to `backend/.venv/bin/python`
2. Reload VS Code window (Cmd+Shift+P → "Reload Window")
3. Check extensions: Python and Ruff are installed

---

### 2. **Makefile Commands** ⭐ RECOMMENDED

**What it does**: Provides simple commands to run checks manually before committing.

**Setup**: Already configured in `backend/Makefile`

**Usage**:
```bash
cd backend/

# Run mypy only
make mypy

# Run all checks (mypy + ruff linting)
make check

# Format code + run checks + tests
make all
```

**When to use**:
- **Before committing code** (recommended workflow)
- After making significant changes
- Before pushing to remote

---

### 3. **Manual Command** (Alternative)

**What it does**: Run mypy directly via command line.

**Usage**:
```bash
cd backend/
uv run mypy app/
```

**When to use**:
- Quick manual check
- Debugging mypy configuration
- CI/CD scripts

---

## 📋 Recommended Workflow

### Daily Development:
1. **VS Code shows errors as you type** (real-time feedback)
2. Fix type errors as they appear
3. Save file → auto-format happens

### Before Committing:
```bash
cd backend/
make check  # Type check + lint
```

If any errors appear, fix them and run `make check` again.

### Before Pushing:
```bash
cd backend/
make all  # Format + type check + lint + test
```

---

## 🔍 Understanding mypy Output

### Example Error:
```
app/services/answer_generator.py:33: error: Function is missing a return type annotation  [no-untyped-def]
```

**Breaking it down**:
- `app/services/answer_generator.py:33` - File and line number
- `error:` - Severity level
- `Function is missing a return type annotation` - The issue
- `[no-untyped-def]` - Error code

### Common Error Codes:
- `[no-untyped-def]` - Missing return type annotation
- `[attr-defined]` - Accessing undefined attribute
- `[return-value]` - Wrong return type
- `[call-overload]` - Wrong function arguments
- `[type-arg]` - Missing generic type parameters (e.g., `Dict[str, Any]` not `dict`)

### How to Fix:
```python
# ❌ Before - missing type hints
def process_data(data):
    return data

# ✅ After - with type hints
def process_data(data: str) -> str:
    return data
```

---

## 🛠️ Configuration

### Location:
`backend/pyproject.toml` under `[tool.mypy]`

### Current Settings:
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
check_untyped_defs = true
plugins = ["pydantic.mypy"]  # Pydantic integration
```

### Strictness:
We start **lenient** and gradually tighten:
- `disallow_untyped_defs = false` - Currently OFF (allows functions without type hints)
- Plan: Enable this later once codebase is fully typed

### Ignoring Errors (use sparingly):
```python
# Ignore one line
result = some_function()  # type: ignore[return-value]

# Ignore entire file (add at top)
# mypy: ignore-errors
```

⚠️ **Only use `type: ignore` when absolutely necessary!**

---

## 📊 Integration Status

| Method | Status | Auto-runs | Setup Required |
|--------|--------|-----------|----------------|
| VS Code | ✅ Configured | On file save | Install extensions |
| Makefile | ✅ Configured | Manual | None |
| CI/CD | ⏳ Future | On PR/push | GitHub Actions |

---

## 🚀 Quick Start

**First time setup**:
```bash
cd backend/

# Install dependencies
uv sync

# Verify mypy works
make mypy
```

**From now on**:
- Code normally in VS Code
- Check "Problems" panel for real-time feedback
- Run `make check` before committing

---

## 🐛 Troubleshooting

### "mypy not running in VS Code"
1. Check Python interpreter is set to `backend/.venv/bin/python`
2. Reload VS Code window (Cmd+Shift+P → "Reload Window")
3. Check "Python" output channel for errors
4. Verify extensions are installed: Python, Ruff

### "Too many mypy errors!"
Start by fixing:
1. Missing return type annotations (`-> ReturnType`)
2. Missing type hints for function parameters
3. Generic type parameters (`Dict[str, Any]` not `dict`)

Then run `make mypy` to see progress.

### "make mypy" shows errors but VS Code doesn't
VS Code might be using a different Python interpreter or mypy version. Check:
```bash
# In terminal
cd backend/
which python  # Should be .venv/bin/python
uv run mypy --version

# In VS Code
# Check bottom-left status bar for Python version
```

---

## 📚 Learning Resources

- **mypy Docs**: https://mypy.readthedocs.io/
- **Type Hints Cheat Sheet**: https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
- **Pydantic + mypy**: https://docs.pydantic.dev/latest/integrations/mypy/

---

## ✅ Checklist

- [ ] Verify VS Code shows type errors in "Problems" panel
- [ ] Run `make mypy` to see current issues
- [ ] Add to daily workflow: Check "Problems" panel regularly
- [ ] Run `make check` before committing
- [ ] Run `make all` before pushing

---

## 💡 Why Not Pre-commit Hooks?

**Question**: Why don't we use pre-commit hooks that run automatically on `git commit`?

**Answer**: This is a **multi-folder learning repository** with code from different course lessons. Using pre-commit hooks would:
- Apply checks to the entire repository (including course materials)
- Require maintaining compatibility across unrelated projects
- Slow down commits for work on other folders

**Our approach**:
- **Manual checks via Makefile** before committing (`make check`)
- **VS Code integration** for real-time feedback
- Focused only on your certification challenge project

This gives you the benefits of automated checking without the complexity of managing hooks across multiple independent projects.
