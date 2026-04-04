import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        hg: {
          lime:    "#CAFF33",
          "lime-d":"#b3e020",
          black:   "#0d0d0d",
          surface: "#141414",
          card:    "#1a1a1a",
          border:  "#242424",
          muted:   "#2e2e2e",
        },
      },
    },
  },
  plugins: [],
};

export default config;
