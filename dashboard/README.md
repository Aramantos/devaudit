# DevAudit Dashboard

Modern web dashboard for DevAudit local mode.

## Features

- 📊 **Real-time Monitoring** - Live updates via WebSocket
- 🎨 **Beautiful UI** - Modern, responsive design with Tailwind CSS
- 📦 **Package Tracking** - Visualize installed packages and outdated versions
- 🔒 **100% Private** - All data stays on your machine

## Tech Stack

- **Framework:** Next.js 14 (React)
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Charts:** Recharts
- **Language:** TypeScript

## Development

### Prerequisites

- Node.js 18+ and npm
- DevAudit installed in venv with server extras

### Install Dependencies

```bash
cd dashboard
npm install
```

### Development Server

```bash
npm run dev
```

Opens development server at http://localhost:3000

### Build for Production

```bash
npm run build
```

Creates optimized static build in `dist/` directory that will be served by the Python FastAPI server.

## How It Works

1. **FastAPI Server** - Serves static files from `dist/` directory
2. **WebSocket Connection** - Real-time communication for audit results
3. **Static Export** - Next.js exports to static HTML/JS/CSS (no Node.js runtime needed)

## Project Structure

```
dashboard/
├── src/
│   ├── app/
│   │   ├── layout.tsx      # Root layout
│   │   ├── page.tsx        # Main dashboard page
│   │   └── globals.css     # Global styles
│   ├── components/
│   │   ├── Overview.tsx           # Stats overview cards
│   │   ├── PythonDetails.tsx      # Python audit results
│   │   ├── NodeDetails.tsx        # Node.js audit results
│   │   ├── DockerDetails.tsx      # Docker audit results
│   │   └── RealtimeStatus.tsx     # WebSocket connection status
│   └── lib/
│       └── websocket.ts    # WebSocket hook
├── public/                 # Static assets
├── package.json
├── next.config.js          # Next.js config (static export)
├── tailwind.config.js      # Tailwind CSS config
└── tsconfig.json           # TypeScript config
```

## Using with DevAudit

1. **Build dashboard:**
   ```bash
   cd dashboard
   npm install
   npm run build
   ```

2. **Start DevAudit server:**
   ```bash
   cd ..
   .venv/Scripts/devaudit serve
   ```

3. **Open browser:**
   - Automatically opens to http://localhost:8080
   - Click "Run Scan" to audit your environment

## WebSocket Protocol

The dashboard communicates with the server via WebSocket messages:

### From Server to Dashboard

```typescript
// Scan started
{
  type: "scan_started",
  target_dir: string | null,
  total_auditors: number
}

// Auditor started
{
  type: "auditor_started",
  auditor: string,
  progress: { current: number, total: number }
}

// Auditor completed
{
  type: "auditor_completed",
  auditor: string,
  data: AuditResult,
  progress: { current: number, total: number }
}

// Scan completed
{
  type: "scan_completed",
  results: { [auditor: string]: AuditResult },
  summary: SummaryStats
}

// Error
{
  type: "auditor_error",
  auditor: string,
  error: string,
  progress: { current: number, total: number }
}
```

## Customization

### Colors

Edit `tailwind.config.js` to customize the color scheme.

### Components

All components are in `src/components/` - modify as needed.

### Layout

Main layout is in `src/app/layout.tsx` and `src/app/page.tsx`.

## Troubleshooting

### Dashboard not loading

- Ensure dashboard is built: `npm run build`
- Check `dist/` directory exists
- Verify FastAPI server is running

### WebSocket not connecting

- Check server is running on correct port
- Verify no firewall blocking localhost:8080
- Check browser console for errors

### Styles not loading

- Run `npm install` to ensure dependencies installed
- Rebuild: `npm run build`
- Clear browser cache

## License

MIT License - See main DevAudit LICENSE file
