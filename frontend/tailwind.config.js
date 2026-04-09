/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // PPT Dark Theme Colors
        primary: {
          50: '#e6faf5',
          100: '#b3f0e0',
          200: '#80e6cc',
          300: '#4ddcb7',
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
        dark: {
          50: '#1a2e2a',
          100: '#162623',
          200: '#121f1c',
          300: '#0e1916',
          400: '#0a1310',
          500: '#0a1f1a',
          600: '#081a15',
          700: '#061410',
          800: '#040f0b',
          900: '#020a06',
        },
        accent: {
          gold: '#f59e0b',
          amber: '#d97706',
          orange: '#ea580c',
        },
        surface: {
          card: 'rgba(20, 40, 35, 0.8)',
          glass: 'rgba(20, 40, 35, 0.6)',
          hover: 'rgba(45, 212, 191, 0.1)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Outfit', 'system-ui', 'sans-serif'],
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-right': 'slideRight 0.3s ease-out',
        'pulse-glow': 'pulseGlow 2s infinite',
        'count-up': 'countUp 1.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideRight: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 5px rgba(45, 212, 191, 0.3)' },
          '50%': { boxShadow: '0 0 20px rgba(45, 212, 191, 0.6)' },
        },
      },
    },
  },
  plugins: [],
}
