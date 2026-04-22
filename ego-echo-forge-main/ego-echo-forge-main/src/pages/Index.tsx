import heroBg from "@/assets/hero-bg.jpg";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import HowItWorksSection from "@/components/HowItWorksSection";
import RAGSection from "@/components/RAGSection";
import TechStackSection from "@/components/TechStackSection";
import PricingSection from "@/components/PricingSection";
import PrivacyCTASection from "@/components/PrivacyCTASection";
import FloatingParticles from "@/components/FloatingParticles";

const Index = () => {
  return (
    <div className="relative min-h-screen">
      {/* Fixed mountain background across entire page */}
      <div className="fixed inset-0 z-0">
        <img
          src={heroBg}
          alt=""
          className="w-full h-full object-cover"
          width={1920}
          height={1080}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-foreground/40 via-foreground/60 to-foreground/80" />
      </div>

      {/* 3D Floating particles across entire page */}
      <FloatingParticles />

      {/* Content */}
      <div className="relative z-10">
        <Navbar />
        <HeroSection />
        <FeaturesSection />
        <HowItWorksSection />
        <RAGSection />
        <TechStackSection />
        <PricingSection />
        <PrivacyCTASection />
      </div>
    </div>
  );
};

export default Index;
