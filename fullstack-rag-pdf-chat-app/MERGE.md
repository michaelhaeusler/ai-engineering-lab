# 📦 RAG App Fixes and Deployment Stability - Merge Instructions

## 🚀 Overview

This branch `feature/rag-app` stabilizes the RAG app for Vercel deployments and previews.

Highlights:
- ✅ Route Python backend under `/backend/*` so Next.js can stream via `/api/*`
- ✅ Use absolute origin in prod for proxying (fixes Invalid URL errors)
- ✅ Add missing backend deps: `python-dotenv`, `numpy`
- ✅ Add server-side PDF size limit with a 413 response
- ✅ Single source of truth for max PDF size via env (`MAX_PDF_MB` / `NEXT_PUBLIC_MAX_PDF_MB`)
- ✅ UI hint shows max size; client and server validations are in sync

## 🔧 Files Touched

 - `vercel.json`: rewrite `/backend/(.*)` → Python backend; set `MAX_PDF_MB` envs
 - `api/app.py`: backend aliases under `/backend/*`, server-side size check using env
 - `api/requirements.txt`: add `python-dotenv`, `numpy`
 - `frontend/src/app/api/*/route.ts`: proxies use absolute origin in prod and `/backend/*`
 - `frontend/src/hooks/useFileUpload.ts`: client-side size check reads from `MAX_PDF_MB`
 - `frontend/src/components/FileUploadArea.tsx`: shows max size hint
 - `frontend/src/config/constants.ts`: exports `MAX_PDF_MB` from `NEXT_PUBLIC_MAX_PDF_MB`

## 🧪 Testing Checklist (Preview & Production)

- [ ] Upload < MAX_PDF_MB PDF → processes, embeddings created, summary streams in chat
- [ ] Upload > MAX_PDF_MB PDF → client blocks OR server returns 413 with clear message
- [ ] Clear document → returns app to normal chat
- [ ] No real OpenAI calls in E2E (tests mock APIs)
- [ ] Preview deploy works (same-origin `/backend/*` routing)

## 🔀 Merge Strategy

When you’re ready to ship, open a PR from `feature/rag-app` → `main`, validate the preview, then merge.

## 🔄 How to Merge

### Option 1: GitHub Pull Request (Recommended)

```bash
# Create a Pull Request on GitHub:
# 1. Go to your repository on GitHub
# 2. Click "Compare & pull request"
# 3. Base: main ← Compare: feature/rag-app
# 4. Title: "Stabilize RAG app for Vercel: backend routing, deps, size limit"
# 5. Paste the Overview + Files Touched sections
# 6. Ensure preview deploy passes manual checks, then merge
```

### Option 2: GitHub CLI

```bash
# Create and merge pull request using GitHub CLI
gh pr create \
  --base main \
  --head feature/rag-app \
  --title "Stabilize RAG app for Vercel: backend routing, deps, size limit" \
  --body "Routes backend under /backend, fixes prod proxy, adds deps, unified MAX_PDF_MB, server-side 413."
gh pr merge --merge  # or --squash or --rebase based on your preference
```

### Option 3: Direct Merge (Use with caution)

```bash
# Switch to main branch
git checkout main

# Merge the feature branch
git merge feature/rag-app

# Push to main
git push origin main

# Clean up feature branch (optional)
git branch -d feature/rag-app
```

## 🎉 User Experience Improvements

### Before
- ❌ `/api/*` routed to Python → broke streaming in prod
- ❌ Relative backend URLs in prod → Invalid URL errors
- ❌ Missing deps caused 500s on Vercel
- ❌ Size limits duplicated and inconsistent

### After
- ✅ Next.js streams via `/api/*`; Python served under `/backend/*`
- ✅ Absolute origin used in prod proxies
- ✅ Deps declared in `api/requirements.txt`
- ✅ One env-driven `MAX_PDF_MB` reflected in UI, client, and server

## 🔧 Technical Details

### Architecture
- **Frontend**: Next.js with TypeScript, streaming responses
- **Backend**: FastAPI with async processing
- **AI Integration**: OpenAI APIs
- **Vector Storage**: In-memory numpy-based vector database

### Performance
- **Streaming**: Real-time summary generation and display via Next proxy
- **Progress Tracking**: Visual feedback during long operations
- **Efficient Processing**: Optimized chunk sampling for summary generation

---

## 🎯 Ready to Merge!

This update makes the app robust on Vercel (including previews), preserves streaming via Next.js, and centralizes configuration so changes are low-friction.
