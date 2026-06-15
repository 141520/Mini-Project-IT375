"""Generate code explanation PDF with Thai font support."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUTPUT = r"C:\Users\Ts\Desktop\BoardGame_AI_CodeDoc.pdf"

# Register Thai fonts
pdfmetrics.registerFont(TTFont("TH", r"C:\Windows\Fonts\tahoma.ttf"))
pdfmetrics.registerFont(TTFont("TH-Bold", r"C:\Windows\Fonts\tahomabd.ttf"))

# Colors
AMBER  = HexColor("#F59E0B")
DARK   = HexColor("#1E293B")
SLATE  = HexColor("#64748B")
LIGHT  = HexColor("#F8FAFC")
GREEN  = HexColor("#10B981")
BLUE   = HexColor("#3B82F6")
PURPLE = HexColor("#8B5CF6")
ORANGE = HexColor("#F97316")
CODE_BG = HexColor("#1E293B")
CODE_FG = HexColor("#E2E8F0")

def S(name, **kw):
    return ParagraphStyle(name, **kw)

H1    = S("H1",    fontSize=20, textColor=white,  fontName="TH-Bold",  spaceAfter=4,  spaceBefore=2)
H2    = S("H2",    fontSize=14, textColor=AMBER,  fontName="TH-Bold",  spaceAfter=6,  spaceBefore=12)
H3    = S("H3",    fontSize=11, textColor=DARK,   fontName="TH-Bold",  spaceAfter=4,  spaceBefore=8)
BODY  = S("BODY",  fontSize=10, textColor=DARK,   fontName="TH",       spaceAfter=5,  leading=17, alignment=TA_JUSTIFY)
CODE  = S("CODE",  fontSize=8,  textColor=CODE_FG, fontName="Courier", spaceAfter=2,  leading=12, backColor=CODE_BG, leftIndent=6)
LABEL = S("LABEL", fontSize=9,  textColor=SLATE,  fontName="TH",       spaceAfter=3)
COVER_TITLE = S("CT", fontSize=28, textColor=white, fontName="TH-Bold", alignment=TA_CENTER)
COVER_SUB   = S("CS", fontSize=13, textColor=SLATE, fontName="TH", alignment=TA_CENTER)

def header_box(title, color=AMBER):
    return Table([[Paragraph(title, H1)]], colWidths=[17*cm],
        style=TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), color),
            ("TOPPADDING",(0,0),(-1,-1), 10),
            ("BOTTOMPADDING",(0,0),(-1,-1), 10),
            ("LEFTPADDING",(0,0),(-1,-1), 14),
        ]))

def code_block(lines):
    text = "<br/>".join(
        l.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace(" ","&nbsp;")
        for l in lines
    )
    return Table([[Paragraph(text, CODE)]], colWidths=[17*cm],
        style=TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), CODE_BG),
            ("TOPPADDING",(0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("LEFTPADDING",(0,0),(-1,-1), 10),
        ]))

def info_table(rows, widths=None):
    widths = widths or [5*cm, 12*cm]
    data = [[Paragraph(f"<b>{k}</b>", BODY), Paragraph(v, BODY)] for k,v in rows]
    return Table(data, colWidths=widths, style=TableStyle([
        ("BACKGROUND",(0,0),(0,-1), LIGHT),
        ("GRID",(0,0),(-1,-1), 0.5, HexColor("#E2E8F0")),
        ("TOPPADDING",(0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
    ]))

def sp(n=1): return Spacer(1, n*0.28*cm)

def build():
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # COVER
    story += [
        sp(3),
        Table([[Paragraph("BoardGame AI", COVER_TITLE)]], colWidths=[17*cm],
            style=TableStyle([
                ("BACKGROUND",(0,0),(-1,-1), DARK),
                ("TOPPADDING",(0,0),(-1,-1), 28),
                ("BOTTOMPADDING",(0,0),(-1,-1), 28),
            ])),
        sp(2),
        Paragraph("เอกสารอธิบายโค้ดโปรแกรม", COVER_SUB),
        sp(),
        Paragraph("Mini Project — IT375 Application Service Design &amp; Development", COVER_SUB),
        sp(2),
        info_table([
            ("ผู้พัฒนา",      "65112488 นายธีรพัฒน์ สุภาโสต"),
            ("URL",           "https://mini-project-it375.onrender.com"),
            ("GitHub",        "https://github.com/141520/Mini-Project-IT375"),
            ("Tech Stack",    "Python 3.12 + FastAPI + SQLite + Groq LLaMA 3 + TF-IDF"),
        ]),
        PageBreak(),
    ]

    # 1. OVERVIEW
    story += [
        header_box("1. ภาพรวมของระบบ (System Overview)"),
        sp(),
        Paragraph(
            "BoardGame AI เป็นระบบ RAG (Retrieval-Augmented Generation) "
            "ช่วยตอบคำถามกติกาบอร์ดเกมจาก PDF คู่มือจริง โดยใช้ AI ตอบเป็นภาษาไทย", BODY),
        sp(),
        Paragraph("<b>Flow การทำงานหลัก:</b>", H3),
        code_block([
            "ผู้ใช้ถามคำถาม (ภาษาไทย)",
            "    |",
            "    v  translate_th_to_en()  [Groq API]",
            "แปลเป็นภาษาอังกฤษ",
            "    |",
            "    v  vector_store.search()  [TF-IDF]",
            "ค้นหา chunks ที่เกี่ยวข้องจาก PDF",
            "    |",
            "    v  generate_answer()  [Groq LLaMA 3]",
            "AI สร้างคำตอบจาก context ที่ค้นได้",
            "    |",
            "    v",
            "ส่งคำตอบภาษาไทยกลับให้ผู้ใช้",
        ]),
        sp(),
        Paragraph("<b>โครงสร้างไฟล์หลัก:</b>", H3),
        info_table([
            ("main.py",    "FastAPI entry point — mount routers, CORS, startup event"),
            ("config.py",  "Settings ทั้งหมด อ่านจาก Environment Variables"),
            ("database.py","SQLAlchemy engine + SessionLocal + Base"),
            ("models.py",  "ORM models: User, BoardGame, Conversation, Message"),
            ("auth.py",    "JWT token + bcrypt password + dependency functions"),
            ("seed.py",    "สร้าง admin/demo user ครั้งแรก (idempotent — ไม่ลบของเดิม)"),
            ("routers/",   "auth_api, chat_api, admin_api, games_api, web"),
            ("services/",  "pdf_parser, vector_store, rag_service"),
        ]),
        PageBreak(),
    ]

    # 2. MODELS
    story += [
        header_box("2. Database Models (models.py)", BLUE),
        sp(),
        Paragraph("ใช้ SQLAlchemy ORM กับ SQLite มี 4 ตารางหลัก:", BODY),
        sp(),
        Paragraph("<b>User — ตารางผู้ใช้งาน</b>", H3),
        code_block([
            "class User(Base):",
            "    __tablename__ = 'users'",
            "    id            = Column(Integer, primary_key=True)",
            "    username      = Column(String(50), unique=True)   # ชื่อผู้ใช้ (unique)",
            "    email         = Column(String(120), unique=True)  # อีเมล (unique)",
            "    password_hash = Column(String(255))               # bcrypt hash (ไม่เก็บ plain text)",
            "    role          = Column(String(20), default='user') # 'user' หรือ 'admin'",
            "    is_active     = Column(Boolean, default=True)     # Toggle เปิด/ปิดบัญชี",
        ]),
        sp(),
        Paragraph("<b>BoardGame — ตารางบอร์ดเกม</b>", H3),
        code_block([
            "class BoardGame(Base):",
            "    __tablename__ = 'board_games'",
            "    id          = Column(Integer, primary_key=True)",
            "    name        = Column(String(200))   # ชื่อเกม",
            "    pdf_path    = Column(String(300))   # path ไฟล์ PDF ที่อัปโหลด",
            "    category    = Column(String(50))    # หมวดหมู่ เช่น ครอบครัว / กลยุทธ์",
            "    is_indexed  = Column(Boolean)       # True = TF-IDF index แล้ว พร้อมถาม AI",
            "    total_pages = Column(Integer)       # จำนวนหน้าของ PDF",
        ]),
        sp(),
        Paragraph("<b>Conversation + Message — ประวัติแชท</b>", H3),
        code_block([
            "class Conversation(Base):    # 1 conversation = 1 session การถามเกมนั้น",
            "    user_id   = ForeignKey(users.id)       # เชื่อมกับผู้ใช้",
            "    game_id   = ForeignKey(board_games.id) # เชื่อมกับเกม",
            "    is_pinned = Column(Boolean, default=False)  # ปักหมุด",
            "    messages  = relationship('Message', cascade='all, delete-orphan')",
            "",
            "class Message(Base):         # แต่ละข้อความในแชท",
            "    conversation_id = ForeignKey(conversations.id)",
            "    role    = Column(String)  # 'user' หรือ 'assistant'",
            "    content = Column(Text)    # ข้อความ",
            "    citations = Column(Text)  # JSON: [{page, snippet}, ...]",
        ]),
        PageBreak(),
    ]

    # 3. AUTH
    story += [
        header_box("3. Authentication — JWT + bcrypt (auth.py)", GREEN),
        sp(),
        Paragraph(
            "ระบบ Authentication ใช้ JWT (JSON Web Token) สำหรับ stateless auth "
            "และ bcrypt สำหรับ hash รหัสผ่าน ไม่เก็บ plain text ใน database", BODY),
        sp(),
        Paragraph("<b>Password Hashing ด้วย bcrypt</b>", H3),
        code_block([
            "# hash รหัสผ่านก่อนเก็บ DB — ไม่มีใครถอดรหัสกลับได้",
            "def hash_password(password: str) -> str:",
            "    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()",
            "",
            "# ตรวจสอบรหัสผ่านตอน login",
            "def verify_password(plain: str, hashed: str) -> bool:",
            "    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))",
        ]),
        sp(),
        Paragraph("<b>สร้างและถอดรหัส JWT Token</b>", H3),
        code_block([
            "def create_access_token(subject: str, role: str) -> str:",
            "    payload = {",
            "        'sub':  subject,    # username",
            "        'role': role,       # 'user' หรือ 'admin'",
            "        'exp':  timestamp   # หมดอายุใน 60 นาที",
            "    }",
            "    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')",
            "",
            "def decode_token(token: str) -> dict:",
            "    return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])",
            "    # ถ้า token หมดอายุหรือผิด → raise HTTP 401",
        ]),
        sp(),
        Paragraph("<b>FastAPI Dependency — ป้องกัน Endpoint</b>", H3),
        code_block([
            "# ใช้ Depends() ป้องกัน endpoint — FastAPI เรียกอัตโนมัติทุก request",
            "",
            "# ต้อง login → ใช้ใน chat, dashboard",
            "def get_current_user(request, credentials, db) -> User:",
            "    token = credentials หรือ Cookie",
            "    payload = decode_token(token)  # ถ้า token ผิด → 401",
            "    return db.query(User).filter_by(username=payload['sub']).first()",
            "",
            "# ต้องเป็น Admin เท่านั้น → ใช้ใน admin endpoints",
            "def require_admin(user = Depends(get_current_user)) -> User:",
            "    if user.role != 'admin':",
            "        raise HTTPException(403, 'Admin privileges required')",
            "",
            "# ตัวอย่าง — endpoint นี้ทุกคน admin เข้าได้เท่านั้น",
            "@router.post('/api/v1/admin/games')",
            "def create_game(admin = Depends(require_admin), ...):",
            "    ...",
        ]),
        sp(),
        info_table([
            ("Token เก็บที่ไหน", "HTTP Cookie (access_token) ใน browser"),
            ("Token format",     "Header.Payload.Signature (Base64)"),
            ("อายุ Token",       "60 นาที ตั้งค่าใน config.py JWT_EXPIRE_MINUTES"),
            ("Algorithm",        "HS256 (HMAC SHA-256)"),
        ]),
        PageBreak(),
    ]

    # 4. RAG
    story += [
        header_box("4. RAG Service — AI ตอบคำถาม (services/rag_service.py)", PURPLE),
        sp(),
        Paragraph(
            "RAG = Retrieval-Augmented Generation คือการนำข้อมูลจริงจาก PDF มาเป็น context "
            "ให้ AI ตอบ แทนการ hallucinate (แต่งเรื่องขึ้นเอง)", BODY),
        sp(),
        Paragraph("<b>ขั้นตอน RAG ทั้งหมด (answer_question)</b>", H3),
        code_block([
            "def answer_question(game_id, game_name, question):",
            "",
            "    # Step 1: แปลคำถามไทย -> อังกฤษ เพื่อให้ TF-IDF แม่นยำขึ้น",
            "    search_query = translate_th_to_en(question)   # เรียก Groq API",
            "",
            "    # Step 2: ค้นหา chunks ที่เกี่ยวข้องด้วย TF-IDF (cosine similarity)",
            "    hits = vector_store.search(game_id, search_query, top_k=5)",
            "",
            "    # Step 3: fallback — ถ้าค่าต่ำ ลองค้นด้วยภาษาไทยตรงๆ",
            "    if not hits or hits[0]['score'] < 0.01:",
            "        hits = vector_store.search(game_id, question, top_k=5)",
            "",
            "    # Step 4: ส่ง context + คำถาม ให้ Groq LLaMA 3 สร้างคำตอบ",
            "    answer = generate_answer(game_name, question, hits[:4])",
        ]),
        sp(),
        Paragraph("<b>Prompt Template ที่ส่งให้ AI</b>", H3),
        code_block([
            'PROMPT_TEMPLATE = """',
            'You are a board game rules assistant for "{game_name}".',
            'Answer ONLY from the context below.',
            'Always cite page numbers (e.g. page 3).',
            'If no relevant info found -> reply: NO_INFO',
            '',
            'Context:',
            '{context}       <-- ข้อความจาก PDF ที่ค้นได้ (top 4 chunks)',
            '',
            'Question: {question_en}    <-- คำถามแปลเป็นอังกฤษ',
            'Original (Thai): {question_th}',
            '',
            'Answer in Thai language:   <-- บังคับตอบเป็นภาษาไทย',
            '"""',
        ]),
        sp(),
        info_table([
            ("Provider",   "Groq (groq.com)"),
            ("Model",      "llama-3.1-8b-instant"),
            ("Free Quota", "14,400 req/day, 30 RPM — ใช้ได้เยอะกว่า Gemini"),
            ("ทำไม Groq",  "เร็ว, ฟรี quota มาก, รองรับภาษาไทยได้ดี"),
        ]),
        PageBreak(),
    ]

    # 5. PDF + VECTOR
    story += [
        header_box("5. PDF Parser + TF-IDF Search", HexColor("#0EA5E9")),
        sp(),
        Paragraph("<b>pdf_parser.py — แยกข้อความจาก PDF</b>", H3),
        code_block([
            "def extract_pages(pdf_path) -> List[Dict]:",
            "    doc = fitz.open(pdf_path)   # เปิด PDF ด้วย PyMuPDF",
            "    for page in doc:",
            "        text = page.get_text('text')   # ดึงข้อความ",
            "",
            "        # ถ้าน้อยกว่า 50 ตัว = น่าจะเป็น PDF สแกน -> ใช้ OCR",
            "        if len(text.strip()) < 50:",
            "            text = _ocr_page(page)",
            "",
            "def _ocr_page(page) -> str:",
            "    # แปลงหน้าเป็นรูปภาพที่ DPI=72 (ต่ำ = ใช้ RAM น้อย)",
            "    pix = page.get_pixmap(dpi=72)",
            "    img = Image.open(io.BytesIO(pix.tobytes('png')))",
            "    # ใช้ tesseract OCR แปลงรูปเป็นข้อความ",
            "    return pytesseract.image_to_string(img, lang='eng', config='--oem 0')",
        ]),
        sp(),
        Paragraph("<b>chunk_text() — แบ่งข้อความเป็น chunks</b>", H3),
        Paragraph(
            "แต่ละหน้า PDF ถูกแบ่งเป็น chunks ขนาด ~400 ตัวอักษร "
            "มี overlap 50 ตัว เพื่อให้ context ต่อเนื่องข้ามขอบ chunk", BODY),
        code_block([
            "def chunk_text(text, chunk_size=400, overlap=50):",
            "    # พยายามตัดที่ย่อหน้า (\\n\\n) หรือจุด (.) ไม่ตัดกลางประโยค",
            "    # overlap = chunk ถัดไปเริ่มย้อนหลัง 50 ตัว เพื่อ context ต่อเนื่อง",
        ]),
        sp(),
        Paragraph("<b>vector_store.py — TF-IDF Index</b>", H3),
        Paragraph(
            "ใช้ scikit-learn TF-IDF แทน ChromaDB + embedding model "
            "ทำให้ระบบเบา ไม่ต้องการ GPU และไม่กิน RAM มาก:", BODY),
        code_block([
            "def index_chunks(game_id, chunks):",
            "    texts = [c['text'] for c in chunks]",
            "    # char_wb n-gram รองรับภาษาไทยได้โดยไม่ต้อง tokenizer",
            "    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,4))",
            "    matrix = vectorizer.fit_transform(texts)",
            "    # บันทึกเป็นไฟล์ game_1.pkl ใน disk",
            "    pickle.dump({'vectorizer': v, 'matrix': m, 'chunks': chunks}, f)",
            "",
            "def search(game_id, query, top_k=5):",
            "    # โหลด .pkl -> แปลง query เป็น vector -> cosine similarity -> top-k",
            "    q_vec = vectorizer.transform([query])",
            "    scores = cosine_similarity(q_vec, matrix)[0]",
            "    return [chunks[i] for i in scores.argsort()[-top_k:][::-1]]",
        ]),
        PageBreak(),
    ]

    # 6. ROUTERS
    story += [
        header_box("6. API Routers", ORANGE),
        sp(),
        Paragraph("<b>auth_api.py — Register &amp; Login</b>", H3),
        code_block([
            "POST /api/v1/auth/register",
            "    -> รับ username, email, password",
            "    -> hash_password() -> บันทึกลง DB",
            "    -> return JWT token + set Cookie",
            "",
            "POST /api/v1/auth/login",
            "    -> verify_password() กับ hash ใน DB",
            "    -> สร้าง JWT -> set Cookie 'access_token'",
        ]),
        sp(),
        Paragraph("<b>chat_api.py — RAG Chat</b>", H3),
        code_block([
            "POST /api/v1/chat                          # ถามคำถาม AI",
            "    -> ต้อง login  Depends(get_current_user)",
            "    -> รับ game_id, question, conversation_id",
            "    -> เรียก rag_service.answer_question()",
            "    -> บันทึก user message + AI response ลง DB",
            "    -> return answer, citations, conversation_id",
            "",
            "GET    /api/v1/chat/conversations            # ดูประวัติแชท",
            "POST   /api/v1/chat/conversations/{id}/pin  # ปักหมุด",
            "DELETE /api/v1/chat/conversations/{id}      # ลบ conversation",
        ]),
        sp(),
        Paragraph("<b>admin_api.py — Admin Management</b>", H3),
        code_block([
            "# ทุก endpoint ต้อง Admin  Depends(require_admin)",
            "",
            "POST   /api/v1/admin/games              # เพิ่มเกม + อัปโหลด PDF + รูป",
            "POST   /api/v1/admin/games/{id}/index   # chunk_pdf() -> TF-IDF index",
            "DELETE /api/v1/admin/games/{id}         # ลบเกม + ไฟล์ + index",
            "DELETE /api/v1/admin/users/{id}         # ลบ user (ลบ admin ไม่ได้)",
            "POST   /api/v1/admin/users/{id}/toggle  # เปิด/ปิดบัญชี user",
        ]),
        sp(),
        Paragraph("<b>games_api.py — Games List (Public)</b>", H3),
        code_block([
            "GET /api/v1/games",
            "    -> query params: q (search text), cat (category filter)",
            "    -> ไม่ต้อง login — ทุกคนดูรายการเกมได้",
        ]),
        PageBreak(),
    ]

    # 7. DEPLOYMENT
    story += [
        header_box("7. Deployment — Docker on Render Cloud", DARK),
        sp(),
        Paragraph("<b>Dockerfile</b>", H3),
        code_block([
            "FROM python:3.12-slim",
            "",
            "# ติดตั้ง Tesseract OCR engine สำหรับ PDF สแกน",
            "RUN apt-get install -y tesseract-ocr",
            "",
            "COPY requirements.txt .",
            "RUN pip install -r requirements.txt",
            "",
            "COPY . .",
            "EXPOSE 8000",
            "",
            "# รัน seed.py ก่อน (สร้าง admin user ถ้ายังไม่มี)",
            "# แล้วจึงเริ่ม FastAPI server",
            'CMD ["sh", "-c", "python seed.py && uvicorn main:app --host 0.0.0.0"]',
        ]),
        sp(),
        Paragraph("<b>seed.py — Idempotent Database Seeding</b>", H3),
        Paragraph(
            "รันทุกครั้งที่ container start แต่สร้าง user ก็ต่อเมื่อยังไม่มีเท่านั้น "
            "ป้องกัน data loss ถ้า server restart:", BODY),
        code_block([
            "def run():",
            "    # ตรวจก่อนว่ามีแล้วหรือยัง ถ้ามีแล้วไม่สร้างซ้ำ",
            "    if not db.query(User).filter_by(username='admin').first():",
            "        db.add(User(username='admin',",
            "                   password_hash=hash_password('admin1234'),",
            "                   role='admin'))",
            "",
            "    if not db.query(User).filter_by(username='demo').first():",
            "        db.add(User(username='demo',",
            "                   password_hash=hash_password('demo1234'),",
            "                   role='user'))",
        ]),
        sp(),
        info_table([
            ("GROQ_API_KEY",   "API key สำหรับ Groq LLaMA 3 (ห้ามใส่ใน code/git ด้วยเด็ดขาด)"),
            ("JWT_SECRET_KEY", "Secret key สำหรับเซ็น JWT token"),
            ("DATABASE_URL",   "sqlite:///./boardgame.sqlite3 (default)"),
        ]),
        sp(),
        Paragraph("<b>ข้อจำกัด Render Free Tier</b>", H3),
        info_table([
            ("Ephemeral FS",  "ไฟล์ PDF + SQLite หายทุก redeploy (ยังคงอยู่ช่วง sleep/wake ปกติ)"),
            ("RAM 512MB",     "OCR บน PDF สแกนขนาดใหญ่อาจ OOM — ลด DPI เป็น 72 แก้ปัญหาได้"),
            ("Sleep 15 min",  "ครั้งแรกที่เข้าอาจรอ 30-60 วินาทีให้ server wake up"),
        ]),
        PageBreak(),
    ]

    # 8. SUMMARY
    story += [
        header_box("8. สรุปฟีเจอร์ vs เกณฑ์คะแนน", GREEN),
        sp(),
        Table([
            [Paragraph("<b>เกณฑ์</b>", BODY),
             Paragraph("<b>ฟีเจอร์ที่มี</b>", BODY),
             Paragraph("<b>ไฟล์หลัก</b>", BODY)],
            [Paragraph("ระบบทำงานได้ /10", BODY),
             Paragraph("Register/Login, Chat+AI, Admin Panel, PDF Index, Category Filter", BODY),
             Paragraph("routers/, services/", BODY)],
            [Paragraph("JWT Auth /5", BODY),
             Paragraph("bcrypt hash, JWT token, Depends(require_admin) ทุก admin endpoint", BODY),
             Paragraph("auth.py", BODY)],
            [Paragraph("อธิบายโค้ด /5", BODY),
             Paragraph("เอกสารนี้ + โค้ดมี comment อธิบายทุกส่วนสำคัญ", BODY),
             Paragraph("CodeDoc.pdf", BODY)],
            [Paragraph("ระบบเสถียร /2.5", BODY),
             Paragraph("Error handling, fallback OCR, retry Groq 429, redirect ถ้า game ไม่มี", BODY),
             Paragraph("rag_service.py", BODY)],
            [Paragraph("Diagram /2.5", BODY),
             Paragraph("UseCase Diagram + System Architecture Diagram + ER Diagram", BODY),
             Paragraph("docs/diagrams.md", BODY)],
        ], colWidths=[4*cm, 9*cm, 4*cm],
        style=TableStyle([
            ("BACKGROUND",(0,0),(-1,0),  DARK),
            ("TEXTCOLOR", (0,0),(-1,0),  white),
            ("GRID",      (0,0),(-1,-1), 0.5, HexColor("#E2E8F0")),
            ("TOPPADDING",(0,0),(-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
            ("LEFTPADDING",(0,0),(-1,-1), 8),
            ("VALIGN",    (0,0),(-1,-1), "TOP"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [LIGHT, white]),
        ])),
        sp(2),
        Paragraph("<b>URL:</b> https://mini-project-it375.onrender.com", BODY),
        Paragraph("<b>Admin:</b> admin / admin1234     <b>User:</b> demo / demo1234", BODY),
    ]

    doc.build(story)
    print(f"Done: {OUTPUT}")

build()
