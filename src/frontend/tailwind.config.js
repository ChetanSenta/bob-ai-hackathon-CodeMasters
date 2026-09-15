/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg:      '#080d14',
        surface: '#0e1621',
        card:    '#131e2c',
        border:  '#1e2f45',
        hover:   '#1a2c42',
        primary: '#f1f5f9',
        muted:   '#7a92ac',
        accent:  '#38bdf8',
        'accent-dim': 'rgba(56,189,248,0.12)',
        green:   '#34d399',
        amber:   '#fbbf24',
        red:     '#f87171',
        orange:  '#fb923c',
        'green-dim':  'rgba(52,211,153,0.12)',
        'amber-dim':  'rgba(251,191,36,0.12)',
        'red-dim':    'rgba(248,113,113,0.12)',
        'orange-dim': 'rgba(251,146,60,0.12)',
      },
      fontFamily: {
        sans: ['"Inter"', '"Segoe UI"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 3px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.3)',
        'card-hover': '0 4px 16px rgba(0,0,0,0.5), 0 1px 4px rgba(0,0,0,0.4)',
        glow:  '0 0 16px rgba(56,189,248,0.15)',
        'glow-red': '0 0 16px rgba(248,113,113,0.15)',
      },
      borderRadius: {
        card: '10px',
      },
    },
  },
  plugins: [],
}
