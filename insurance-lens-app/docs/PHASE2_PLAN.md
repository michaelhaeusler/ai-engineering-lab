# Phase 2: LangGraph Multi-Agent System - Implementation Plan

## 🎯 Objective
Implement intelligent question routing using LangGraph to handle both policy-specific and general insurance questions.

## 📋 Requirements
1. ✅ Use LangGraph StateGraph for state management
2. ✅ Implement conditional routing (policy vs. general questions)
3. ✅ Integrate Tavily for web search
4. ✅ Add clause highlighting on upload
5. ✅ Keep implementation simple and maintainable

---

## 🏗️ Architecture

### LangGraph Flow
```
START
  ↓
CLASSIFIER NODE
(Question classification)
  ↓
CONDITIONAL EDGE
  ├→ POLICY NODE (RAG with existing AnswerGenerator)
  └→ WEB SEARCH NODE (Tavily API)
  ↓
END
```

### Agent State
```python
class AgentState(TypedDict):
    # Input
    question: str
    policy_id: Optional[str]
    
    # Routing
    question_type: Literal["policy", "general"]
    
    # Output
    answer: str
    citations: List[Citation]
    web_sources: List[str]
    confidence: float
    
    # Metadata
    route_taken: str
    processing_time: float
```

---

## 📝 Implementation Steps

### Step 1: Question Classifier Service (1 hour)
**File**: `backend/app/services/question_classifier.py`

**Features**:
- Heuristic checks (fast path)
  - No policy_id → general
  - Keywords like "meine Police", "in meinem Vertrag" → policy
- LLM classification (accurate fallback)
- Returns `QuestionType.POLICY_SPECIFIC` or `QuestionType.GENERAL_INSURANCE`

### Step 2: Web Search Agent (1.5 hours)
**File**: `backend/app/services/web_search_agent.py`

**Features**:
- Tavily API integration
- German-language search with insurance-specific domains
- Answer generation from search results
- Returns `AnswerResult` with web sources

### Step 3: LangGraph Orchestrator (1 hour)
**File**: `backend/app/services/agent_orchestrator.py`

**Features**:
- StateGraph setup with nodes and edges
- Classifier node (wraps QuestionClassifier)
- Policy node (wraps existing AnswerGenerator)
- Web search node (wraps WebSearchAgent)
- Conditional routing logic

### Step 4: Integrate into PolicyService (30 min)
**File**: `backend/app/services/policy_service.py`

**Changes**:
- Replace direct `AnswerGenerator` call with `AgentOrchestrator`
- Pass through LangGraph result
- Update logging

### Step 5: Clause Highlighting (1.5 hours)
**File**: `backend/app/services/clause_highlighter.py`

**Features**:
- Extract key clauses using LLM (structured output)
- Query norms database in Qdrant
- Compare policy clauses vs. norms
- Return highlighted differences

**Integration**:
- Call during `process_policy_upload` in `PolicyService`
- Populate `highlights` field in response

### Step 6: Configuration & Testing (30 min)
- Add Tavily config to `app/core/config.py`
- Update `app/services/__init__.py`
- Test both routing paths
- Create test script for web search

---

## 🔍 Classification Logic

### Heuristic Rules (Fast)
```python
# Policy-specific keywords (German)
POLICY_KEYWORDS = [
    "meine police", "mein vertrag", "in meinem vertrag",
    "meine versicherung", "mein tarif", "bei mir",
    "in der police", "laut vertrag"
]

# General question indicators
GENERAL_KEYWORDS = [
    "was ist", "was bedeutet", "wie funktioniert",
    "unterschied zwischen", "allgemein", "generell"
]
```

### LLM Classification (Accurate)
```
You are a question classifier for a German health insurance assistant.

Classify the question as either:
- "policy": Asks about a specific uploaded insurance policy
- "general": Asks for general insurance information

Question: {question}
Has uploaded policy: {has_policy}

Classification:
```

---

## 🌐 Tavily Search Configuration

```python
search_params = {
    "query": question,
    "search_depth": "advanced",
    "max_results": 5,
    "include_domains": [
        "gesundheit.de",
        "krankenkassen.de",
        "bundesgesundheitsministerium.de"
    ],
    "exclude_domains": [
        "facebook.com",
        "twitter.com"
    ]
}
```

---

## 🎨 Clause Highlighting Process

1. **Extract Clauses** (LLM with structured output)
```python
extraction_prompt = """
Extract key insurance clauses from this policy text:
{policy_text}

For each clause, provide:
- category: waiting_period | exclusion | coverage_limit | deductible
- title: Brief title
- text: Exact clause text
- value: Numerical value if applicable
"""
```

2. **Query Norms Database**
```python
# Search for relevant norms
norms = vector_store.search_norms(
    category="waiting_period",
    limit=1
)
```

3. **Compare & Highlight**
```python
# If clause differs significantly from norm
if policy_value < norm_value * 0.7:  # 30% better
    highlight = {
        "reason": "significantly_better",
        "comparison": f"Your {policy_value} vs. typical {norm_value}"
    }
```

---

## ✅ Success Criteria

- [ ] Questions route correctly (policy vs. general)
- [ ] Policy questions return answers with citations
- [ ] General questions return answers with web sources
- [ ] LangGraph state transitions work smoothly
- [ ] Clause highlighting returns 2-5 highlights per policy
- [ ] All tests pass
- [ ] Code follows best practices (Pydantic, type hints, etc.)

---

## 📊 Testing Strategy

### Unit Tests
- Question classifier with various inputs
- Web search agent with mock Tavily responses
- Clause highlighter with sample policies

### Integration Tests
- Full LangGraph flow for policy questions
- Full LangGraph flow for general questions
- Upload with clause highlighting

### Manual Tests
- Upload real PDF, ask policy question
- Ask general question without policy
- Verify highlights in UI

---

*Implementation Time Estimate: 4-5 hours*
*Current Status: Ready to start*

