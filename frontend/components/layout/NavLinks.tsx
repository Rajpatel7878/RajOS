"use client";

import Link from "next/link";

const links = [
  { name: "Features", href: "#features" },
  { name: "Workspace", href: "#workspace" },
  { name: "Pricing", href: "#pricing" },
  { name: "Docs", href: "#docs" },
];

export default function NavLinks() {
  return (
    <nav className="hidden items-center gap-8 md:flex">
      {links.map((link) => (
        <Link
          key={link.name}
          href={link.href}
          className="text-sm font-medium text-slate-300 transition-colors duration-300 hover:text-cyan-400"
        >
          {link.name}
        </Link>
      ))}
    </nav>
  );
}
