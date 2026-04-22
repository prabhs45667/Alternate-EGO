import { motion } from "framer-motion";
import { UserPlus, Camera, Mic, MessageCircle } from "lucide-react";

const steps = [
  {
    phase: "01",
    title: "Imprint",
    subtitle: "Name + Data",
    desc: "Enter your name, connect social profiles, upload data exports. We scrape public data to build your twin's knowledge base.",
    icon: UserPlus,
  },
  {
    phase: "02",
    title: "Perceive",
    subtitle: "4 Emotions",
    desc: "Capture four emotion-validated photos — neutral, happy, sad, angry — using real-time computer vision.",
    icon: Camera,
  },
  {
    phase: "03",
    title: "Embody",
    subtitle: "Voice Clone",
    desc: "Answer 9 personality-probing questions. Your voice is cloned locally with zero cloud APIs.",
    icon: Mic,
  },
  {
    phase: "04",
    title: "Converge",
    subtitle: "Chat Twin!",
    desc: "Your digital twin is alive! Chat naturally — it responds in your voice, with your personality.",
    icon: MessageCircle,
  },
];

const HowItWorksSection = () => {
  return (
    <section id="how-it-works" className="py-28 overflow-hidden">
      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <span className="text-secondary font-body text-sm font-semibold uppercase tracking-widest mb-3 block">How It Works</span>
          <h2 className="font-heading text-4xl md:text-5xl font-bold text-primary-foreground mb-4">
            Four Stages to <span className="italic">Digital Consciousness</span>
          </h2>
        </motion.div>

        <div className="relative max-w-5xl mx-auto">
          {/* Connection line */}
          <div className="hidden lg:block absolute top-24 left-[10%] right-[10%] h-px bg-gradient-to-r from-primary/50 via-accent/50 to-secondary/50" />

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, i) => (
              <motion.div
                key={step.phase}
                className="relative flex flex-col items-center text-center"
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
              >
                <motion.div
                  className="w-20 h-20 rounded-2xl gradient-hero-bg flex items-center justify-center mb-5 relative z-10"
                  whileHover={{ scale: 1.15, rotate: 8 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <step.icon className="w-9 h-9 text-primary-foreground" />
                </motion.div>
                <span className="text-xs font-body font-bold text-primary uppercase tracking-widest mb-1">
                  Phase {step.phase}
                </span>
                <h3 className="font-heading text-xl font-bold text-primary-foreground mb-1">{step.title}</h3>
                <span className="text-sm font-body text-primary-foreground/50 italic mb-3">{step.subtitle}</span>
                <p className="text-primary-foreground/60 font-body text-sm leading-relaxed max-w-[240px]">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
