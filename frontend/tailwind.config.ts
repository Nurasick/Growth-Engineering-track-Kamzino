import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#0f172a",
        card: "#1e293b",
        border: "#334155",
      },
    },
  },
  plugins: [],
};

export default config;
