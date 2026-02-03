# 🚀 RAG Chat Frontend

A beautiful, modern frontend for the RAG (Retrieval-Augmented Generation) Chat application. Built with Next.js, TypeScript, and Tailwind CSS, featuring document upload, AI-powered summarization, and themeable chat interface.

## ✨ Features

- 🔐 **Secure API Key Management** - Safe OpenAI API key handling
- 📄 **Smart PDF Upload** - Drag & drop PDF processing with progress tracking
- 🤖 **Intelligent Summarization** - Book-back-cover style document summaries
- 💬 **Dual Chat Modes** - Normal AI chat + RAG-powered document Q&A
- 🎨 **12 Beautiful Themes** - Customizable color schemes with persistence
- 📱 **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- ⚡ **Real-time Streaming** - Live AI response streaming
- 🧪 **Comprehensive Testing** - Full E2E test coverage with Playwright

## 🚀 Getting Started

### Quick Start (Full Stack)

The easiest way to get everything running is with our magical development scripts from the project root:

```bash
# From the project root directory
./start-dev.sh      # 🪄 Starts both frontend + backend servers
./status-dev.sh     # 📊 Check if servers are running
./stop-dev.sh       # 🛑 Stop both servers gracefully
```

This will fire up:
- 🎨 **Frontend**: [http://localhost:3000](http://localhost:3000)
- 🔧 **Backend API**: [http://localhost:8000](http://localhost:8000)
- 📖 **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend Only Development

If you just want to work on the frontend (with a running backend elsewhere):

```bash
npm run dev
# or if you're feeling fancy
yarn dev
pnpm dev
bun dev
```

Then cruise over to [http://localhost:3000](http://localhost:3000) and watch the magic happen! ✨

### Backend Only

Need just the API server? We've got you covered:

```bash
# From the project root directory
./start-backend.sh  # 🎵 Just the FastAPI server
```

### First Time Setup

1. **Enter your OpenAI API Key** - The app will guide you through this on first launch
2. **Upload a PDF** - Drag & drop any PDF to start the RAG experience
3. **Choose your vibe** - Pick from 12 beautiful color themes in Settings
4. **Start chatting!** - Ask questions about your document or chat normally

## 🧪 Testing

We've got you covered with comprehensive End-to-End testing using [Playwright](https://playwright.dev/). Because broken features are like broken hearts - nobody wants them! 💔

### Test Commands

```bash
# Run all tests on ALL browsers (Chrome, Firefox, WebKit 🌐)
npm run test:e2e

# Quick tests on Chrome only (for speedy development! ⚡)
npm run test:e2e:fast

# Stable tests on Chrome & Firefox only (our reliable duo! 🎸)
npm run test:e2e:stable

# Run tests with the fancy Playwright UI
npm run test:e2e:ui

# Run tests with browser visible (great for debugging)
npm run test:e2e:headed

# Debug mode - step through tests like a detective 🔍
npm run test:e2e:debug
```

### What's Tested

Our test suite is more thorough than a TSA security check:

- ✅ **API Key Flow** - Input validation, navigation, persistence
- ✅ **Settings Modal** - Theme selection, model switching, modal behavior
- ✅ **File Upload** - Drag & drop, progress tracking, document management
- ✅ **Chat Functionality** - Message sending, streaming responses, error handling
- ✅ **UI Theming** - Color application, persistence, visual states
- ✅ **Cross-browser** - Chromium, Firefox, WebKit compatibility

### Test Coverage

- **📱 Responsive Design** - Mobile, tablet, desktop viewports
- **🎨 Theme Persistence** - Colors survive page reloads
- **⚡ Real-time Features** - Progress bars, streaming responses
- **🚨 Error Handling** - API failures, network issues, validation
- **♿ Accessibility** - Focus states, keyboard navigation

## 🛠 Development

### Full Stack Scripts (from project root)

```bash
./start-dev.sh       # 🚀 Start both frontend + backend
./stop-dev.sh        # 🛑 Stop both servers
./status-dev.sh      # 📊 Check server status
./start-backend.sh   # 🎵 Start backend only
```

### Frontend Scripts (from frontend directory)

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run test:e2e        # Run E2E tests (all browsers)
npm run test:e2e:fast   # Quick tests (Chrome only)
npm run test:e2e:stable # Stable tests (Chrome & Firefox)
npm run test:e2e:ui     # Run tests with UI
```

### Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript (because we like our code type-safe!)
- **Styling**: Tailwind CSS + Radix UI components
- **Testing**: Playwright for E2E testing
- **State Management**: React hooks + localStorage
- **Icons**: Lucide React (beautiful and lightweight)

## 📚 Learn More

Want to dive deeper? Check out these awesome resources:

- [Next.js Documentation](https://nextjs.org/docs) - The holy grail of Next.js knowledge
- [Tailwind CSS](https://tailwindcss.com/docs) - Utility-first CSS framework
- [Playwright Testing](https://playwright.dev/) - Modern E2E testing
- [Radix UI](https://www.radix-ui.com/) - Unstyled, accessible components

## 🚀 Deploy on Vercel

Ready to show your creation to the world? Deploy with Vercel (the creators of Next.js):

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme)

Check out the [Next.js deployment docs](https://nextjs.org/docs/app/building-your-application/deploying) for more deployment options.

---

Built with ❤️ and lots of ☕ by the RAG Chat team
