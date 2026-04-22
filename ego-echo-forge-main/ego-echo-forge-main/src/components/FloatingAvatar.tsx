import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import avatar1 from "@/assets/avatar-1.png";
import avatar2 from "@/assets/avatar-2.png";
import avatar3 from "@/assets/avatar-3.png";

const avatars = [avatar1, avatar2, avatar3];

const FloatingAvatar = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % avatars.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative w-56 h-56 md:w-72 md:h-72">
      {/* Orbital particles */}
      <div className="absolute inset-0">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 rounded-full bg-primary"
            style={{
              top: "50%",
              left: "50%",
              opacity: 0.6,
            }}
            animate={{
              rotate: 360,
            }}
            transition={{
              duration: 8 + i * 2,
              repeat: Infinity,
              ease: "linear",
              delay: i * 0.5,
            }}
          >
            <motion.div
              className="w-2 h-2 rounded-full"
              style={{
                background: i % 2 === 0 ? "hsl(199, 89%, 48%)" : "hsl(262, 60%, 55%)",
                transform: `translateX(${100 + i * 15}px)`,
              }}
              animate={{ scale: [1, 1.5, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: i * 0.3 }}
            />
          </motion.div>
        ))}
      </div>

      {/* Glow rings */}
      <motion.div
        className="absolute inset-[-12px] rounded-full border-2 border-primary/30"
        animate={{ scale: [1, 1.05, 1], opacity: [0.3, 0.6, 0.3] }}
        transition={{ duration: 3, repeat: Infinity }}
      />
      <motion.div
        className="absolute inset-[-24px] rounded-full border border-accent/20"
        animate={{ scale: [1, 1.08, 1], opacity: [0.2, 0.4, 0.2] }}
        transition={{ duration: 4, repeat: Infinity, delay: 0.5 }}
      />

      {/* Avatar circle with face swap */}
      <div className="relative w-full h-full rounded-full overflow-hidden border-4 border-primary/40 glow-primary">
        <AnimatePresence mode="wait">
          <motion.img
            key={currentIndex}
            src={avatars[currentIndex]}
            alt="Digital Twin Avatar"
            className="w-full h-full object-cover"
            initial={{ rotateY: 90, opacity: 0 }}
            animate={{ rotateY: 0, opacity: 1 }}
            exit={{ rotateY: -90, opacity: 0 }}
            transition={{ duration: 0.6, ease: "easeInOut" }}
          />
        </AnimatePresence>
      </div>

      {/* Label */}
      <motion.div
        className="absolute -bottom-6 left-1/2 -translate-x-1/2 glass-dark px-4 py-1.5 rounded-full"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
      >
        <span className="text-primary-foreground text-xs font-body font-medium tracking-wider uppercase">
          Your Digital Twin
        </span>
      </motion.div>
    </div>
  );
};

export default FloatingAvatar;
