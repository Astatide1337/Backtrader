import type { Config } from 'tailwindcss';

export default {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './lib/**/*.{js,ts,jsx,tsx}',
    './hooks/**/*.{js,ts,jsx,tsx}'
  ],
  darkMode: ['class'],
  theme: {
    // Add extended breakpoints and container sizes for ultra-wide displays
    screens: {
      xs: '480px',
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px',
      // New larger screens
      '3xl': '1920px',
      '4xl': '2160px' // 2K/ultra-wide friendly
    },
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        sm: '1rem',
        md: '1.25rem',
        lg: '1.5rem',
        xl: '2rem',
        '2xl': '2rem',
        '3xl': '2.5rem',
        '4xl': '3rem'
      }
    },
    extend: {
      maxWidth: {
        // wider content containers for dashboards
        '7xl': '80rem', // 1280px
        '8xl': '90rem', // 1440px
        '9xl': '96rem', // 1536px
        '10xl': '112rem' // 1792px
      },
      colors: {
        background: 'hsl(0 0% 100%)',
        foreground: 'hsl(222.2 84% 4.9%)',
        primary: {
          DEFAULT: 'hsl(221 83% 53%)',
          foreground: 'hsl(210 40% 98%)'
        },
        muted: {
          DEFAULT: 'hsl(210 40% 96%)',
          foreground: 'hsl(215 16% 47%)'
        },
        card: {
          DEFAULT: 'hsl(0 0% 100%)',
          foreground: 'hsl(222.2 84% 4.9%)'
        },
        border: 'hsl(214.3 31.8% 91.4%)'
      },
      boxShadow: {
        card: '0 1px 2px 0 rgba(0,0,0,0.05)'
      },
      gridTemplateColumns: {
        // helper for dense dashboards on big screens
        'auto-fit-16': 'repeat(auto-fit, minmax(16rem, 1fr))',
        'auto-fit-20': 'repeat(auto-fit, minmax(20rem, 1fr))'
      },
      spacing: {
        '18': '4.5rem'
      }
    }
  },
  plugins: []
} satisfies Config;