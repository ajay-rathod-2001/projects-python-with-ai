/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        phonepe: {
          dark: "#090D16",
          darker: "#060910",
          card: "#111827",
          cardHover: "#162032",
          border: "rgba(255, 255, 255, 0.08)",
          purple: "#5f259f",
          accent: "#8B5CF6",
          light: "#A78BFA",
          rose: "#F43F5E",
          emerald: "#10B981",
        },
      },
    },
  },
  plugins: [],
}

