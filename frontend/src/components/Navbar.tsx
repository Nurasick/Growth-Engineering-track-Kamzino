"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/",          label: "Dashboard" },
  { href: "/analytics", label: "Analytics" },
  { href: "/scrapers",  label: "Scrapers" },
  { href: "/pipeline",  label: "Pipeline" },
  { href: "/downloads", label: "Downloads" },
  { href: "/charts", label: "Charts" },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-10 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-8 px-6 py-3">
        <div className="flex items-center gap-2">
          <span className="text-violet-400 text-xl">⚡</span>
          <span className="font-semibold text-slate-100 text-sm tracking-wide">
            Growth Intelligence
          </span>
        </div>

        <div className="flex gap-1">
          {links.map(({ href, label }) => {
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={`rounded-md px-3 py-1.5 text-sm transition-colors ${
                  active
                    ? "bg-violet-500/20 text-violet-300"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }`}
              >
                {label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
