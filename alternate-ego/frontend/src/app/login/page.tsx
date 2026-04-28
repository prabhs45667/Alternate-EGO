"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setTimeout(() => setMounted(true), 50);
    // If already logged in, redirect
    const token = localStorage.getItem("ego_token");
    if (token) router.push("/chat");
  }, [router]);

  const handleLogin = async () => {
    if (!email.trim() || !password) {
      setError("Please enter your email and password");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const result = await login(email.trim(), password);
      localStorage.setItem("ego_token", result.token);
      localStorage.setItem("ego_account", JSON.stringify({
        account_id: result.account_id,
        email: result.email,
        user_id: result.user_id,
        twin_id: result.twin_id,
        has_twin: result.has_twin,
      }));

      // Restore ego_session so existing pages work
      if (result.user_id && result.twin_id) {
        const existing = localStorage.getItem("ego_session");
        if (!existing) {
          localStorage.setItem("ego_session", JSON.stringify({
            user_id: result.user_id,
            twin_id: result.twin_id,
            session_id: "",
            name: result.email.split("@")[0],
          }));
        }
        const status = result.twin_status || "";
        if (result.has_twin || status === "active") {
          router.push("/chat");
        } else if (status === "creating") {
          router.push("/onboarding");
        } else {
          router.push("/upload");
        }
      } else {
        router.push("/upload");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="form-bg" />
      <div className="form-bg-overlay" />

      <div className={`upload-form-container ${mounted ? "upload-visible" : ""}`}>
        <div className="form-card" style={{ maxWidth: 420 }}>
          <div className="text-center" style={{ marginBottom: 32 }}>
            <h1 className="ego-title">Alternate Ego</h1>
            <p className="ego-subtitle">SIGN IN</p>
          </div>

          {error && (
            <div className="error-banner" style={{ marginBottom: 16, padding: "10px 16px", background: "rgba(248,113,113,0.12)", border: "1px solid rgba(248,113,113,0.3)", borderRadius: 10, color: "#f87171", fontSize: 14 }}>
              {error}
            </div>
          )}

          <div className="input-group">
            <input
              type="email"
              className="input-glass"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleLogin()}
              autoComplete="email"
            />
          </div>

          <div className="input-group" style={{ marginTop: 12 }}>
            <input
              type="password"
              className="input-glass"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleLogin()}
              autoComplete="current-password"
            />
          </div>

          <button
            className="submit-btn"
            onClick={handleLogin}
            disabled={loading}
            style={{ marginTop: 24, width: "100%" }}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>

          <div style={{ textAlign: "center", marginTop: 20, color: "var(--text-muted)", fontSize: 14 }}>
            Don&apos;t have an account?{" "}
            <a
              href="/signup"
              style={{ color: "var(--primary-light)", textDecoration: "none", fontWeight: 600 }}
            >
              Sign Up
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
