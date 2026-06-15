# 🎲 BoardGame AI — คู่มือการใช้งาน

**Mini Project รายวิชา IT375 — Application Service Design & Development**

ระบบ Board Game Rulebook AI Assistant — อัปโหลดคู่มือ PDF ของบอร์ดเกม แล้วถาม AI ด้วยภาษาไทยได้

---

## 🌐 URL ที่ใช้งาน (Deploy บน Render Cloud)

**https://mini-project-it375.onrender.com**

> ⚠️ Render Free Tier จะ sleep หลังไม่มีคนเข้าใช้ 15 นาที — ครั้งแรกที่เข้าอาจรอ 30-60 วินาที

---

## 🔑 บัญชีทดสอบ

### Admin (ผู้ดูแลระบบ)
| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin1234` |

**สิทธิ์:** เพิ่ม/ลบเกม, อัปโหลด PDF, จัดการผู้ใช้, ดู stats

### User (ผู้ใช้ทั่วไป)
| Field | Value |
|-------|-------|
| Username | `demo` |
| Password | `demo1234` |

**สิทธิ์:** ดูเกม, chat กับ AI, จัดการประวัติแชท

หรือสมัครใหม่ได้ที่หน้า **Register**

---

## 🚀 วิธีใช้งาน

### สำหรับผู้ใช้ทั่วไป
1. เข้า URL → คลิก **เข้าสู่ระบบ** → ใช้ `demo` / `demo1234`
2. เลือกบอร์ดเกมจากหน้าแรก
3. พิมพ์คำถามภาษาไทยได้เลย เช่น
   - "เกมนี้เล่นกี่คน?"
   - "กติกาชนะคืออะไร?"
   - "เริ่มเกมยังไง?"

### สำหรับ Admin
1. Login ด้วย `admin` / `admin1234`
2. ไปที่ **⚙️ Admin Panel**
3. กรอกข้อมูลเกม + เลือกไฟล์ PDF + รูป → กด **บันทึก + อัปโหลด**
4. กด **Index PDF** เพื่อประมวลผลคู่มือ
5. ไปที่หน้า chat ทดสอบถามคำถาม

---

## 🧱 เทคโนโลยี

| ส่วน | เทคโนโลยี |
|------|-----------|
| Backend | Python 3.12 + FastAPI |
| Frontend | Jinja2 + Tailwind CSS |
| Database | SQLite + SQLAlchemy ORM |
| Authentication | JWT (pyjwt) + bcrypt |
| AI Model | Groq — `llama-3.1-8b-instant` |
| Vector Search | TF-IDF (scikit-learn) |
| PDF Parser | PyMuPDF + pytesseract (OCR fallback) |
| Deployment | Docker on Render Cloud |

---

## 📋 ฟีเจอร์

- ✅ ระบบสมาชิก (Register, Login, Logout) + JWT Authentication ทุก API endpoint
- ✅ Role-based access control (admin / user)
- ✅ Upload PDF คู่มือบอร์ดเกม + OCR fallback สำหรับ PDF สแกน
- ✅ TF-IDF indexing + semantic search
- ✅ Thai → English translation ก่อน search เพื่อเพิ่มความแม่นยำ
- ✅ RAG (Retrieval-Augmented Generation) ด้วย Groq LLaMA 3
- ✅ Chat history + pin / delete conversation
- ✅ Category filter + search เกม
- ✅ Admin Panel: เพิ่ม/ลบเกม, จัดการ user, ลบ user
- ✅ Dark Mode + Responsive UI

---

## 🔒 ข้อจำกัดของการ Deploy บน Render Free Tier

1. **Ephemeral filesystem** — ข้อมูลและไฟล์ PDF ที่อัปโหลดจะหายเมื่อ redeploy (ไม่หายช่วง sleep/wake ปกติ)
2. **RAM จำกัด 512MB** — PDF แบบ scanned image ขนาดใหญ่อาจทำ OCR ไม่สำเร็จ
3. **Sleep หลัง idle 15 นาที** — ครั้งแรกที่เข้าอาจรอ 30-60 วินาทีให้ server wake up

> หากต้องการใช้งานระดับ production จริง ควรใช้ Supabase / PostgreSQL + Object Storage + paid instance

---

## 📁 โครงสร้างโปรเจกต์

```
boardgame-ai/
├── main.py                 # FastAPI entry point
├── config.py               # Settings (env vars)
├── database.py             # SQLAlchemy setup
├── models.py               # ORM models
├── auth.py                 # JWT + bcrypt
├── seed.py                 # Initial admin/demo users
├── routers/
│   ├── auth_api.py         # POST /login, /register
│   ├── chat_api.py         # POST /chat, conversations
│   ├── admin_api.py        # Admin endpoints
│   └── web.py              # Jinja pages
├── services/
│   ├── pdf_parser.py       # PDF text + OCR
│   ├── vector_store.py     # TF-IDF index
│   └── rag_service.py      # Groq LLaMA RAG
├── templates/              # Jinja HTML
├── static/                 # CSS, JS, uploads
└── docs/diagrams.md        # UseCase + Architecture
```

---

## 👨‍💻 ผู้พัฒนา

65112488 นายธีรพัฒน์ สุภาโสต