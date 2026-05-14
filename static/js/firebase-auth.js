// ─────────────────────────────────────────────────────────────
// Firebase Authentication (Google Sign-in) — BoardGame AI
// แบบเดียวกับ ig342 BeatdownPWA
// ─────────────────────────────────────────────────────────────
// ⚠️ กรอก firebaseConfig จาก Firebase Console ของคุณ:
//    Firebase Console > Project Settings > Your apps > Web > Config
// ─────────────────────────────────────────────────────────────
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
  onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/10.7.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyDxSYqNsQJ8so7u2vffsfieWzriWaBEd7Q",
  authDomain: "ig342-f1cc4.firebaseapp.com",
  projectId: "ig342-f1cc4",
  storageBucket: "ig342-f1cc4.firebasestorage.app",
  messagingSenderId: "520882963925",
  appId: "1:520882963925:web:495843322049a46eeda95c",
  measurementId: "G-CTQ9CLQ34K",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

// ─── เข้าสู่ระบบด้วย Google ───────────────────────────────
window.firebaseLogin = async function () {
  const btn = document.getElementById("googleBtn");
  if (btn) { btn.disabled = true; btn.textContent = "⏳ กำลังเข้าสู่ระบบ..."; }
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const idToken = await result.user.getIdToken();

    // ส่ง ID token ให้ FastAPI verify แล้วออก JWT ของระบบเรา
    const res = await fetch("/api/v1/auth/firebase-login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ id_token: idToken }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Firebase login failed");

    localStorage.setItem("token", data.access_token);
    window.location = "/dashboard";
  } catch (err) {
    console.error("[firebase] login error:", err);
    const el = document.getElementById("err");
    if (el) {
      el.textContent = "Google login: " + (err.message || err);
      el.classList.remove("hidden");
    }
    if (btn) { btn.disabled = false; btn.innerHTML = '<span>🔑</span> เข้าสู่ระบบด้วย Google'; }
  }
};

// ─── ออกจากระบบ Firebase ──────────────────────────────────
window.firebaseLogout = async function () {
  try { await signOut(auth); } catch (e) { console.warn(e); }
};

console.log("[Firebase] auth module loaded");
