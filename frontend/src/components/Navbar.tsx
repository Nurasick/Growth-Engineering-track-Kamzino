"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/",          label: "Dashboard" },
  { href: "/analytics", label: "Analytics" },
  { href: "/scrapers",  label: "Scrapers" },
  { href: "/pipeline",  label: "Pipeline" },
  { href: "/downloads", label: "Downloads" },
  { href: "/charts",    label: "Charts" },
  { href: "/playbooks", label: "Playbooks" },
];

function HiggsLogo() {
  return (
    <Link href="/" className="flex items-center gap-3 group">
      <img
        src="/logo.jpg"
        alt="Higgsfield"
        width={28}
        height={28}
        className="rounded shrink-0 object-contain"
      />
      <span className="text-sm font-bold tracking-[0.18em] uppercase text-white group-hover:text-[#CAFF33] transition-colors">
        HIGGSFIELD
      </span>
    </Link>
  );
}

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-10 border-b border-[#242424] bg-[#0d0d0d]/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-8 px-6 py-3">
        <HiggsLogo />

        <div className="flex gap-0.5">
          {links.map(({ href, label }) => {
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={`rounded px-3 py-1.5 text-xs font-medium tracking-wide uppercase transition-colors ${
                  active
                    ? "bg-[#CAFF33]/10 text-[#CAFF33]"
                    : "text-white/40 hover:text-white/80 hover:bg-white/5"
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
