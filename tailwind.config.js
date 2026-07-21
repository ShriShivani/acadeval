/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#e8ecf3',
          100: '#c5cfe4',
          200: '#9fb0d3',
          300: '#7990c2',
          400: '#5c77b6',
          500: '#3f5eaa',
          600: '#3756a3',
          700: '#2d4b99',
          800: '#233f90',
          900: '#1B2A4A',
          950: '#0f1a2e',
        },
        teal: {
          50: '#e3f4f2',
          100: '#b8e3de',
          200: '#8ad1c9',
          300: '#5bbfb4',
          400: '#36b1a4',
          500: '#1E7F72',
          600: '#137a6d',
          700: '#0a7267',
          800: '#046a5f',
          900: '#005c51',
          950: '#003b35',
        },
        gold: {
          50: '#fdf8ee',
          100: '#faecd4',
          200: '#f7dfb8',
          300: '#f3d29c',
          400: '#f1c787',
          500: '#C99A3A',
          600: '#bf9231',
          700: '#b38827',
          800: '#a77e1d',
          900: '#966e0d',
          950: '#7a5800',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Poppins', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 2px 15px rgba(27, 42, 74, 0.08)',
        'card-hover': '0 8px 25px rgba(27, 42, 74, 0.15)',
        'teal-glow': '0 0 20px rgba(30, 127, 114, 0.3)',
        'gold-glow': '0 0 20px rgba(201, 154, 58, 0.3)',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'pulse-soft': 'pulseSoft 2s infinite',
        'spin-slow': 'spin 3s linear infinite',
        'shimmer': 'shimmer 1.5s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
