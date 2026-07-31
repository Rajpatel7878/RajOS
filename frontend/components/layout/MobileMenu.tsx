"use client";

import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";

export default function MobileMenu() {
  return (
    <div className="md:hidden">
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon">
            <Menu className="h-6 w-6" />
          </Button>
        </SheetTrigger>

        <SheetContent side="right" className="bg-black text-white border-white/10">
          <nav className="mt-10 flex flex-col gap-6">
            <a href="#features">Features</a>
            <a href="#workspace">Workspace</a>
            <a href="#pricing">Pricing</a>
            <a href="#docs">Docs</a>
          </nav>
        </SheetContent>
      </Sheet>
    </div>
  );
}
