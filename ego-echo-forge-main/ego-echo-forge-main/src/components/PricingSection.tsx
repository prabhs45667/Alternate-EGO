import { motion } from "framer-motion";
import { Check, Sparkles, Zap, Crown } from "lucide-react";

const plans = [
  {
    name: "Personal",
    price: "₹0",
    period: "Forever Free",
    desc: "Everything you need for your personal digital twin.",
    icon: Zap,
    features: [
      "1 Digital Twin",
      "RAG-powered personality",
      "Voice cloning (Coqui XTTS v2)",
      "4 emotion avatar photos",
      "9 voice interview questions",
      "Social media scraping",
      "100% local processing",
      "Full data encryption",
    ],
    cta: "Get Started Free",
    highlighted: false,
  },
  {
    name: "Pro",
    price: "₹0",
    period: "Open Source",
    desc: "Advanced features for power users and developers.",
    icon: Sparkles,
    features: [
      "Everything in Personal",
      "Multiple twin profiles",
      "Custom LLM models",
      "API access & integrations",
      "Advanced personality extraction",
      "Real-time voice chat",
      "Social media automation",
      "Priority community support",
    ],
    cta: "Clone the Repo",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "Contact Us",
    desc: "For organizations preserving institutional knowledge.",
    icon: Crown,
    features: [
      "Everything in Pro",
      "On-premise deployment",
      "Team knowledge twins",
      "Custom model fine-tuning",
      "Federated learning support",
      "Enterprise security audit",
      "SLA & dedicated support",
      "White-label options",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
];

const PricingSection = () => {
  return (
    <section id="pricing" className="py-28 overflow-hidden">
      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <span className="text-secondary font-body text-sm font-semibold uppercase tracking-widest mb-3 block">Pricing</span>
          <h2 className="font-heading text-4xl md:text-5xl font-bold text-primary-foreground mb-4">
            Zero Cost. <span className="italic">Maximum Value.</span>
          </h2>
          <p className="text-primary-foreground/60 font-body text-lg max-w-xl mx-auto">
            Alternate Ego is open source. Your digital twin costs nothing to create.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              className={`relative rounded-2xl p-7 flex flex-col ${
                plan.highlighted
                  ? "glass border-2 border-primary/40 glow-primary"
                  : "glass-dark"
              }`}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              whileHover={{ y: -5 }}
            >
              {plan.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 gradient-hero-bg text-primary-foreground text-xs font-body font-semibold px-4 py-1 rounded-full">
                  Most Popular
                </div>
              )}

              <plan.icon className="w-8 h-8 text-primary mb-4" />
              <h3 className="font-heading text-xl font-bold text-primary-foreground">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mt-2 mb-1">
                <span className="font-heading text-4xl font-bold text-primary-foreground">{plan.price}</span>
                <span className="text-primary-foreground/40 font-body text-sm">/ {plan.period}</span>
              </div>
              <p className="text-primary-foreground/50 font-body text-sm mb-6">{plan.desc}</p>

              <ul className="space-y-3 mb-8 flex-1">
                {plan.features.map((feat) => (
                  <li key={feat} className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-secondary flex-shrink-0 mt-0.5" />
                    <span className="text-primary-foreground/70 font-body text-sm">{feat}</span>
                  </li>
                ))}
              </ul>

              <motion.button
                className={`w-full py-3 rounded-xl font-body font-semibold text-sm ${
                  plan.highlighted
                    ? "gradient-hero-bg text-primary-foreground"
                    : "bg-primary-foreground/10 text-primary-foreground hover:bg-primary-foreground/20"
                } transition-colors`}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
              >
                {plan.cta}
              </motion.button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default PricingSection;
