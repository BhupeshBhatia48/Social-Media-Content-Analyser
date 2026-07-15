/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#0B0C0F",
        surface: "#131417",
        "surface-raised": "#1A1B20",
        border: "#26272C",
        "border-soft": "#1E1F24",
        ink: "#EDEDEF",
        "ink-soft": "#A1A1AA",
        "ink-faint": "#6B6B72",
        accent: "#6E6AF6",
        "accent-soft": "#6E6AF622",
        success: "#3DD68C",
        "success-soft": "#3DD68C1A",
        info: "#5B9BF0",
        "info-soft": "#5B9BF01A",
        warning: "#F0B054",
        "warning-soft": "#F0B0541A",
        danger: "#F0616E",
        "danger-soft": "#F0616E1A",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
      },
      borderRadius: {
        xl2: "1.25rem",
      },
      boxShadow: {
        card: "0 1px 2px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.03)",
        raised: "0 8px 24px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,255,255,0.04)",
      },
    },
  },
  plugins: [],
};
