"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function LandingPage() {
  const router = useRouter();

  useEffect(() => {
    // If already authenticated, go to chat; otherwise show the hero
    const token = localStorage.getItem("ego_token");
    if (token) router.replace("/chat");
  }, [router]);

  const handleContinue = () => {
    const token = localStorage.getItem("ego_token");
    router.push(token ? "/chat" : "/login");
  };

  return (
    <div className="landing-wrapper">
      {/* ── HERO VIDEO — full screen, click to go to /login ── */}
      <section className="hero-section" id="hero" onClick={handleContinue}>
        <video
          className="hero-video"
          src="/hero-video.mp4"
          autoPlay
          loop
          muted
          playsInline
        />
        {/* Click hint at bottom */}
        <div className="click-hint">
          <div className="click-hint-pulse" />
          <span>Click anywhere to continue</span>
        </div>
      </section>
    </div>
  );
}

