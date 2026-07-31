"use client";

import FooterLinks from "./FooterLinks";
import SocialLinks from "./SocialLinks";

export default function Footer() {
  return (
    <footer className="border-t border-white/10">

      <div className="mx-auto max-w-7xl px-6 py-12">

        <div className="text-center">

          <h2 className="text-3xl font-bold text-white">
            RajOS
          </h2>

          <p className="mt-3 text-slate-400">
            AI Productivity Workspace
          </p>

        </div>

        <FooterLinks />

        <SocialLinks />


        <div className="mt-10 border-t border-white/10 pt-6 text-center text-sm text-slate-500">

          © {new Date().getFullYear()} RajOS. All rights reserved.

        </div>

      </div>

    </footer>
  );
}
