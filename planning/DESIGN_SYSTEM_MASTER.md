# 🎨 Master Design System - Aramantos Digital Suite

**Created:** 2025-11-18
**Version:** 1.0
**Apps Covered:** DevAudit, ProveChain, SignaSeal

---

## Philosophy

**"Cohesive but Distinct"** - Each app in the suite has its own color identity and personality, but shares common design patterns, spacing, typography principles, and visual effects.

### Design Principles

1. **Color-Coded Identity** - Each app gets a unique brand color
2. **Dark Mode First** - All apps support dark mode as primary experience
3. **Glass Morphism** - Consistent use of backdrop blur and transparency
4. **HSL Color Variables** - Semantic, theme-able color system
5. **Tailwind Foundation** - Shared utility-first CSS framework
6. **Accessible Contrast** - WCAG AA minimum for all text
7. **Smooth Transitions** - Consistent animation timing and easing

---

## App Color Identities

### DevAudit - Green/Emerald (Health & System Monitoring)
```css
--primary: 159 68% 45%;        /* #10b981 - Emerald-500 */
--primary-light: 142 77% 73%;  /* #6ee7b7 - Emerald-300 */
--primary-dark: 158 64% 52%;   /* #059669 - Emerald-600 */
```
**Theme:** Health monitoring, system cleanliness, environment auditing
**Vibe:** Technical, reliable, clean, professional

### ProveChain - Purple/Violet (Innovation & IP Protection)
```css
--primary: 262.1 83.3% 57.8%;  /* Vibrant purple */
--primary-foreground: 210 40% 98%;
```
**Theme:** Innovation, creativity, IP protection, proof of ownership
**Vibe:** Bold, creative, forward-thinking, vibrant

### SignaSeal - Muted Blue-Purple (Document Focus & Professionalism)
```css
--accent: 240 25% 30%;         /* Muted blue-purple, subdued */
--accent-foreground: 0 0% 100%;
```
**Theme:** Document signing, legal, professional, trustworthy
**Vibe:** Serious, professional, document-focused, minimal distraction

---

## Typography

### Font Families

**SignaSeal:**
```css
font-family: 'Satoshi', system-ui, sans-serif;
```
- **Weight:** 300-900 (Variable font)
- **Usage:** Entire app, clean and modern
- **Source:** CDN Fonts

**ProveChain & DevAudit:**
```css
font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```
- **Usage:** System fonts for performance
- **Fallback:** Consistent across platforms

### Hierarchy

```css
/* Headings - All Apps */
h1: text-3xl md:text-4xl font-bold (48px desktop, 30px mobile)
h2: text-2xl md:text-3xl font-semibold (30px desktop, 24px mobile)
h3: text-xl font-semibold (20px)
h4: text-lg font-medium (18px)

/* Body Text */
body: text-base (16px)
small: text-sm (14px)
xs: text-xs (12px)

/* Text Wrapping (ProveChain Pattern) */
h1, h2, h3, h4, h5, h6, p {
  text-wrap: balance; /* Better typography */
}
```

---

## Color System Architecture

### HSL Variable Pattern (All Apps)

**Why HSL?**
- Easy theme switching
- Semantic naming
- Component-agnostic
- shadcn/ui compatible

### Base Variables Structure

```css
:root {
  /* Surfaces */
  --background: [hsl];    /* Page background */
  --foreground: [hsl];    /* Primary text */
  --card: [hsl];          /* Card backgrounds */
  --card-foreground: [hsl];

  /* Brand */
  --primary: [hsl];       /* App-specific brand color */
  --primary-foreground: [hsl];
  --accent: [hsl];        /* Secondary brand color */
  --accent-foreground: [hsl];

  /* UI Elements */
  --muted: [hsl];         /* Muted backgrounds */
  --muted-foreground: [hsl];
  --border: [hsl];        /* Border color */
  --input: [hsl];         /* Input borders */
  --ring: [hsl];          /* Focus rings */

  /* Layout */
  --radius: 0.5rem;       /* Border radius */
}
```

### Dark Mode Pattern

**All apps use `.dark` class:**
```css
.dark {
  --background: [dark value];
  --foreground: [light value];
  /* ... */
}
```

**Implementation:**
```typescript
// Dark mode toggle
localStorage.setItem('[app]-theme', 'dark' | 'light');
document.documentElement.classList.toggle('dark');
```

---

## Common Color Values

### Light Mode Foundation
```css
:root {
  --background: 0 0% 100%;           /* White */
  --foreground: 222.2 84% 4.9%;      /* Near black */
  --border: 214.3 31.8% 78%;         /* Light grey */
}
```

### Dark Mode Foundation

**ProveChain (Deep Dark):**
```css
.dark {
  --background: 222.2 84% 4.9%;      /* Very dark blue-grey */
  --card: 222.2 84% 4.9%;
  --border: 217.2 32.6% 17.5%;
}
```

**SignaSeal (Charcoal with Blue Tint):**
```css
.dark {
  --background: 0 0% 6%;             /* Deep charcoal */
  --card: 220 15% 12%;               /* Subtle bluish grey */
  --border: 220 15% 18%;
}
```

**DevAudit (Modern Dark with Green Tint):**
```css
.dark {
  --background: #0a0f1a;             /* dark-950 */
  --surface: #1a2332;                /* dark-850 */
  --card: #1f2937;                   /* dark-800 */
  --border: #374151;                 /* dark-700 */
}
```

---

## Component Patterns

### 1. Cards

#### Base Card Structure
```tsx
<div className="bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border border-gray-200 dark:border-dark-700 p-6">
  <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
    Card Title
  </h3>
  <p className="text-gray-600 dark:text-gray-400">
    Card content
  </p>
</div>
```

#### Glass Morphism Cards (ProveChain Pattern)
```css
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.15);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.dark .glass-card {
  background: rgba(30, 30, 46, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}
```

#### Stat Cards (DevAudit Pattern)
```tsx
<div className="bg-gray-50 dark:bg-dark-700 rounded p-3 border border-gray-100 dark:border-dark-600">
  <p className="text-sm text-gray-600 dark:text-gray-400">Label</p>
  <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
    {value}
  </p>
</div>
```

### 2. Buttons

#### SignaSeal Button Pattern
```css
.btn {
  @apply px-4 py-2 rounded-md font-medium transition-colors;
}

.btn-accent {
  @apply bg-accent text-accent-foreground hover:bg-accent/90;
}

.btn-sm {
  @apply px-3 py-1.5 text-sm;
}

.btn-destructive {
  @apply bg-red-500 text-white hover:bg-red-600;
}
```

#### DevAudit Button Pattern
```tsx
<button className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-all shadow-md hover:shadow-lg hover:shadow-primary-500/50">
  Primary Action
</button>
```

### 3. Badges/Tags

#### Framework Badges (Python, Node, etc.)
```tsx
<span className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-800 text-xs rounded">
  Badge Text
</span>
```

### 4. Status Indicators

#### Color-Coded Status
```tsx
// Success/Healthy
<div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-300">

// Warning
<div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 text-yellow-700 dark:text-yellow-300">

// Error/Attention
<div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300">

// Info
<div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300">
```

---

## Spacing Scale

### Consistent Across All Apps
```css
/* Tailwind Default Scale */
0.5: 2px
1: 4px
2: 8px
3: 12px
4: 16px
5: 20px
6: 24px
8: 32px
10: 40px
12: 48px
16: 64px
20: 80px
24: 96px
```

### Common Usage Patterns
```css
/* Card Padding */
p-6 (24px) - Standard card padding
p-4 (16px) - Compact card padding
p-3 (12px) - Stat card padding

/* Section Spacing */
py-8 (32px) - Main content sections
py-12 (48px) - Major section dividers
py-20 (80px) - Hero sections

/* Gap in Grids */
gap-4 (16px) - Standard grid gap
gap-6 (24px) - Loose grid gap
gap-2 (8px) - Tight grid gap
```

---

## Shadows

### Light Mode Shadows
```css
shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05)
shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)
shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)
shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)
```

### Dark Mode Shadows
```css
/* SignaSeal Custom Shadow */
dark-card-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.15)

/* DevAudit Pattern */
dark:shadow-dark-950/50  /* Softer shadows in dark mode */
```

### Glow Effects (Brand Colors)
```css
/* DevAudit Green Glow */
hover:shadow-lg hover:shadow-primary-500/50

/* ProveChain Purple Glow */
hover:shadow-lg hover:shadow-primary/30
```

---

## Visual Effects

### 1. Animations

#### Pulse (SignaSeal Pattern)
```css
@keyframes gradientShift {
  0%, 100% { filter: hue-rotate(0deg); }
  50% { filter: hue-rotate(30deg); }
}

.animate-gradient {
  animation: gradientShift 20s ease-in-out infinite;
}
```

#### Slow Pulse (ProveChain Pattern)
```css
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

#### Transitions (All Apps)
```css
transition-colors duration-200  /* Color changes */
transition-all duration-200     /* Everything */
transition-shadow duration-300  /* Shadows on hover */
```

### 2. Gradient Text (ProveChain)
```css
.gradient-text {
  @apply bg-gradient-to-r from-primary-500 to-emerald-400 bg-clip-text text-transparent;
  padding-bottom: 0.15em; /* Fix descender clipping */
  display: inline-block;
}
```

### 3. Backdrop Blur (All Apps)
```css
backdrop-filter: blur(10px);
-webkit-backdrop-filter: blur(10px); /* Safari */
```

### 4. Scrollbar Hiding (ProveChain Pattern)
```css
.scrollbar-hide {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;  /* Chrome, Safari, Opera */
}
```

---

## Layout Patterns

### Container Max-Width
```css
max-w-7xl mx-auto px-4 sm:px-6 lg:px-8  /* All apps */
```
**Breakdown:**
- `max-w-7xl`: 1280px maximum width
- `mx-auto`: Center horizontally
- `px-4 sm:px-6 lg:px-8`: Responsive padding (16px → 24px → 32px)

### Grid Patterns

#### Stats Grid (DevAudit)
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* Stat cards */}
</div>
```

#### Content Grid
```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  {/* Content cards */}
</div>
```

### Responsive Breakpoints (Tailwind Default)
```css
sm: 640px   /* Small screens */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large desktops */
```

---

## Icon System

### Library: Lucide React (All Apps)
```tsx
import { Play, Loader, Package, AlertTriangle } from 'lucide-react';

<Play className="w-5 h-5" />        /* Standard size */
<Loader className="w-4 h-4" />      /* Small size */
<Package className="w-6 h-6" />     /* Large size */
```

### Icon Colors
```tsx
/* Brand colored icons */
<Icon className="text-primary-600 dark:text-primary-400" />

/* Status colored icons */
<AlertTriangle className="text-yellow-600 dark:text-yellow-400" />
<CheckCircle className="text-green-600 dark:text-green-400" />
<XCircle className="text-red-600 dark:text-red-400" />
```

---

## Watermarks & Branding

### Footer Pattern (All Apps)
```tsx
<footer className="bg-white dark:bg-dark-850 border-t border-gray-200 dark:border-dark-700">
  <div className="max-w-7xl mx-auto px-4 py-6">
    <div className="text-center text-gray-500 dark:text-gray-400 text-sm">
      <p className="font-semibold text-gray-700 dark:text-gray-300">
        {appName} v{version}
      </p>
      <p className="mt-1 flex items-center justify-center gap-2">
        <span className="inline-block w-2 h-2 bg-primary-500 rounded-full animate-pulse"></span>
        {tagline}
      </p>
    </div>
  </div>
</footer>
```

### Privacy Indicators
```tsx
/* DevAudit Pattern */
<span className="inline-block w-2 h-2 bg-primary-500 rounded-full animate-pulse"></span>
100% private • All data stays on your machine
```

---

## Form Elements

### Input Pattern (SignaSeal/ProveChain)
```tsx
<input
  className="w-full px-4 py-2 rounded-md border border-input bg-background text-foreground focus:ring-2 focus:ring-ring focus:border-transparent"
/>
```

### Select/Dropdown
```tsx
<select className="w-full px-4 py-2 rounded-md border border-input bg-background">
  <option>...</option>
</select>
```

---

## Accessibility

### Focus States
```css
focus:ring-2 focus:ring-ring focus:outline-none
focus-visible:ring-2 focus-visible:ring-ring /* Keyboard only */
```

### Color Contrast Requirements
- **Body Text:** Minimum 4.5:1 (WCAG AA)
- **Large Text (18px+):** Minimum 3:1
- **UI Components:** Minimum 3:1

### Skip Links
```tsx
<a href="#main" className="sr-only focus:not-sr-only">
  Skip to main content
</a>
```

---

## Implementation Checklist

### New App Setup
- [ ] Install Tailwind CSS
- [ ] Configure dark mode (`darkMode: 'class'`)
- [ ] Define HSL color variables
- [ ] Choose brand color (unique to app)
- [ ] Set up typography (Satoshi or system fonts)
- [ ] Implement glass morphism utilities
- [ ] Add common animations
- [ ] Test dark/light mode switching
- [ ] Verify accessibility (contrast ratios)
- [ ] Add footer with branding

### Component Checklist
- [ ] Cards with dark mode support
- [ ] Buttons (primary, secondary, destructive)
- [ ] Badges/tags with brand colors
- [ ] Status indicators (success, warning, error, info)
- [ ] Form inputs with focus states
- [ ] Icons from Lucide React
- [ ] Loading states (spinners, skeletons)
- [ ] Tooltips and popovers
- [ ] Modals/dialogs

---

## File Structure

### Recommended Layout
```
app/
├── globals.css          # Tailwind + HSL variables
├── layout.tsx           # Root layout with theme provider
└── page.tsx            # Main pages

components/
├── ui/                 # Reusable UI components
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Badge.tsx
│   └── ...
└── [feature]/          # Feature-specific components

lib/
├── theme.ts           # Theme toggle hook
└── utils.ts           # Utility functions

tailwind.config.js     # Tailwind configuration
```

---

## Quick Reference

### App Color Codes
```
DevAudit:   #10b981 (Green/Emerald)
ProveChain: hsl(262.1 83.3% 57.8%) (Purple)
SignaSeal:  hsl(240 25% 30%) (Muted Blue-Purple)
```

### Common Class Patterns
```css
/* Card */
bg-white dark:bg-dark-800 rounded-lg shadow dark:shadow-dark-950/50 border border-gray-200 dark:border-dark-700 p-6

/* Heading */
text-xl font-semibold text-gray-900 dark:text-gray-100

/* Body Text */
text-gray-600 dark:text-gray-400

/* Button */
px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-all
```

---

## Future Enhancements

### Potential Additions
- [ ] Animation library (Framer Motion)
- [ ] Toast notification system
- [ ] Loading skeleton components
- [ ] Data visualization components (charts)
- [ ] Table components with sorting/filtering
- [ ] Command palette (⌘K)
- [ ] Keyboard shortcuts system

---

## Maintained By

**Aramantos Digital**
**Created:** 2025-11-18
**Last Updated:** 2025-11-18
**Version:** 1.0

**Apps in Suite:**
- **DevAudit** - Developer environment auditing
- **ProveChain** - IP protection and proof of ownership
- **SignaSeal** - Document signing and verification

---

**Next Steps:**
1. ✅ Review this master document
2. ✅ Apply baseline to DevAudit
3. ⏳ Test consistency across apps
4. ⏳ Create reusable component library (future)
5. ⏳ Document custom components per app
