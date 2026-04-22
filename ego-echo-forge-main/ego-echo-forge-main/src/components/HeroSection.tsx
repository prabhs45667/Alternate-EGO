import { motion } from "framer-motion";
import FaceRecognition3D from "./FaceRecognition3D";
import { ArrowRight, Sparkles } from "lucide-react";

const HeroSection = () => {
  return (
    <section id="home" className="relative min-h-screen flex items-center pt-20">
      <div className="relative z-10 container mx-auto px-6 py-20 grid lg:grid-cols-2 gap-12 items-center">
        {/* Left - Text content */}
        <motion.div
          className="flex flex-col items-center lg:items-start text-center lg:text-left"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <motion.div
            className="glass-dark inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Sparkles className="w-4 h-4 text-secondary" />
            <span className="text-primary-foreground/80 text-xs font-body font-medium uppercase tracking-widest">
              AI-Powered Digital Twin
            </span>
          </motion.div>

          <h1 className="font-heading text-5xl md:text-7xl lg:text-8xl italic font-bold text-primary-foreground leading-[0.95] mb-6">
            Alternate
            <br />
            <span className="gradient-text">Ego</span>
          </h1>

          <p className="text-primary-foreground/70 font-body text-lg md:text-xl max-w-lg leading-relaxed mb-4">
            Your hyper-realistic digital twin that <em>thinks</em>, <em>speaks</em>, and <em>responds</em> like you — powered by your social data, voice, and personality.
          </p>

          <p className="text-primary-foreground/50 font-body text-sm mb-8">
            Running 100% locally at zero cost. No cloud. No API keys. No compromises.
          </p>

          <div className="flex flex-col sm:flex-row gap-4">
            <motion.button
              className="gradient-hero-bg text-primary-foreground font-body font-semibold px-8 py-4 rounded-xl flex items-center justify-center gap-2 text-base"
              whileHover={{ scale: 1.05, boxShadow: "0 0 40px hsla(199, 89%, 48%, 0.4)" }}
              whileTap={{ scale: 0.95 }}
            >
              Begin the Imprint <ArrowRight className="w-5 h-5" />
            </motion.button>
            <motion.button
              className="glass text-primary-foreground font-body font-medium px-8 py-4 rounded-xl text-base hover:bg-primary-foreground/10 transition-colors"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              Watch Demo
            </motion.button>
          </div>

          {/* Stats */}
          <div className="flex gap-8 mt-10">
            {[
              { value: "₹0", label: "Total Cost" },
              { value: "100%", label: "Local" },
              { value: "9", label: "Voice Questions" },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="font-heading text-2xl font-bold text-primary-foreground">{stat.value}</div>
                <div className="text-primary-foreground/50 font-body text-xs uppercase tracking-wider">{stat.label}</div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Right - 3D Face */}
        <motion.div
          className="flex justify-center"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, delay: 0.5 }}
        >
          <div className="relative">
            {/* Glow behind face */}
            <div className="absolute inset-0 bg-primary/20 rounded-full blur-[80px] pulse-glow" />
            <FaceRecognition3D />

            {/* Floating labels */}
            <motion.div
              className="absolute top-4 right-0 glass-dark px-3 py-1.5 rounded-full"
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              <span className="text-secondary text-xs font-body font-medium">🧠 RAG Brain</span>
            </motion.div>
            <motion.div
              className="absolute bottom-12 left-0 glass-dark px-3 py-1.5 rounded-full"
              animate={{ y: [0, 8, 0] }}
              transition={{ duration: 3.5, repeat: Infinity, delay: 0.5 }}
            >
              <span className="text-primary text-xs font-body font-medium">🎤 Voice Clone</span>
            </motion.div>
            <motion.div
              className="absolute bottom-4 right-4 glass-dark px-3 py-1.5 rounded-full"
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 4, repeat: Infinity, delay: 1 }}
            >
              <span className="text-accent text-xs font-body font-medium">🔒 Privacy First</span>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;
