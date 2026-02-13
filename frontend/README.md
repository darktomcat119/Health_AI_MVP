# Clinical Chatbot Frontend

Next.js 14 frontend for the AI Clinical Chatbot MVP. Features real-time SSE streaming, mental health-focused UX, dark mode, and crisis resource management.

## Tech Stack

| Component       | Technology              |
|-----------------|-------------------------|
| Framework       | Next.js 14              |
| Language        | TypeScript 5.3 (strict) |
| Styling         | Tailwind CSS 3.4        |
| State           | Zustand 4.5             |
| Animations      | Framer Motion 11        |
| Icons           | Lucide React            |

## Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open http://localhost:3000.

## Available Scripts

| Script | Command | Description |
|--------|---------|-------------|
| Dev    | `npm run dev` | Start development server |
| Build  | `npm run build` | Production build |
| Start  | `npm start` | Start production server |
| Lint   | `npm run lint` | Run ESLint |
| Type Check | `npm run type-check` | TypeScript validation |

## Component Architecture

```
app/layout.tsx (root: fonts, theme, metadata)
└── app/chat/layout.tsx (sidebar + main area)
    ├── Sidebar
    │   ├── SessionItem (per session)
    │   └── RiskIndicator (colored dot)
    └── ChatContainer
        ├── WelcomeScreen (empty state)
        ├── MessageBubble (static messages)
        ├── StreamingMessage (live streaming)
        ├── TypingIndicator (thinking dots)
        ├── CrisisBanner (emergency resources)
        ├── HandoffNotice (professional joining)
        └── ChatInput (auto-grow textarea)
```

## SSE Streaming Flow

1. User sends message via `ChatInput`
2. `useChat` hook calls `streamChat()` in SSE service
3. Backend processes: risk scoring → triage → LLM response
4. SSE events stream back:
   - `metadata` → update session risk info
   - `crisis` → show crisis banner with phone numbers
   - `token` → append word to `StreamingMessage`
   - `done` → finalize message, stop cursor
5. `StreamingMessage` shows blinking cursor during stream
6. Auto-scroll follows new content

## Design System

### Colors

| Token | Light | Dark |
|-------|-------|------|
| Background | `#FAFBFC` | `#0F0F1A` |
| Surface | `#FFFFFF` | `#1A1A2E` |
| User Bubble | `#4F46E5` | `#4F46E5` |
| Bot Bubble | `#FFFFFF` | `#1E1E32` |
| Accent | `#6366F1` | `#818CF8` |
| Crisis | `#FEF3C7` | `#78350F` |

### Typography

- Font: Inter (Google Fonts)
- Body: 14-16px
- Headings: 18-24px
- Spacing: 4px grid system

### Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Full-width, drawer sidebar |
| Tablet | 640-1024px | Collapsible sidebar |
| Desktop | > 1024px | Persistent sidebar |

## Screenshots

> Screenshots will be added after the first release.
