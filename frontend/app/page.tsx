import Navbar from "@/components/layout/Navbar";
import AnimatedBackground from "@/components/background/AnimatedBackground";
import PremiumHero from "@/components/premium-hero/PremiumHero";
import AIDemoSection from "@/components/ai-demo/AIDemoSection";
import FeatureSection from "@/components/features/FeatureSection";
import WorkspaceSection from "@/components/workspace/WorkspaceSection";
import PricingSection from "@/components/pricing/PricingSection";
import DocsSection from "@/components/docs/DocsSection";
import Footer from "@/components/footer/Footer";

export default function Home() {
  return (
    <main className="relative min-h-screen bg-background text-foreground">

      <AnimatedBackground />
      <Navbar />

      <PremiumHero />

      <FeatureSection />

      <WorkspaceSection />

      <PricingSection />

      <DocsSection />

      <AIDemoSection />

      <Footer />

    </main>
  );
}
