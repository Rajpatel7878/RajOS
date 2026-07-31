"use client";

import { Check } from "lucide-react";

const plans = [
  {
    name: "Free",
    price: "$0",
    description: "For getting started",
    features: [
      "Basic AI Assistant",
      "Smart Notes",
      "Personal Workspace",
    ],
  },
  {
    name: "Pro",
    price: "$19",
    description: "For serious productivity",
    popular: true,
    features: [
      "Advanced AI Models",
      "AI Memory",
      "Automation Tools",
      "Priority Support",
      "API Access",
    ],
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For teams and companies",
    features: [
      "Unlimited AI",
      "Team Workspace",
      "Advanced Security",
      "Dedicated Support",
    ],
  },
];

export default function PricingCards() {
  return (
    <>
      {plans.map((plan) => (
        <div
          key={plan.name}
          className={`glass rounded-3xl p-8 transition-all duration-500 hover:-translate-y-3 hover:scale-[1.03] hover-glow
          ${
            plan.popular
              ? "border-cyan-400/50 shadow-lg shadow-cyan-500/30 scale-105"
              : ""
          }`}
        >

          {plan.popular && (
            <div className="mb-4 inline-block rounded-full bg-cyan-400/20 px-4 py-1 text-xs font-semibold text-cyan-300">
              MOST POPULAR
            </div>
          )}

          <h3 className="text-2xl font-bold text-white">
            {plan.name}
          </h3>

          <p className="mt-2 text-sm text-slate-400">
            {plan.description}
          </p>

          <p className="mt-6 text-5xl font-extrabold text-cyan-400">
            {plan.price}
          </p>

          {plan.price !== "Custom" && (
            <span className="text-slate-400">
              / month
            </span>
          )}

          <div className="mt-8 space-y-4">

            {plan.features.map((feature) => (
              <div
                key={feature}
                className="flex items-center gap-3 text-slate-300"
              >
                <Check className="h-5 w-5 text-cyan-400" />
                {feature}
              </div>
            ))}

          </div>

          <button className="mt-8 w-full rounded-xl bg-cyan-500 py-3 font-semibold text-black transition hover:bg-cyan-400">
            Choose Plan
          </button>

        </div>
      ))}
    </>
  );
}
