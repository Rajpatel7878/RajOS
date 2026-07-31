"use client";

import Logo from "./Logo";
import NavLinks from "./NavLinks";
import { Button } from "@/components/ui/button";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-black/30 backdrop-blur-xl">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6">
        <Logo />

        <NavLinks />

        <Button className="hidden md:flex bg-cyan-500 hover:bg-cyan-400 text-black font-semibold">
          Get Started
        </Button>
      </div>
    </header>
  );
}
