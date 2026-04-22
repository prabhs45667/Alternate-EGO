import { motion } from "framer-motion";
import { Brain, Mic, Camera, MessageSquare, Shield, Cpu, Zap, Globe } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "RAG-Powered Brain",
    desc: "Topic-based chunking + cosine similarity search creates a memory that truly knows you.",
    gradient: "from-primary to-secondary",
  },
  {
    icon: Mic,
    title: "Voice Cloning",
    desc: "Coqui XTTS v2 clones your voice from 9 interview answers. Your twin speaks like you.",
    gradient: "from-accent to-primary",
  },
  {
    icon: Camera,
    title: "Emotion-Aware Avatar",
    desc: "4 emotion photos + face-api.js create an avatar that reacts with your expressions.",
    gradient: "from-secondary to-accent",
  },
  {
    icon: MessageSquare,
    title: "Personality Chat",
    desc: "First-person responses with RAG source citations. Your twin answers as you would.",
    gradient: "from-primary to-accent",
  },
  {
    icon: Shield,
    title: "Privacy First",
    desc: "Fernet encryption, auto-deletion of raw files. Only embeddings remain.",
    gradient: "from-secondary to-primary",
  },
  {
    icon: Cpu,
    title: "100% Local",
    desc: "Ollama LLM + embeddings, faster-whisper STT, SQLite DB. Zero cloud dependencies.",
    gradient: "from-accent to-secondary",
  },
  {
    icon: Zap,
    title: "₹0 Total Cost",
    desc: "Every paid API replaced with a free, local alternative. No subscriptions needed.",
    gradient: "from-primary to-secondary",
  },
  {
    icon: Globe,
    title: "Social Intelligence",
    desc: "Scrapes your public profiles to feed your twin's knowledge base automatically.",
    gradient: "from-accent to-primary",
  },
];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

const FeaturesSection = () => {
  return (
    <section id="features" className="relative py-28 overflow-hidden">
      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <span className="text-secondary font-body text-sm font-semibold uppercase tracking-widest mb-3 block">Features</span>
          <h2 className="font-heading text-4xl md:text-5xl font-bold text-primary-foreground mb-4">
            Everything You Need to <span className="italic">Clone Yourself</span>
          </h2>
          <p className="text-primary-foreground/60 font-body max-w-2xl mx-auto text-lg">
            Voice, face, memory, and personality — running entirely on your machine.
          </p>
        </motion.div>

        <motion.div
          className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5"
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
        >
          {features.map((feat) => (
            <motion.div
              key={feat.title}
              className="group glass-dark rounded-2xl p-6 hover:border-primary/30 transition-all duration-300"
              variants={item}
              whileHover={{ y: -8, scale: 1.02 }}
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feat.gradient} flex items-center justify-center mb-4`}>
                <feat.icon className="w-6 h-6 text-primary-foreground" />
              </div>
              <h3 className="font-heading text-lg font-semibold text-primary-foreground mb-2">{feat.title}</h3>
              <p className="text-primary-foreground/60 font-body text-sm leading-relaxed">{feat.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default FeaturesSection;
