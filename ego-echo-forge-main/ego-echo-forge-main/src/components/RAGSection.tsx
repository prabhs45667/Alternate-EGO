import { motion } from "framer-motion";
import brainGlow from "@/assets/brain-glow.png";

const pipeline = [
  { label: "Data Sources", items: ["Social Scrapes", "Voice Transcripts ×9", "Data Exports"], color: "border-primary" },
  { label: "Topic Chunker", items: ["Semantic splitting", "Source metadata"], color: "border-secondary" },
  { label: "Ollama Embedder", items: ["nomic-embed-text", "768-dim vectors"], color: "border-accent" },
  { label: "JSON Vector Store", items: ["Cosine similarity", "Pure Python"], color: "border-primary" },
  { label: "LLM Response", items: ["llama3.1:8b", "First-person reply", "Citations"], color: "border-secondary" },
];

const RAGSection = () => {
  return (
    <section id="technology" className="py-28 overflow-hidden">
      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <span className="text-secondary font-body text-sm font-semibold uppercase tracking-widest mb-3 block">Technology</span>
          <h2 className="font-heading text-4xl md:text-5xl font-bold text-primary-foreground mb-4">
            The <span className="italic">RAG Brain</span> Pipeline
          </h2>
          <p className="text-primary-foreground/60 font-body text-lg max-w-2xl mx-auto">
            What makes your twin actually <em>know</em> you.
          </p>
        </motion.div>

        <div className="flex flex-col lg:flex-row items-center gap-12">
          <motion.div
            className="flex-shrink-0"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            <motion.img
              src={brainGlow}
              alt="AI Brain Neural Network"
              className="w-56 h-56 md:w-72 md:h-72 drop-shadow-[0_0_30px_rgba(14,165,233,0.4)]"
              width={512}
              height={512}
              animate={{ y: [0, -15, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            />
          </motion.div>

          <div className="flex-1 space-y-4 w-full">
            {pipeline.map((step, i) => (
              <motion.div
                key={step.label}
                className={`glass-dark rounded-xl p-5 border-l-4 ${step.color} flex flex-col sm:flex-row sm:items-center gap-3`}
                initial={{ opacity: 0, x: 40 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                whileHover={{ x: 8 }}
              >
                <div className="flex items-center gap-3 min-w-[160px]">
                  <span className="text-xs font-body font-bold text-primary-foreground/40">0{i + 1}</span>
                  <h4 className="font-heading text-base font-semibold text-primary-foreground">{step.label}</h4>
                </div>
                <div className="flex flex-wrap gap-2">
                  {step.items.map((item) => (
                    <span
                      key={item}
                      className="text-xs font-body bg-primary-foreground/10 text-primary-foreground/70 px-3 py-1 rounded-full"
                    >
                      {item}
                    </span>
                  ))}
                </div>
                {i < pipeline.length - 1 && (
                  <span className="hidden sm:block ml-auto text-primary-foreground/30">→</span>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default RAGSection;
