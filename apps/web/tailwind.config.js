/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        bg2: "var(--bg2)",
        core: "var(--core)",
        shell: "var(--shell)",
        line: "var(--line)",
        line2: "var(--line2)",
        t1: "var(--t1)",
        t2: "var(--t2)",
        t3: "var(--t3)",
        rec: "var(--rec)",
        proof: "var(--proof)",
        fork: "var(--fork)",
        err: "var(--err)",
        brand: "var(--brand)",
      },
      fontFamily: {
        display: ["Unbounded", "sans-serif"],
        body: ["Space Grotesk", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      transitionTimingFunction: {
        ease: "cubic-bezier(0.32, 0.72, 0, 1)",
      },
    },
  },
  plugins: [],
}
