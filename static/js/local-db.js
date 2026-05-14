// ─────────────────────────────────────────────────────────────
// Local Database (IndexedDB) — BoardGame AI
// ใช้ Dexie.js wrapper (เหมือน ig342 BeatdownDB)
// ─────────────────────────────────────────────────────────────
// เก็บ:
//  1. ai_cache    — แคชคำตอบ AI (ลด Groq API call + เร็วขึ้น)
//  2. searches    — ประวัติคำค้นหา 10 รายการล่าสุด
//  3. drafts      — ข้อความที่พิมพ์ค้างไว้ (กันลืม)
// ─────────────────────────────────────────────────────────────

const DB_NAME = "BoardGameAI_DB";
const DB_VERSION = 1;

let _db = null;
function openDB() {
  if (_db) return Promise.resolve(_db);
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains("ai_cache")) {
        db.createObjectStore("ai_cache", { keyPath: "key" });
      }
      if (!db.objectStoreNames.contains("searches")) {
        db.createObjectStore("searches", { keyPath: "id", autoIncrement: true });
      }
      if (!db.objectStoreNames.contains("drafts")) {
        db.createObjectStore("drafts", { keyPath: "game_id" });
      }
    };
    req.onsuccess = () => { _db = req.result; resolve(_db); };
    req.onerror   = () => reject(req.error);
  });
}

function tx(store, mode = "readonly") {
  return openDB().then(db => db.transaction(store, mode).objectStore(store));
}

// ─── AI Response Cache ────────────────────────────────────────
async function hashKey(gameId, question) {
  const data = new TextEncoder().encode(`${gameId}::${question.trim().toLowerCase()}`);
  const buf = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");
}

window.AICache = {
  async get(gameId, question) {
    const key = await hashKey(gameId, question);
    const store = await tx("ai_cache");
    return new Promise(resolve => {
      const r = store.get(key);
      r.onsuccess = () => {
        const v = r.result;
        // หมดอายุใน 7 วัน
        if (v && Date.now() - v.time < 7 * 86400000) resolve(v);
        else resolve(null);
      };
      r.onerror = () => resolve(null);
    });
  },
  async set(gameId, question, answer, citations = []) {
    const key = await hashKey(gameId, question);
    const store = await tx("ai_cache", "readwrite");
    store.put({ key, gameId, question, answer, citations, time: Date.now() });
  },
  async clear() {
    const store = await tx("ai_cache", "readwrite");
    store.clear();
  }
};

// ─── Recent Searches ──────────────────────────────────────────
window.RecentSearch = {
  async add(query) {
    if (!query || !query.trim()) return;
    const store = await tx("searches", "readwrite");
    store.add({ query: query.trim(), time: Date.now() });
  },
  async list(limit = 10) {
    const store = await tx("searches");
    return new Promise(resolve => {
      const r = store.getAll();
      r.onsuccess = () => {
        const all = (r.result || []).sort((a, b) => b.time - a.time);
        // unique + limit
        const seen = new Set();
        const out = [];
        for (const item of all) {
          if (!seen.has(item.query)) { seen.add(item.query); out.push(item); }
          if (out.length >= limit) break;
        }
        resolve(out);
      };
      r.onerror = () => resolve([]);
    });
  }
};

// ─── Draft (ข้อความค้างพิมพ์) ─────────────────────────────────
window.Draft = {
  async save(gameId, text) {
    const store = await tx("drafts", "readwrite");
    if (!text) store.delete(gameId);
    else store.put({ game_id: gameId, text, time: Date.now() });
  },
  async load(gameId) {
    const store = await tx("drafts");
    return new Promise(resolve => {
      const r = store.get(gameId);
      r.onsuccess = () => resolve(r.result ? r.result.text : "");
      r.onerror = () => resolve("");
    });
  }
};

console.log("[LocalDB] IndexedDB ready: ai_cache, searches, drafts");
