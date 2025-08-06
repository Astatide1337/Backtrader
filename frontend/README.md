# Backtrader Frontend (Next.js 14 - Pages Router)

A minimal, responsive dashboard for the Backtrader backend using Next.js 14 (Pages Router), TypeScript, SWR, and Tailwind CSS.

## Features

- Next.js 14 (Pages Router) with React 18 and TypeScript
- Tailwind CSS with a neutral theme and responsive layout
- SWR for data fetching (CSR)
- Lightweight UI components (Button, Card, Input, Select, Table, Modal, Toast, Skeleton, EmptyState, ErrorState)
- Responsive sidebar/topbar layout
- API client wrappers with retries and typed responses
- Sample dashboard showing portfolio, orders, backtests, and a compact AAPL ticker

## Prerequisites

- Node.js 18+ and npm

## Getting Started

1) Configure environment:
   - Copy `.env.local.example` to `.env.local` and edit if needed:
     ```
     NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
     ```

2) Install dependencies:
   ```
   npm install
   ```

3) Run the development server:
   ```
   npm run dev
   ```

4) Open http://localhost:3000 in your browser.

## Scripts

- `npm run dev` - Start Next.js dev server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run typecheck` - Run TypeScript type checks
- `npm run format` - Run Prettier formatting

## Project Structure

```
frontend/
  components/
    layout/ (AppLayout, Sidebar, Topbar)
    ui/ (Button, Card, Input, Select, Table, Modal, Toast, Skeleton, EmptyState, ErrorState)
  hooks/ (SWR-based hooks for API)
  lib/ (config, http, swr)
  pages/ (_app, _document, index, 404, 500)
  styles/ (globals.css)
  types/ (api types)
  tailwind.config.ts
  postcss.config.js
  tsconfig.json
  next.config.js
  .eslintrc.cjs
  .prettierrc
  package.json
```

## Notes

- Client-side rendering with SWR for now. No authentication or WebSocket in this subtask.
- Charting is intentionally omitted; the ticker area shows the latest close only.
- The layout collapses the sidebar on small screens and provides a Topbar toggle.
- Import aliases are configured via `tsconfig.json` (e.g., `import Button from 'components/ui/Button'`).
- Tailwind is set up through `styles/globals.css` and `tailwind.config.ts`.