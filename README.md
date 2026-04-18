# 🎲 Board Game Rulebook AI Assistant

AI-powered chatbot ที่ตอบคำถามกติกาบอร์ดเกมจากคู่มือ PDF จริง ด้วยเทคนิค **RAG (Retrieval-Augmented Generation)** พร้อมอ้างอิงหน้าที่แม่นยำ

**IT375 Mini Project** — FastAPI + SQLAlchemy + JWT + ChromaDB + Gemini

---

## ✨ Features

### 👤 User
- สมัคร/เข้าสู่ระบบด้วย JWT
- ถามกติกาบอร์ดเกมเป็นภาษาธรรมชาติ
- คำตอบพร้อมอ้างอิงหน้าในคู่มือ
- บันทึกประวัติการสนทนา
- Favorite เกมโปรด

### ⚙️ Admin
- อัปโหลด PDF คู่มือเข้าระบบ
- Index ข้อมูลเข้า Vector DB (ChromaDB)
- ดูสถิติผู้ใช้งาน + คำถามยอดนิยม
- จัดการ User (enable/disable)

---

## 🏗️ Project Structure

```
boardgame-ai/
├── main.py                 # FastAPI entry point
├── config.py               # Pydantic settings (.env)
├── database.py             # SQLAlchemy engine/session
├── models.py               # DB models (User, BoardGame, Conversation, Message, Favorite)
├── auth.py                 # JWT: hash/verify/create/decode + dependencies
├── seed.py                 # Seed admin + sample data
│
├── schemas/
│   ├── user.py             # UserRegister/Login/Out, Token
│   ├── game.py             # GameCreate/Out
│   └── chat.py             # ChatRequest/Response, Citation
│
├── routers/
│   ├── web.py              # Jinja pages (/, /login, /dashboard, /chat, /admin)
│   ├── auth_api.py         # /api/v1/auth/{register,login,me}
│   ├── games_api.py        # /api/v1/games (list, get, favorite)
│   ├── chat_api.py         # /api/v1/chat (RAG Q&A + history)
│   └── admin_api.py        # /api/v1/admin (upload PDF, index, stats)
│
├── services/
│   ├── pdf_parser.py       # Extract + chunk PDF (PyMuPDF)
│   ├── vector_store.py     # ChromaDB wrapper
│   └── rag_service.py      # Retrieve → prompt → Gemini
│
├── templates/              # Jinja2 + Tailwind
│   ├── base.html
│   ├── index.html
│   ├── login.html / register.html
│   ├── dashboard.html
│   ├── chat.html           # Chat UI
│   └── admin/index.html    # Admin panel
│
├── static/
│   ├── css/app.css
│   ├── js/app.js
│   └── uploads/            # PDF + images
│
├── tests/                  # pytest
│   ├── test_auth.py        # JWT & password
│   ├── test_pdf_parser.py  # Chunking
│   └── test_api.py         # API smoke tests
│
├── .github/workflows/ci.yml  # GitHub Actions CI
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── Procfile
└── render.yaml             # Render.com deploy config
```

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone <your-repo>
cd boardgame-ai

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# แก้ไข .env — ใส่ GEMINI_API_KEY (ฟรีที่ https://aistudio.google.com/apikey)
```

### 3. Seed Database
```bash
python seed.py
# สร้าง admin/admin1234 + demo/demo1234 + 4 บอร์ดเกมตัวอย่าง
```

### 4. Run
```bash
uvicorn main:app --reload
```

เปิด http://localhost:8000

- **Swagger API docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Admin Panel**: http://localhost:8000/admin (ล็อกอินด้วย admin)

---

## 🧪 Testing

```bash
pytest -q
```

---

## 🔐 JWT Authentication Flow

```
POST /api/v1/auth/login  ──► {access_token: "eyJ..."}
                              ↓
ทุก request ถัดไปแนบ header:
  Authorization: Bearer eyJ...

Server decode → ดึง user จาก DB → inject เข้า endpoint
```

Endpoints ที่ต้องมี JWT:
- `/api/v1/chat/*`
- `/api/v1/games/*/favorite`
- `/api/v1/admin/*` (admin role only)

---

## 🧠 RAG Flow

```
1. Admin upload PDF → PyMuPDF extract ข้อความต่อหน้า
2. Chunk เป็นช่วงละ ~500 ตัว overlap 80
3. ChromaDB สร้าง embedding + index ใน collection game_<id>
4. User ถาม → vector search top-4 chunks (พร้อม page metadata)
5. ประกอบ prompt → Gemini API → คำตอบ + citations
```

---

## ☁️ Deploy to Render.com

1. Push โค้ดขึ้น GitHub
2. ไปที่ https://dashboard.render.com → **New Web Service**
3. เชื่อม repo + Render จะอ่าน `render.yaml` อัตโนมัติ
4. ตั้งค่า env var:
   - `GEMINI_API_KEY` = ของคุณ
5. Deploy!

---

## 📐 System Architecture

```
┌──────────┐     HTTPS      ┌──────────────────────┐
│ Browser  │ ─────────────► │   FastAPI (Render)   │
│ Tailwind │                │                      │
└──────────┘                │  ┌────────────────┐  │
                            │  │ Web Router     │  │
                            │  │ API Router     │  │
                            │  │ Admin Router   │  │
                            │  └───────┬────────┘  │
                            │          │           │
                            │  ┌───────▼────────┐  │
                            │  │ JWT Auth       │  │
                            │  └───────┬────────┘  │
                            │          │           │
                            │  ┌───────▼────────┐  │
                            │  │ RAG Service    │  │
                            │  └──┬────────┬────┘  │
                            └─────┼────────┼───────┘
                                  │        │
                      ┌───────────▼─┐  ┌───▼───────────┐
                      │  SQLite/    │  │   ChromaDB    │
                      │  PostgreSQL │  │   (vectors)   │
                      └─────────────┘  └───────┬───────┘
                                               │
                                      ┌────────▼────────┐
                                      │  Gemini API     │
                                      └─────────────────┘
```

## 🎯 Use Case Diagram (text)

```
              ┌───────────────┐
              │     User      │
              └───────┬───────┘
                      │
        ┌─────────────┼──────────────┐
        ▼             ▼              ▼
  ( Register )   ( Login )    ( Ask Question )
                                     │
                                     ▼
                              ( View History )
                                     │
                                     ▼
                              ( Favorite Game )

              ┌───────────────┐
              │    Admin      │
              └───────┬───────┘
                      │
      ┌───────────────┼──────────────────┐
      ▼               ▼                  ▼
( Upload PDF )  ( Index Rulebook ) ( Manage Users )
                      │
                      ▼
                ( View Stats )
```

---

## 📝 Git Commit Strategy

```bash
feat: add JWT authentication
feat: add PDF upload + chunking
feat: integrate ChromaDB vector search
feat: add chat UI with citations
fix: handle empty search results
docs: add API documentation
test: add auth & PDF parser tests
ci: add GitHub Actions workflow
```

---

## 📋 Checklist ส่งงาน (IT375)

- [x] Admin Panel สำหรับจัดการข้อมูล
- [x] API (Swagger `/docs`)
- [x] Database Models
- [x] JWT Authentication
- [x] FastAPI
- [x] Database (SQLite/PostgreSQL)
- [x] Git (`.gitignore` + strategy)
- [x] Cloud deployment (`render.yaml`)
- [x] Use Case Diagram (ดูด้านบน)
- [x] System Architecture (ดูด้านบน)
- [x] Unit Tests (pytest)
- [x] CI/CD (GitHub Actions)

---

## 👤 Author

Student: 141520podcast@gmail.com
Course: IT375 Application Service Design & Development
