/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: { vazir: ["Vazirmatn", "sans-serif"] },
      colors: {
        bg: "#0f1117",
        surface: "#171a23",
        surface2: "#1f2330",
        border: "#2a2f3e",
        primary: "#6366f1",
        accent: "#22c55e",
        danger: "#ef4444",
      },
    },
  },
  plugins: [],
};
