"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { linkTwin, startOnboarding, uploadDataExport } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [gender, setGender] = useState("male");
  const [linkedin, setLinkedin] = useState("");
  const [instagram, setInstagram] = useState("");
  const [twitter, setTwitter] = useState("");
  const [facebook, setFacebook] = useState("");
  const [otherUrls, setOtherUrls] = useState<string[]>([""]);
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dataFiles, setDataFiles] = useState<File[]>([]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(t);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setDataFiles((prev) => [...prev, ...newFiles]);
      e.target.value = "";
    }
  };

  const handleAddOtherUrl = () => {
    setOtherUrls((prev) => [...prev, ""]);
  };

  const handleOtherUrlChange = (index: number, value: string) => {
    const nextUrls = [...otherUrls];
    nextUrls[index] = value;
    setOtherUrls(nextUrls);
  };

  const handleRemoveOtherUrl = (index: number) => {
    if (otherUrls.length > 1) {
      setOtherUrls((prev) => prev.filter((_, i) => i !== index));
      return;
    }
    setOtherUrls([""]);
  };

  const handleRemoveFile = (index: number) => {
    setDataFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (!name.trim()) {
      setError("Please enter your name");
      return;
    }
    if (!consent) {
      setError("Please accept the privacy consent");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await startOnboarding({
        name: name.trim(),
        linkedin_url: linkedin.trim(),
        instagram_url: instagram.trim(),
        twitter_url: twitter.trim(),
        facebook_url: facebook.trim(),
        other_url: otherUrls.map((url) => url.trim()).filter(Boolean).join(","),
        email: email.trim(),
        phone: phone.trim(),
        gender,
      });

      if (dataFiles.length > 0) {
        for (const file of dataFiles) {
          uploadDataExport(result.twin_id, result.session_id, file).catch((uploadError) => {
            console.warn(`Background upload failed: ${file.name}`, uploadError);
          });
        }
      }

      localStorage.setItem(
        "ego_session",
        JSON.stringify({
          user_id: result.user_id,
          twin_id: result.twin_id,
          session_id: result.session_id,
          name: name.trim(),
          gender,
          linkedin_url: linkedin.trim(),
          instagram_url: instagram.trim(),
          twitter_url: twitter.trim(),
          facebook_url: facebook.trim(),
          other_url: otherUrls.map((url) => url.trim()).filter(Boolean).join(","),
          email: email.trim(),
          phone: phone.trim(),
          data_files: dataFiles.map((file) => file.name),
        })
      );

      if (dataFiles.length > 0) {
        localStorage.setItem("ego_has_data_file", "true");
      }

      try {
        await linkTwin(result.user_id, result.twin_id);
        const acct = localStorage.getItem("ego_account");
        if (acct) {
          const parsed = JSON.parse(acct);
          parsed.user_id = result.user_id;
          parsed.twin_id = result.twin_id;
          localStorage.setItem("ego_account", JSON.stringify(parsed));
        }
      } catch {
        // Linking auth state is non-fatal for onboarding.
      }

      router.push("/onboarding");
    } catch (err) {
      setError("Failed to connect to backend. Is the server running on port 8000?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="form-bg" />
      <div className="form-bg-overlay" />

      <div className={`upload-form-container ${mounted ? "upload-visible" : ""}`}>
        <div className="form-card">
          <div className="text-center">
            <h1 className="ego-title">Alternate Ego</h1>
            <p className="ego-subtitle">UPLOAD YOURSELF</p>
          </div>

          <div className="input-group">
            <input
              id="name-input"
              type="text"
              className="input-glass"
              placeholder="Enter your full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            />
          </div>

          <span className="social-inputs-label">GENDER</span>
          <div className="input-group" style={{ display: "flex", gap: "10px", marginBottom: "8px" }}>
            {[
              { value: "male", label: "Male" },
              { value: "female", label: "Female" },
              { value: "trans", label: "Trans" },
            ].map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setGender(option.value)}
                style={{
                  flex: 1,
                  padding: "10px 0",
                  borderRadius: "12px",
                  border: gender === option.value ? "2px solid #8b5cf6" : "2px solid rgba(255,255,255,0.12)",
                  background: gender === option.value ? "rgba(139,92,246,0.2)" : "rgba(255,255,255,0.05)",
                  color: gender === option.value ? "#c4b5fd" : "rgba(255,255,255,0.5)",
                  fontSize: "0.9rem",
                  fontWeight: gender === option.value ? 600 : 400,
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  backdropFilter: "blur(8px)",
                }}
              >
                {option.label}
              </button>
            ))}
          </div>

          <span className="social-inputs-label">SOCIAL PROFILES (OPTIONAL)</span>

          <div className="social-grid">
            <div className="social-input-row">
              <span className="social-icon">💼</span>
              <input className="input-glass" placeholder="LinkedIn URL" value={linkedin} onChange={(e) => setLinkedin(e.target.value)} />
            </div>
            <div className="social-input-row">
              <span className="social-icon">📸</span>
              <input className="input-glass" placeholder="Instagram URL or @handle" value={instagram} onChange={(e) => setInstagram(e.target.value)} />
            </div>
            <div className="social-input-row">
              <span className="social-icon">🐦</span>
              <input className="input-glass" placeholder="Twitter/X URL or @handle" value={twitter} onChange={(e) => setTwitter(e.target.value)} />
            </div>
            <div className="social-input-row">
              <span className="social-icon">📘</span>
              <input className="input-glass" placeholder="Facebook URL" value={facebook} onChange={(e) => setFacebook(e.target.value)} />
            </div>
            {otherUrls.map((url, index) => (
              <div key={`other-url-${index}`} className="social-input-row" style={{ gridColumn: "1 / -1", display: "flex", gap: "8px" }}>
                <span className="social-icon">🔗</span>
                <input
                  className="input-glass flex-grow"
                  placeholder="Any other URL (Portfolio, TikTok, Blog, GitHub...)"
                  value={url}
                  onChange={(e) => handleOtherUrlChange(index, e.target.value)}
                />
                {index === otherUrls.length - 1 ? (
                  <button
                    onClick={handleAddOtherUrl}
                    className="flex items-center justify-center w-10 h-10 rounded-full bg-purple-600/50 text-white hover:bg-purple-600/80 transition-colors"
                    title="Add another URL"
                  >
                    +
                  </button>
                ) : (
                  <button
                    onClick={() => handleRemoveOtherUrl(index)}
                    className="flex items-center justify-center w-10 h-10 rounded-full bg-red-500/30 text-white hover:bg-red-500/60 transition-colors"
                    title="Remove URL"
                  >
                    x
                  </button>
                )}
              </div>
            ))}
          </div>

          <span className="social-inputs-label mt-4">CONTACT INFO (OPTIONAL)</span>

          <div className="social-grid">
            <div className="social-input-row">
              <span className="social-icon">📧</span>
              <input className="input-glass" placeholder="Email address" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className="social-input-row">
              <span className="social-icon">📱</span>
              <input className="input-glass" placeholder="Phone number" type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>
          </div>

          <span className="social-inputs-label mt-section">DATA EXPORT ZIP (OPTIONAL)</span>

          <div className="input-group">
            <label className="file-upload-zone">
              <span>📁 Click to add files (.zip, .json, .csv, .txt)</span>
              <input type="file" accept=".zip,.json,.txt,.csv" multiple onChange={handleFileChange} />
            </label>
            {dataFiles.length > 0 && (
              <div className="file-list">
                {dataFiles.map((file, index) => (
                  <div key={`${file.name}-${index}`} className="file-list-item">
                    <div className="file-list-item-info">
                      <span className="file-list-item-icon">📦</span>
                      <span className="file-list-item-name">{file.name}</span>
                      <span className="file-list-item-size">{(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                    <button onClick={() => handleRemoveFile(index)} className="file-remove-btn" title="Remove file">
                      ✕
                    </button>
                  </div>
                ))}
                <div className="file-upload-count">
                  {dataFiles.length} file{dataFiles.length > 1 ? "s" : ""} selected
                </div>
              </div>
            )}
          </div>

          <div className="privacy-box">
            <h3 className="privacy-title">
              <span>🛡️</span> Your Privacy is Protected
            </h3>
            <ul className="privacy-list">
              <li>Your data is encrypted and processed locally on your device</li>
              <li>We never share your data with anyone</li>
              <li>Raw files are deleted automatically after processing</li>
              <li>You can delete all your data at any time</li>
            </ul>
          </div>

          <label className="consent-wrapper">
            <input type="checkbox" className="consent-checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
            <span className="consent-label">I consent to the processing of my data</span>
          </label>

          {error && <p className="error-text">{error}</p>}

          <button className="upload-btn" onClick={handleSubmit} disabled={loading || !name.trim() || !consent}>
            {loading ? <div className="spinner" /> : "UPLOAD YOURSELF ➔"}
          </button>
        </div>
      </div>
    </div>
  );
}
