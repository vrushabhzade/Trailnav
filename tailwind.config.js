/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#020617",
                foreground: "#f8fafc",
                card: {
                    DEFAULT: "rgba(15, 23, 42, 0.8)",
                    hover: "rgba(30, 41, 59, 0.9)",
                },
                primary: {
                    DEFAULT: "#06b6d4",
                    hover: "#22d3ee",
                },
                secondary: "#64748b",
                accent: "#8b5cf6",
                success: "#10b981",
                warning: "#f59e0b",
                error: "#ef4444",
            },
            fontFamily: {
                sans: ["Inter", "system-ui", "sans-serif"],
                display: ["Outfit", "Inter", "system-ui", "sans-serif"],
            },
            backdropBlur: {
                xs: "2px",
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out forwards',
                'slide-up': 'slideUp 0.5s ease-out forwards',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
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
            },
        },
    },
    plugins: [],
}
