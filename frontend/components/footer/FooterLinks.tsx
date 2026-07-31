"use client";

const links = [
  {
    title: "Product",
    items: [
      "Features",
      "Workspace",
      "Pricing",
    ],
  },
  {
    title: "Resources",
    items: [
      "Documentation",
      "Guides",
      "Support",
    ],
  },
  {
    title: "Company",
    items: [
      "About",
      "Contact",
      "Privacy",
    ],
  },
];

export default function FooterLinks() {
  return (
    <div className="mt-10 grid gap-8 sm:grid-cols-3">

      {links.map((section) => (
        <div key={section.title}>

          <h3 className="mb-4 font-semibold text-white">
            {section.title}
          </h3>

          <div className="space-y-3">

            {section.items.map((item) => (
              <p
                key={item}
                className="text-sm text-slate-400 hover:text-cyan-400 transition-colors"
              >
                {item}
              </p>
            ))}

          </div>

        </div>
      ))}

    </div>
  );
}
