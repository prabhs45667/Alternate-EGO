"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { register } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setTimeout(() => setMounted(true), 50);
    const token = localStorage.getItem("ego_token");
    if (token) router.push("/chat");
  }, [router]);

  const handleSignup = async () => {
    if (!email.trim() || !password) {
      setError("Please enter your email and password");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const result = await register(email.trim(), password);
      localStorage.setItem("ego_token", result.token);
      localStorage.setItem("ego_account", JSON.stringify({
        account_id: result.account_id,
        email: result.email,
        user_id: result.user_id,
        twin_id: result.twin_id,
        has_twin: false,
      }));
      router.push("/upload");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
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
            <p className="ego-subtitle">CREATE ACCOUNT</p>
          </div>

          {error && (
            <div style={{ marginBottom: 16, padding: "10px 16px", background: "rgba(248,113,113,0.12)", border: "1px solid rgba(248,113,113,0.3)", borderRadius: 10, color: "#f87171", fontSize: 14 }}>
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
              autoComplete="email"
            />
          </div>

          <div className="input-group" style={{ marginTop: 12 }}>
            <input
              type="password"
              className="input-glass"
              placeholder="Password (min. 6 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
            />
          </div>

          <div className="input-group" style={{ marginTop: 12 }}>
            <input
              type="password"
              className="input-glass"
              placeholder="Confirm password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSignup()}
              autoComplete="new-password"
            />
          </div>

          <button
            className="submit-btn"
            onClick={handleSignup}
            disabled={loading}
            style={{ marginTop: 24, width: "100%" }}
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>

          <div style={{ textAlign: "center", marginTop: 20, color: "var(--text-muted)", fontSize: 14 }}>
            Already have an account?{" "}
            <a
              href="/login"
              style={{ color: "var(--primary-light)", textDecoration: "none", fontWeight: 600 }}
            >
              Sign In
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
