import { motion } from "framer-motion";
import { ArrowRightLeft } from "lucide-react";

const replacements = [
  { original: "OpenAI Embeddings", replacement: "nomic-embed-text (Ollama)", reason: "Local, 768-dim, ₹0" },
  { original: "Claude / GPT-4", replacement: "llama3.1:8b (Ollama)", reason: "Local LLM, no API key" },
  { original: "ElevenLabs Voice", replacement: "Coqui XTTS v2", reason: "Open-source voice cloning" },
  { original: "Whisper Cloud API", replacement: "faster-whisper (CPU)", reason: "STT on your machine" },
  { original: "ChromaDB + hnswlib", replacement: "Pure Python JSON Store", reason: "Zero DLL dependencies" },
  { original: "Supabase PostgreSQL", replacement: "SQLite (local)", reason: "File-based, zero setup" },
  { original: "EXA AI Scraping", replacement: "BeautifulSoup + DDG", reason: "No API key needed" },
  { original: "Nano Banana 2", replacement: "face-api.js (browser CV)", reason: "Client-side emotions" },
];

const TechStackSection = () => {
  return (
    <section className="py-28 overflow-hidden">
      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <span className="text-secondary font-body text-sm font-semibold uppercase tracking-widest mb-3 block">Zero Cost Stack</span>
          <h2 className="font-heading text-4xl md:text-5xl font-bold text-primary-foreground mb-4">
            The <span className="italic">₹0 Stack</span>
          </h2>
          <p className="text-primary-foreground/60 font-body text-lg max-w-2xl mx-auto">
            Every paid API replaced with a free, local alternative.
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto grid gap-3">
          <div className="grid grid-cols-[1fr_auto_1fr_1fr] gap-4 px-5 py-3">
            <span className="text-xs font-body font-bold text-destructive uppercase tracking-wider">Original (Paid)</span>
            <span />
            <span className="text-xs font-body font-bold text-secondary uppercase tracking-wider">Our Replacement</span>
            <span className="text-xs font-body font-bold text-primary-foreground/40 uppercase tracking-wider hidden sm:block">Why</span>
          </div>

          {replacements.map((row, i) => (
            <motion.div
              key={row.original}
              className="grid grid-cols-[1fr_auto_1fr] sm:grid-cols-[1fr_auto_1fr_1fr] gap-4 glass-dark rounded-xl px-5 py-4 items-center"
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              whileHover={{ scale: 1.02 }}
            >
              <span className="font-body text-sm text-primary-foreground/50 line-through">{row.original}</span>
              <ArrowRightLeft className="w-4 h-4 text-primary flex-shrink-0" />
              <span className="font-body text-sm font-semibold text-primary-foreground">{row.replacement}</span>
              <span className="font-body text-xs text-primary-foreground/40 hidden sm:block">{row.reason}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TechStackSection;
