import { motion } from "framer-motion";
import { ShieldCheck, Lock, Trash2, Eye, ArrowRight } from "lucide-react";

const PrivacyCTASection = () => {
  return (
    <>
      {/* Privacy Section */}
      <section id="about" className="py-28 overflow-hidden">
        <div className="container mx-auto px-6 relative z-10">
          <motion.div
            className="max-w-4xl mx-auto text-center"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <ShieldCheck className="w-16 h-16 text-secondary mx-auto mb-6" />
            <h2 className="font-heading text-4xl md:text-5xl font-bold text-primary-foreground mb-6">
              Your Data. <span className="italic">Your Rules.</span>
            </h2>
            <p className="text-primary-foreground/60 font-body text-lg mb-12 max-w-2xl mx-auto">
              Everything runs on your machine. No cloud. No third-party servers.
            </p>

            <div className="grid sm:grid-cols-3 gap-6 mb-12">
              {[
                { icon: Lock, title: "Encrypted at Rest", desc: "Fernet encryption protects all uploaded files before processing." },
                { icon: Trash2, title: "Auto-Deleted", desc: "Raw files are permanently deleted after RAG indexing." },
                { icon: Eye, title: "Not Human-Readable", desc: "Vector embeddings cannot be reverse-engineered into original data." },
              ].map((item, i) => (
                <motion.div
                  key={item.title}
                  className="glass-dark rounded-2xl p-6 text-center"
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.15 }}
                  whileHover={{ y: -5 }}
                >
                  <item.icon className="w-10 h-10 text-primary mx-auto mb-4" />
                  <h3 className="font-heading text-lg font-semibold text-primary-foreground mb-2">{item.title}</h3>
                  <p className="text-primary-foreground/60 font-body text-sm">{item.desc}</p>
                </motion.div>
              ))}
            </div>

            {/* Data lifecycle */}
            <motion.div
              className="glass-dark rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-center gap-4 text-sm font-body"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
            >
              <span className="bg-primary/20 text-primary px-4 py-2 rounded-full font-medium">Upload</span>
              <span className="text-primary-foreground/30">→</span>
              <span className="bg-secondary/20 text-secondary px-4 py-2 rounded-full font-medium">Encrypt</span>
              <span className="text-primary-foreground/30">→</span>
              <span className="bg-accent/20 text-accent px-4 py-2 rounded-full font-medium">RAG Index</span>
              <span className="text-primary-foreground/30">→</span>
              <span className="bg-destructive/20 text-destructive px-4 py-2 rounded-full font-medium">Delete Raw 🗑️</span>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 gradient-hero-bg opacity-20" />
        <motion.div
          className="container mx-auto px-6 text-center relative z-10"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="font-heading text-4xl md:text-6xl font-bold text-primary-foreground mb-4 italic">
            Ready to Meet Yourself?
          </h2>
          <p className="text-primary-foreground/60 font-body text-lg mb-8 max-w-xl mx-auto">
            Total Cost: ₹0 · Everything Runs Locally · Zero External Dependencies
          </p>
          <motion.button
            className="gradient-hero-bg text-primary-foreground font-body font-semibold px-10 py-4 rounded-xl text-lg flex items-center gap-2 mx-auto"
            whileHover={{ scale: 1.05, boxShadow: "0 0 40px hsla(199, 89%, 48%, 0.5)" }}
            whileTap={{ scale: 0.95 }}
          >
            Begin the Imprint Process <ArrowRight className="w-5 h-5" />
          </motion.button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-primary-foreground/10 relative z-10">
        <div className="container mx-auto px-6 text-center">
          <h3 className="font-heading text-2xl font-bold text-primary-foreground italic mb-2">Alternate Ego</h3>
          <p className="text-primary-foreground/50 font-body text-sm mb-4">
            Your AI-Powered Digital Twin
          </p>
          <div className="flex items-center justify-center gap-6 text-xs text-primary-foreground/40 font-body">
            <span>🔒 Privacy First</span>
            <span>•</span>
            <span>₹0 Cost</span>
            <span>•</span>
            <span>100% Local</span>
          </div>
          <p className="text-primary-foreground/20 font-body text-xs mt-6">
            Inspired by Ego — 3rd Place, Cursor × Smithery Hackathon, Singapore
          </p>
        </div>
      </footer>
    </>
  );
};

export default PrivacyCTASection;
