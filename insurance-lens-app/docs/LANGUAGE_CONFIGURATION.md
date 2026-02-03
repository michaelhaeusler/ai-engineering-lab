# Language Configuration Guide

## Overview
InsuranceLens is designed to be **language-agnostic**. The backend contains no hardcoded language-specific strings, making it easy to switch to any language.

---

## How to Change the Output Language

### **Method 1: Environment Variable (Recommended)**

Add to your `.env` file:

```bash
# Output language for LLM responses
LLM_OUTPUT_LANGUAGE=German  # or English, French, Spanish, etc.
```

### **Method 2: Default Configuration**

Edit `backend/app/core/config.py`:

```python
llm_output_language: str = Field(default="English", env="LLM_OUTPUT_LANGUAGE")
```

---

## Supported Languages

The system works with **any language** the LLM supports. Common options:

- `English`
- `German`
- `French`
- `Spanish`
- `Italian`
- `Portuguese`
- `Dutch`
- etc.

---

## How It Works

### **1. Conditional Language Instruction**

The system automatically adds language instructions to prompts **only when needed**:

```python
# If LLM_OUTPUT_LANGUAGE is set to "German"
language_instruction = "1. Always respond in German\n"

# If LLM_OUTPUT_LANGUAGE is "English" or not set
language_instruction = ""  # No instruction needed
```

### **2. Dynamic Prompt Generation**

All services (`AnswerGenerator`, `WebSearchAgent`) dynamically build prompts:

- **German Output** (LLM_OUTPUT_LANGUAGE=German):
  ```
  IMPORTANT RULES:
  1. Always respond in German
  2. Be precise and helpful
  3. Explain complex terms clearly
  ...
  ```

- **English Output** (LLM_OUTPUT_LANGUAGE=English or empty):
  ```
  IMPORTANT RULES:
  1. Be precise and helpful
  2. Explain complex terms clearly
  ...
  ```

### **3. Centralized Configuration**

All LLM settings are centralized in `app/core/config.py`:

```python
class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.3, env="LLM_TEMPERATURE")
    llm_output_language: str = Field(default="German", env="LLM_OUTPUT_LANGUAGE")
```

---

## Architecture Benefits

### ✅ **No Backend Code Changes**
Switch languages by changing **one environment variable** - no code modifications needed.

### ✅ **No Hardcoded Strings**
Backend contains zero language-specific strings (except in prompts, which are configurable).

### ✅ **Multi-Language Support**
Easily support multiple languages simultaneously by creating different configurations.

### ✅ **Frontend Independence**
Frontend can be in a different language than LLM responses.

---

## Example: Switching from German to English

### **Step 1: Update .env**
```bash
# Before
LLM_OUTPUT_LANGUAGE=German

# After
LLM_OUTPUT_LANGUAGE=English
```

### **Step 2: Restart Backend**
```bash
cd backend
uv run uvicorn app.main:app --reload
```

### **Step 3: Test**
All LLM responses will now be in English! 🎉

---

## Frontend Localization (Optional)

The frontend UI text is separate from LLM responses:

1. **LLM Responses**: Controlled by `LLM_OUTPUT_LANGUAGE` (backend)
2. **UI Text**: Controlled by frontend i18n library (e.g., react-i18next)

This allows combinations like:
- German UI + English LLM responses
- English UI + German LLM responses
- Spanish UI + Spanish LLM responses

---

## Best Practices

1. **Always use environment variables** for configuration
2. **Never hardcode language-specific strings** in backend code
3. **Test with different languages** to ensure prompts work correctly
4. **Document language requirements** in project README
5. **Keep prompts language-agnostic** except for the output instruction

---

## Related Files

- `backend/app/core/config.py` - Configuration settings
- `backend/app/services/answer_generator.py` - Policy-specific answers
- `backend/app/services/web_search_agent.py` - Web search answers
- `backend/app/services/question_classifier.py` - Question classification
- `backend/.env` - Environment variables (not in git)

---

## Migration from Hardcoded Language

If you find hardcoded language-specific strings:

1. ❌ **BAD**: `return "Entschuldigung, keine Ergebnisse"`
2. ✅ **GOOD**: Return error codes, let frontend handle wording
3. ✅ **GOOD**: Use `settings.llm_output_language` in prompts

See `.cursor/rules/general-rule.mdc` for full i18n guidelines.

