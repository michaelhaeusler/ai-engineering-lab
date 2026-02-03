# Publishing this repo to GitHub

Follow these steps to put the AI Engineering Lab on your GitHub account.

---

## 1. Prerequisites

- **Git** installed ([git-scm.com](https://git-scm.com)).
- **GitHub account** and (optional) **GitHub CLI** (`gh`) for easier repo creation.

---

## 2. Initialize Git and make the first commit

In a terminal, go to the repo root (the folder that contains this file and the `README.md`):

```bash
cd /Users/Micha/Workspace/private/ai-engineering-lab
```

Initialize the repository:

```bash
git init
```

Stage all files (the root `.gitignore` will exclude `.env`, `.venv`, `node_modules`, `cache`, etc.):

```bash
git add .
```

Check what will be committed (optional but recommended):

```bash
git status
```

Create the first commit:

```bash
git commit -m "Initial commit: AI Engineering Lab portfolio and course work"
```

---

## 3. Create the repository on GitHub

**Option A – Using the GitHub website**

1. Open [github.com/new](https://github.com/new).
2. Set **Repository name** (e.g. `ai-engineering-lab`).
3. Choose **Public**.
4. Do **not** add a README, .gitignore, or license (you already have them locally).
5. Click **Create repository**.

**Option B – Using GitHub CLI**

If you have `gh` installed and logged in (`gh auth login`):

```bash
gh repo create ai-engineering-lab --public --source=. --remote=origin --push
```

That creates the repo, adds `origin`, and pushes. If you use this, you can skip steps 4 and 5 below.

---

## 4. Add GitHub as the remote and push

Replace `YOUR_USERNAME` with your GitHub username. If you already used `gh repo create ... --push`, skip this step.

Add the remote:

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-engineering-lab.git
```

Rename the branch to `main` (if GitHub expects `main`):

```bash
git branch -M main
```

Push the first commit:

```bash
git push -u origin main
```

If GitHub prompts for login, use a **Personal Access Token** (Settings → Developer settings → Personal access tokens) as the password, or set up SSH and use the SSH URL: `git@github.com:YOUR_USERNAME/ai-engineering-lab.git`.

---

## 5. Verify

- Open `https://github.com/YOUR_USERNAME/ai-engineering-lab` in your browser.
- Confirm the README, folders, and files look correct.
- Check that no `.env` or `.venv` contents were committed (they should be ignored).

---

## Later: making changes and pushing again

```bash
git add .
git status
git commit -m "Short description of what you did"
git push
```

You can paste your repo URL into your LinkedIn profile once it’s live.
