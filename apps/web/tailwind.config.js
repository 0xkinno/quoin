/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: {
          50: "#FAFAFA",
          100: "#F4F4F6",
          200: "#E5E5EA",
          300: "#D1D1D6",
          800: "#2C2C2E",
          900: "#1C1C1E",
        },
        graphite: {
          main: "#111113",
          muted: "#636366",
          subtle: "#8E8E93",
        },
        fenced: {
          blue: "#0047FF",
          emerald: "#10B981",
          rose: "#EF4444",
          amber: "#F59E0B",
        }
      },
      fontFamily: {
        sans: ["-apple-system", "BlinkMacSystemFont", "Inter", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["SF Mono", "Fira Code", "Courier New", "monospace"],
      }
    },
  },
  plugins: [],
}
