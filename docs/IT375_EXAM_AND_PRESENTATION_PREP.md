# IT375 Exam and Mini Project Presentation Prep

เอกสารนี้ใช้เตรียมสอบปลายภาคและพรีเซนต์ Mini Project วันที่ 8 พฤษภาคม 2569 สำหรับโปรเจ็กต์ `Board Game Rulebook AI Assistant`

## 1. แผนอ่านก่อนสอบ

ตารางเวลาแนะนำก่อนเข้าสอบ 13:00-16:00

| เวลา | สิ่งที่ต้องอ่าน | เป้าหมาย |
|---|---|---|
| 45 นาที | HTTP method, status code, API design | แยก GET/POST/PUT/PATCH/DELETE และตอบ status code ได้ |
| 45 นาที | ORM, CRUD, Pydantic, MVC, Jinja | อ่านโค้ด FastAPI + SQLAlchemy + template ได้ |
| 45 นาที | JWT, authentication, form login | อธิบาย login flow และเติมโค้ด auth ได้ |
| 30 นาที | Ajax/fetch, Unit Test | เข้าใจ frontend เรียก API และ pytest/TestClient |
| 30 นาที | Git, Render deploy | จำคำสั่ง Git และขั้นตอน deploy |
| 30 นาที | ทำข้อสอบซ้อม | ตั้งเป้า 16/20 ขึ้นไป |
| 30 นาที | ซ้อมพูดปากเปล่า | อธิบาย JWT/API/Render โดยไม่ดูโพยยาว |

## 2. Cheat Sheet อ่านสอบ

### API และ HTTP Method

- API คือช่องทางให้ client เช่น browser หรือ app เรียกใช้บริการจาก server
- REST API มักออกแบบโดยใช้ resource เป็นคำนาม เช่น `/api/v1/games`, `/api/v1/users/{id}`
- `GET` ใช้อ่านข้อมูล ไม่ควรเปลี่ยนข้อมูลในระบบ
- `POST` ใช้สร้างข้อมูลหรือส่ง action เช่น login, create game
- `PUT` ใช้อัปเดตข้อมูลทั้งรายการ
- `PATCH` ใช้อัปเดตข้อมูลบาง field
- `DELETE` ใช้ลบข้อมูล
- Query parameter ใช้กรอง/ค้นหา เช่น `/api/v1/games?search=Ticket`
- Path parameter ใช้อ้างถึง resource เฉพาะ เช่น `/api/v1/games/5`

### HTTP Status Code

| Code | ความหมาย | ตัวอย่างในข้อสอบ |
|---|---|---|
| 200 OK | สำเร็จ | ดึงรายการเกมสำเร็จ |
| 201 Created | สร้างข้อมูลสำเร็จ | สมัครสมาชิกหรือสร้างข้อมูลใหม่ |
| 204 No Content | สำเร็จแต่ไม่มี body | favicon หรือ delete แบบไม่คืนข้อมูล |
| 400 Bad Request | request ผิดหรือข้อมูลไม่ครบ | PDF ยังไม่ได้อัปโหลด |
| 401 Unauthorized | ยังไม่ได้ login/token ไม่ถูกต้อง | เรียก `/api/v1/chat` โดยไม่มี JWT |
| 403 Forbidden | login แล้วแต่ไม่มีสิทธิ์ | user ธรรมดาเรียก admin endpoint |
| 404 Not Found | ไม่พบข้อมูล | game id ไม่มีใน database |
| 422 Unprocessable Entity | validation fail | body ไม่ตรง schema Pydantic |
| 500 Internal Server Error | server error | exception ที่ไม่ได้จัดการ |

### API Design

- ตั้งชื่อ endpoint เป็นคำนาม ไม่ใช้คำกริยาเกินจำเป็น
- ใส่ version เช่น `/api/v1`
- ใช้ method ให้ตรงความหมาย เช่น `GET /games`, `POST /games`
- ใช้ response model เพื่อควบคุมรูปแบบ JSON
- แยก router ตามหน้าที่ เช่น auth, games, chat, admin
- ใช้ dependency injection เช่น `Depends(get_db)`, `Depends(get_current_user)`

ตัวอย่างจากโปรเจ็กต์:

```python
@router.get("", response_model=List[GameOut])
def list_games(search: str = "", db: Session = Depends(get_db)):
    q = db.query(BoardGame)
    if search:
        q = q.filter(BoardGame.name.like(f"%{search}%"))
    return q.order_by(BoardGame.created_at.desc()).all()
```

### Pydantic

- Pydantic ใช้กำหนด schema ของ request/response
- ช่วย validation ข้อมูลอัตโนมัติ
- ใช้กับ FastAPI เพื่อสร้าง docs ใน `/docs`
- `BaseModel` คือฐานสำหรับสร้าง schema
- `response_model` ใช้บอกว่า API จะคืนข้อมูลรูปแบบไหน

ตัวอย่างแนวคิด:

```python
class UserLogin(BaseModel):
    username: str
    password: str
```

### ORM และ SQLAlchemy

- ORM คือการ map table ใน database เป็น class ใน Python
- ลดการเขียน SQL ตรง ๆ และช่วยลดความเสี่ยง SQL injection
- Model สำคัญในโปรเจ็กต์:
  - `User` เก็บ username, email, password_hash, role, is_active
  - `BoardGame` เก็บข้อมูลเกม, path ของ PDF, สถานะ index
  - `Conversation` เก็บห้องสนทนาของ user กับเกม
  - `Message` เก็บข้อความ user/assistant และ citations
  - `Favorite` เก็บเกมโปรดของ user

คำสั่ง ORM ที่ควรจำ:

```python
db.query(User).all()
db.query(User).filter(User.username == username).first()
db.get(BoardGame, game_id)
db.add(user)
db.commit()
db.refresh(user)
db.delete(game)
```

### CRUD

- Create: `db.add(...)`, `db.commit()`
- Read: `db.query(...).all()`, `db.get(...)`
- Update: แก้ property แล้ว `db.commit()`
- Delete: `db.delete(...)`, `db.commit()`

ตัวอย่าง update:

```python
u = db.get(User, user_id)
u.is_active = not u.is_active
db.commit()
```

### MVC และ Jinja

- MVC = Model, View, Controller
- Model คือ database model เช่น `models.py`
- View คือ HTML template เช่น `templates/*.html`
- Controller คือ router ที่รับ request แล้วส่ง response เช่น `routers/web.py`
- Jinja2 ใช้ render HTML จาก template

คำสั่ง Jinja ที่ควรจำ:

```html
{{ user.username }}
{% if user %}
{% endif %}
{% for game in games %}
{% endfor %}
{% extends "base.html" %}
{% block content %}{% endblock %}
```

FastAPI register templates:

```python
templates = Jinja2Templates(directory="templates")
return templates.TemplateResponse("index.html", {"request": request})
```

### Ajax และ Fetch

- Ajax คือการให้ JavaScript เรียก API โดยไม่ต้อง reload ทั้งหน้า
- ปัจจุบันนิยมใช้ `fetch`
- Server ส่ง JSON กลับมา แล้ว frontend เอาไปแสดงผล

ตัวอย่าง:

```javascript
const res = await fetch("/api/v1/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify({ game_id: 1, question: "เล่นยังไง" })
});
const data = await res.json();
```

### JWT Authentication

JWT คือ token ที่ server สร้างหลัง login สำเร็จ เพื่อให้ client ใช้ยืนยันตัวตนใน request ถัดไป

Flow ของโปรเจ็กต์:

1. User ส่ง username/password ไปที่ `POST /api/v1/auth/login`
2. Server หา user จาก database
3. ตรวจ password ด้วย `bcrypt.checkpw`
4. ถ้าถูกต้อง สร้าง JWT โดยใส่ `sub`, `role`, `exp`
5. ส่ง token กลับเป็น JSON และตั้ง cookie `access_token`
6. Endpoint ที่ต้อง login ใช้ `Depends(get_current_user)`
7. `get_current_user` decode token แล้วโหลด user จาก database
8. Admin endpoint ใช้ `require_admin` เพื่อตรวจ `role == "admin"`

โค้ดที่ควรจำ:

```python
payload = {"sub": subject, "role": role, "exp": int(expire.timestamp())}
token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
```

```python
payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
```

### Unit Test

- ใช้ `pytest`
- FastAPI ใช้ `TestClient`
- Test ที่ดีควรมี happy case และ invalid case
- โปรเจ็กต์นี้มี test เช่น health check, list games, chat requires auth, admin requires auth

ตัวอย่าง:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
```

### Git

คำสั่งที่ควรจำ:

```bash
git init
git clone <url>
git status
git add .
git commit -m "message"
git branch
git checkout -b feature-name
git pull
git push
git log --oneline
```

ลำดับส่งงานทั่วไป:

1. แก้โค้ด
2. `git status`
3. `git add .`
4. `git commit -m "finish mini project"`
5. `git push origin main`
6. เชื่อม repo กับ Render หรือให้ Render auto deploy

### Render.com Deploy

ขั้นตอน deploy:

1. Push โค้ดขึ้น GitHub
2. เข้า Render Dashboard
3. New Web Service
4. เลือก GitHub repository
5. เลือก Docker หรือให้ Render อ่าน `render.yaml`
6. ตั้ง environment variables เช่น `JWT_SECRET_KEY`, `GROQ_API_KEY`, `ENV`
7. Deploy และรอ build
8. เปิด URL production เพื่อตรวจระบบ

ไฟล์ที่เกี่ยวข้องในโปรเจ็กต์:

- `Dockerfile` ใช้สร้าง container
- `render.yaml` กำหนด web service และ env vars
- `.github/workflows/ci.yml` รัน test ด้วย GitHub Actions

## 3. ข้อสอบซ้อมกากบาท 20 ข้อ

เลือกคำตอบที่ถูกที่สุด

1. Method ใดเหมาะกับการดึงรายการเกมโดยไม่แก้ข้อมูล
   - A. GET
   - B. POST
   - C. PATCH
   - D. DELETE

2. ถ้า request ไม่มี JWT แล้วเรียก endpoint ที่ต้อง login ควรได้ status code ใด
   - A. 200
   - B. 201
   - C. 401
   - D. 500

3. `POST /api/v1/auth/login` มีหน้าที่หลักคืออะไร
   - A. ลบ user
   - B. ตรวจ username/password และออก token
   - C. ดึงรายการเกม
   - D. index PDF

4. ORM หมายถึงอะไร
   - A. การเขียน HTML
   - B. การ map class กับ table ใน database
   - C. การ deploy ขึ้น cloud
   - D. การเข้ารหัส JWT

5. คำสั่งใดใช้หา user คนแรกที่ username ตรงเงื่อนไข
   - A. `db.add(User)`
   - B. `db.query(User).filter(User.username == username).first()`
   - C. `db.delete(User)`
   - D. `db.commit(User)`

6. `Depends(get_current_user)` ใน FastAPI ใช้เพื่ออะไร
   - A. โหลด CSS
   - B. ตรวจ token และดึง user ปัจจุบัน
   - C. สร้าง database table
   - D. สร้าง Docker image

7. JWT field `exp` หมายถึงอะไร
   - A. username
   - B. role
   - C. เวลาหมดอายุของ token
   - D. password hash

8. ถ้า user login แล้วแต่ไม่ใช่ admin แล้วเรียก admin endpoint ควรได้ status code ใด
   - A. 200
   - B. 401
   - C. 403
   - D. 404

9. Pydantic ใช้ทำอะไรใน FastAPI
   - A. วาด diagram
   - B. validate request/response data
   - C. เปิด cloud server
   - D. สร้าง Git commit

10. Jinja2 อยู่ในส่วนใดของ MVC มากที่สุด
    - A. Model
    - B. View
    - C. Controller
    - D. Database

11. `{{ user.username }}` ใน Jinja หมายถึงอะไร
    - A. comment
    - B. แสดงค่าตัวแปร
    - C. วน loop
    - D. import module

12. Ajax/fetch ช่วยให้เว็บทำอะไรได้
    - A. เรียก API โดยไม่ reload ทั้งหน้า
    - B. สร้าง database อัตโนมัติ
    - C. commit โค้ด
    - D. encode password

13. ในโปรเจ็กต์นี้ `bcrypt` ใช้เพื่ออะไร
    - A. hash และตรวจ password
    - B. render HTML
    - C. สร้าง vector index
    - D. deploy app

14. Endpoint ใดเป็น public endpoint ในโปรเจ็กต์
    - A. `GET /api/v1/games`
    - B. `POST /api/v1/chat`
    - C. `GET /api/v1/admin/stats`
    - D. `POST /api/v1/admin/games`

15. `db.commit()` ใช้ทำอะไร
    - A. ยืนยันการเปลี่ยนแปลงลง database
    - B. สร้าง token
    - C. เปิด server
    - D. อ่าน template

16. TestClient ใช้เพื่ออะไร
    - A. ทดสอบ API โดยไม่ต้องเปิด browser จริง
    - B. สร้าง user interface
    - C. เปิด Render service
    - D. สร้าง PDF

17. คำสั่งใดใช้ดูสถานะไฟล์ใน Git
    - A. `git push`
    - B. `git status`
    - C. `git clone`
    - D. `git init`

18. Render.com ใช้ในบทเรียนเพื่ออะไร
    - A. ออกแบบ schema
    - B. deploy web application ขึ้น cloud
    - C. เขียน unit test
    - D. แปลง PDF

19. `response_model=List[GameOut]` ใช้เพื่ออะไร
    - A. บอก schema ของ response
    - B. ลบเกมทั้งหมด
    - C. สร้าง JWT
    - D. เปิด admin panel

20. กรณี `db.get(BoardGame, game_id)` ไม่พบข้อมูล ควร raise อะไร
    - A. 200 OK
    - B. 404 Not Found
    - C. 201 Created
    - D. 204 No Content

### เฉลย MCQ

1 A, 2 C, 3 B, 4 B, 5 B, 6 B, 7 C, 8 C, 9 B, 10 B, 11 B, 12 A, 13 A, 14 A, 15 A, 16 A, 17 B, 18 B, 19 A, 20 B

## 4. คำถามอธิบายหลักการทำงาน

### ข้อ 1: อธิบาย JWT

คำตอบตัวอย่าง:

JWT เป็น token สำหรับยืนยันตัวตนหลังจากผู้ใช้ login สำเร็จ ในระบบนี้ผู้ใช้ส่ง username และ password ไปที่ `/api/v1/auth/login` จากนั้น server ตรวจ password ด้วย bcrypt ถ้าถูกต้องจะสร้าง access token โดยใส่ข้อมูล `sub` เป็น username, `role` เป็นสิทธิ์ของผู้ใช้ และ `exp` เป็นเวลาหมดอายุ เมื่อผู้ใช้เรียก API ที่ต้อง login จะส่ง token มากับ header `Authorization: Bearer <token>` หรือ cookie ระบบจะ decode token ตรวจว่าถูกต้องและยังไม่หมดอายุ แล้วดึง user จาก database ถ้า endpoint เป็น admin จะตรวจ role เพิ่มด้วย `require_admin`

### ข้อ 2: อธิบายการออกแบบ API

คำตอบตัวอย่าง:

การออกแบบ API ที่ดีควรแยก resource ให้ชัดเจน ใช้ URL เป็นคำนาม ใช้ HTTP method ให้ตรงหน้าที่ และใส่ version เช่น `/api/v1` ในโปรเจ็กต์นี้แยก router เป็น auth, games, chat และ admin เช่น `GET /api/v1/games` ใช้ดึงรายการเกม, `POST /api/v1/auth/login` ใช้เข้าสู่ระบบ, `POST /api/v1/chat` ใช้ถามคำถาม ระบบใช้ Pydantic schema ควบคุม request/response และใช้ status code ให้เหมาะสม เช่น 401 เมื่อไม่ได้ login, 403 เมื่อไม่มีสิทธิ์ admin, 404 เมื่อไม่พบข้อมูล

### ข้อ 3: อธิบายการ deploy ลง Render.com

คำตอบตัวอย่าง:

ขั้นตอน deploy เริ่มจาก push โค้ดขึ้น GitHub จากนั้นเข้า Render.com แล้วสร้าง New Web Service เชื่อมกับ repository ของโปรเจ็กต์ ระบบนี้มี `Dockerfile` สำหรับติดตั้ง dependency และรัน FastAPI ด้วย uvicorn และมี `render.yaml` เพื่อบอก Render ว่าเป็น web service แบบ Docker ต้องตั้ง environment variables เช่น `JWT_SECRET_KEY`, `GROQ_API_KEY`, `ENV` หลังจากกด deploy Render จะ build image, start server และให้ URL สำหรับใช้งานจริง เมื่อ push commit ใหม่ขึ้น GitHub ก็สามารถให้ Render auto deploy ได้

## 5. แบบฝึกเติมโค้ด Authentication จาก Form

โจทย์: เติมโค้ดให้ login จาก form สำเร็จ ถ้า username/password ผิดให้ตอบ 401 ถ้าถูกต้องให้สร้าง JWT และ redirect ไปหน้า dashboard

```python
from fastapi import APIRouter, Depends, Form, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth import verify_password, create_access_token

router = APIRouter()

@router.post("/login")
def login_form(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(user.username, user.role)

    redirect = RedirectResponse(
        url="/dashboard",
        status_code=status.HTTP_303_SEE_OTHER
    )
    redirect.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        path="/"
    )
    return redirect
```

จุดที่ควรจำ:

- `Form(...)` ใช้รับค่าจาก HTML form
- `db.query(User).filter(...).first()` ใช้หา user
- `verify_password` ใช้เทียบ password กับ hash
- `HTTPException(status_code=401)` ใช้เมื่อ login ไม่ผ่าน
- `create_access_token` ใช้สร้าง JWT
- `RedirectResponse(..., status_code=303)` ใช้ redirect หลัง POST
- `set_cookie` ใช้เก็บ token ใน browser

## 6. สคริปต์พรีเซนต์ Mini Project ตาม Rubric

เวลาเป้าหมาย 6-8 นาที ให้พูดเรียงตามคะแนนในรูป เพื่อให้อาจารย์เห็นครบทุกหัวข้อ

### ช่วงที่ 1: เปิดเรื่องและบอกขอบเขตระบบ 45 วินาที

สวัสดีครับ โปรเจ็กต์ของผมชื่อ Board Game Rulebook AI Assistant เป็น Web Application ที่พัฒนาด้วย FastAPI สำหรับช่วยตอบคำถามกติกาบอร์ดเกมจากคู่มือ PDF จริง ปัญหาคือคู่มือบอร์ดเกมมักยาวและค้นหายาก ผู้ใช้จึงสามารถเลือกเกม ถามคำถามเป็นภาษาธรรมชาติ แล้วระบบจะค้นหาข้อมูลจากคู่มือและตอบกลับพร้อมอ้างอิงหน้าที่เกี่ยวข้อง

ขอบเขตของระบบตามที่กำหนดมีครบ 4 ส่วนหลัก คือมี Admin สำหรับจัดการข้อมูล มี API สำหรับให้ frontend เรียกใช้งาน มี Database Models สำหรับเก็บข้อมูล และมี Authentication ด้วย Login และ JWT สำหรับ endpoint ที่ต้องป้องกันสิทธิ์

### ช่วงที่ 2: ระบบทำงานได้ตามขอบเขตที่กำหนด 90 วินาที

ระบบแบ่งผู้ใช้เป็น 2 บทบาท คือ User และ Admin

ฝั่ง User สามารถสมัครสมาชิก เข้าสู่ระบบ ดูรายการบอร์ดเกม เลือกเกม ถามคำถามกติกา ดูประวัติการสนทนา ปักหมุดหรือลบ conversation และจัดการ favorite เกมได้

ฝั่ง Admin สามารถเพิ่มบอร์ดเกม อัปโหลดรูปและ PDF คู่มือ สั่ง index PDF เพื่อให้ระบบค้นหาในคู่มือได้ ลบเกม ดูสถิติการใช้งาน และจัดการผู้ใช้ เช่นเปิดปิดสถานะ user หรือ delete user ที่ไม่ใช่ admin

ส่วน API แยกเป็นหมวดชัดเจน เช่น `/api/v1/auth` สำหรับสมัครและ login, `/api/v1/games` สำหรับรายการเกม, `/api/v1/chat` สำหรับถามคำถาม และ `/api/v1/admin` สำหรับงานหลังบ้าน โดย frontend เรียก API เหล่านี้ผ่าน browser และ JavaScript fetch

Database Models หลักมี `User`, `BoardGame`, `Conversation`, `Message` และ `Favorite` ทำให้ระบบเก็บทั้งข้อมูลบัญชีผู้ใช้ ข้อมูลเกม คู่มือ PDF ประวัติแชท ข้อความ และเกมโปรดได้ครบตามขอบเขต

### ช่วงที่ 3: Authentication, Login และ JWT สำหรับ endpoint ที่ใช้งาน 90 วินาที

ระบบ Authentication ใช้ JWT ร่วมกับ bcrypt เริ่มจากผู้ใช้ส่ง username และ password ไปที่ `POST /api/v1/auth/login` จากนั้น server จะค้นหา user จาก database และตรวจ password ด้วย bcrypt เพราะใน database ไม่ได้เก็บ password ตรง ๆ แต่เก็บเป็น `password_hash`

ถ้า login สำเร็จ ระบบจะสร้าง JWT ที่มีข้อมูลสำคัญคือ `sub` เป็น username, `role` เป็นสิทธิ์ของผู้ใช้ และ `exp` เป็นเวลาหมดอายุ token จากนั้นส่ง token กลับเป็น JSON และตั้ง cookie ชื่อ `access_token` เพื่อให้ browser ใช้ต่อได้

endpoint ที่ต้อง login เช่น `POST /api/v1/chat`, favorite endpoint และ admin endpoint จะใช้ `Depends(get_current_user)` เพื่อตรวจ token ก่อน ถ้าไม่มี token หรือตรวจไม่ผ่านจะตอบ 401 Unauthorized

สำหรับ endpoint ของ admin จะใช้ `require_admin` เพิ่มอีกชั้น เพื่อตรวจว่า user มี `role == "admin"` ถ้า login แล้วแต่ไม่ใช่ admin จะตอบ 403 Forbidden จุดนี้ทำให้ทุก endpoint สำคัญมีการป้องกันสิทธิ์ตาม requirement

### ช่วงที่ 4: อธิบายโค้ดและโครงสร้างโปรแกรม 120 วินาที

โครงสร้างโปรแกรมแบ่งเป็นหลายชั้นเพื่อให้อธิบายและดูแลได้ง่าย

ไฟล์ `main.py` เป็นจุดเริ่มต้นของ FastAPI ทำหน้าที่สร้าง app, เปิด static files, ใส่ CORS middleware, สร้าง table จาก SQLAlchemy models และ include router ต่าง ๆ

โฟลเดอร์ `routers` เป็นส่วน Controller ของระบบ เช่น `auth_api.py` รับผิดชอบ register/login/me, `games_api.py` รับผิดชอบ list/get/favorite เกม, `chat_api.py` รับผิดชอบถามคำถามและประวัติแชท, `admin_api.py` รับผิดชอบ upload PDF, index, stats และจัดการ user

ไฟล์ `models.py` เป็นส่วน Model ของ MVC ใช้ SQLAlchemy ORM กำหนด table เช่น `User`, `BoardGame`, `Conversation`, `Message`, `Favorite` เวลาอ่านข้อมูลจะใช้คำสั่งเช่น `db.query(User).filter(...).first()` และเวลาเพิ่มข้อมูลจะใช้ `db.add(...)` แล้ว `db.commit()`

โฟลเดอร์ `templates` เป็นส่วน View ใช้ Jinja2 แสดงหน้าเว็บ เช่น login, dashboard, chat และ admin panel ส่วน `static` เก็บ CSS, JavaScript และไฟล์ upload

โฟลเดอร์ `services` เป็น Business Logic เช่น `pdf_parser.py` อ่านและแบ่งข้อความจาก PDF, `vector_store.py` สร้าง TF-IDF index สำหรับค้นหาข้อความในคู่มือ และ `rag_service.py` นำข้อความที่ค้นเจอไปประกอบ prompt แล้วเรียก Groq LLaMA เพื่อสร้างคำตอบภาษาไทย

สรุปคือระบบนี้มีรูปแบบใกล้กับ MVC คือ Model อยู่ใน `models.py`, View อยู่ใน `templates`, Controller อยู่ใน `routers` และมี Service Layer แยก logic ที่ซับซ้อนออกจาก router

### ช่วงที่ 5: System Architecture และ Use Case Diagram 60 วินาที

จาก Use Case Diagram actor หลักมี User และ Admin โดย Admin สืบทอดความสามารถของ User แต่เพิ่มงานจัดการระบบ เช่นเพิ่มเกม อัปโหลด PDF, index คู่มือ และจัดการผู้ใช้ ส่วน User ใช้งานหลักคือ register, login, browse games, ask question และดูประวัติแชท

จาก System Architecture การทำงานเริ่มจาก Browser ส่ง request ผ่าน HTTPS ไปยัง FastAPI บน Render จากนั้น FastAPI router จะตรวจ JWT ถ้า endpoint นั้นต้อง login แล้วส่งต่อไปยัง service layer หรือ database layer

ข้อมูลปกติ เช่น user, game, conversation และ message เก็บใน SQLite ผ่าน SQLAlchemy ORM ส่วนไฟล์ PDF และรูปเก็บใน `static/uploads` และข้อมูลสำหรับค้นหาคู่มือเก็บเป็น TF-IDF index เมื่อ user ถามคำถาม ระบบจะค้น context จากคู่มือแล้วเรียก Groq เพื่อ generate คำตอบ

### ช่วงที่ 6: Demo ระบบให้เห็นว่าใช้งานได้จริง 90 วินาที

ตอน demo ผมจะเริ่มจากเปิดเว็บ production บน Render ที่ `https://mini-project-it375.onrender.com` ถ้า Render free tier sleep อาจต้องรอระบบตื่นประมาณ 30-60 วินาที

ขั้นแรกจะแสดงหน้า login หรือ register แล้วเข้าสู่ระบบ เพื่อให้เห็นว่า authentication ทำงานจริง หลังจาก login แล้วจะเปิดรายการเกม เลือกเกม และถามคำถามกติกาในหน้า chat จากนั้นระบบจะตอบคำถามพร้อมข้อมูลอ้างอิงจากคู่มือ

ต่อมาจะเปิด admin panel เพื่อให้เห็นว่า admin สามารถเพิ่มเกม อัปโหลด PDF และสั่ง index ได้ รวมถึงดูข้อมูลสถิติและจัดการผู้ใช้

สุดท้ายจะเปิด `/docs` เพื่อให้เห็น Swagger UI ของ FastAPI ว่าระบบมี API จริง แยก endpoint เป็นหมวด และ endpoint ที่ต้องมีสิทธิ์จะถูกป้องกันด้วย JWT

ถ้าระหว่าง demo AI ติด quota หรือ Render ช้า ผมจะอธิบาย fallback ว่าส่วนการค้นหาคู่มือยังทำงานจาก TF-IDF index และสามารถชี้ให้ดู API, database model, และ flow ในโค้ดแทนได้ เพื่อแสดงว่าระบบไม่ได้หลุดหรือ error จากโครงสร้างหลัก

### ช่วงที่ 7: Git, Unit Test, Deploy และสรุป 45 วินาที

โปรเจ็กต์นี้ใช้ Git สำหรับเก็บ version ของโค้ด มี GitHub repository และมี GitHub Actions ใน `.github/workflows/ci.yml` เพื่อรัน test ด้วย pytest เช่น test health check, list games, chat requires auth และ admin requires auth

การ deploy ใช้ Render.com ผ่าน Docker โดย `Dockerfile` ติดตั้ง dependency และรัน FastAPI ด้วย uvicorn ส่วน `render.yaml` กำหนด web service และ environment variables เช่น `JWT_SECRET_KEY`, `GROQ_API_KEY`, `ENV`

สรุปตาม rubric คือระบบทำงานได้ตามขอบเขต มี Admin, API, Database Models และ Authentication ด้วย JWT อธิบายโค้ดได้จาก router, model, service และ template ระบบใช้งานได้จริงบน Render และมี Use Case Diagram กับ System Architecture Diagram ประกอบครบครับ

### ประโยคสั้นไว้ปิดท้ายถ้าอาจารย์ถามเพิ่ม

- ถ้าถามเรื่อง 401 กับ 403: 401 คือยังไม่ได้ยืนยันตัวตนหรือ token ผิด ส่วน 403 คือ login แล้วแต่สิทธิ์ไม่พอ เช่น user ธรรมดาเรียก admin endpoint
- ถ้าถามว่าทำไมใช้ ORM: เพราะเขียน query ผ่าน Python class ได้ ลด SQL ซ้ำ ๆ และเปลี่ยน database ได้ง่ายกว่าเขียน SQL ตรงทุกจุด
- ถ้าถามว่า JWT ปลอดภัยอย่างไร: ระบบไม่ใส่ password ใน token, token มีวันหมดอายุ, password ใน database เป็น bcrypt hash และ endpoint สำคัญตรวจ token ทุกครั้ง
- ถ้าถามเรื่อง AI/RAG: ระบบ retrieve ข้อความที่เกี่ยวข้องจากคู่มือก่อน แล้วจึงส่ง context ให้ LLM ตอบ ไม่ได้ให้ AI เดาเองล้วน ๆ

## 7. Demo Checklist

ก่อนถึงคิวพรีเซนต์:

- เปิด URL production: `https://mini-project-it375.onrender.com`
- ถ้า Render free tier sleep ให้เปิดรอ 30-60 วินาที
- เตรียม account user และ admin
- ทดสอบ login/register
- เปิด `/api/health` ตรวจว่า server ตอบ `status: ok`
- เปิด `/docs` ให้ Swagger UI โหลดสำเร็จ
- ทดสอบ `GET /api/v1/games`
- ทดสอบถามคำถามในหน้า chat
- เข้า admin panel
- ตรวจว่า admin เห็นเมนูเพิ่มเกม/upload PDF/index
- เตรียมเปิด GitHub repository หรือ screenshot GitHub Actions
- เตรียมเปิดไฟล์ diagram ใน `docs/diagrams.md`

ระหว่าง demo ถ้า AI quota เต็ม:

- อธิบายว่า flow การค้นหาคู่มือยังทำงานจาก TF-IDF index
- ระบบมี fallback แสดง context จากคู่มือ
- ชี้ให้เห็น endpoint และ database records แทนการรอคำตอบจาก AI

## 8. Mapping กับ Rubric 25 คะแนน

| Rubric | สิ่งที่ต้องพูดหรือ demo |
|---|---|
| ระบบทำงานได้ตามขอบเขต 10 คะแนน | เว็บใช้งานได้จริง มี User/Admin, chat, upload/index PDF, history |
| Authentication/JWT 5 คะแนน | อธิบาย login, bcrypt, JWT payload, `Depends(get_current_user)`, `require_admin` |
| อธิบายโค้ดได้ 5 คะแนน | ชี้ router, model, service layer, ORM query, status code |
| ระบบรันได้จริง 2.5 คะแนน | เปิด Render URL และ demo flow หลัก |
| Use Case/System Architecture 2.5 คะแนน | เปิด diagram และอธิบาย actor/layer/data flow |

## 9. จุดที่ต้องระวังเวลาพูด

- เอกสารบางไฟล์เก่าอาจพูดถึง Gemini หรือ ChromaDB แต่โค้ดจริงตอนนี้ใช้ Groq LLaMA และ TF-IDF search
- ถ้าอาจารย์ถาม ให้ตอบว่าแนวคิดยังเป็น RAG เหมือนเดิม คือ retrieve context จากคู่มือ แล้ว generate answer ด้วย LLM
- SQLite เหมาะกับ mini project และ demo แต่ production ใหญ่จริงอาจเปลี่ยนเป็น PostgreSQL ได้ เพราะใช้ SQLAlchemy ORM
- JWT ไม่ได้เข้ารหัสข้อมูลแบบลับเต็มรูปแบบ จึงไม่ควรใส่ password ใน payload
- Password ต้องเก็บเป็น hash ด้วย bcrypt ไม่เก็บ plain text

## 10. คำตอบสั้นสำหรับจำก่อนเข้าสอบ

- API คือช่องทางให้ client คุยกับ server
- REST ใช้ resource + HTTP method
- 401 คือยังไม่ authenticated
- 403 คือ authenticated แล้วแต่ไม่มี permission
- ORM คือ map class กับ table
- Pydantic คือ validate schema
- Jinja คือ template engine ฝั่ง View
- Ajax/fetch คือเรียก API แบบไม่ reload หน้า
- JWT คือ token หลัง login ใช้ยืนยันตัวตน
- bcrypt ใช้ hash password
- pytest/TestClient ใช้ทดสอบ API
- Git ใช้ version control
- Render ใช้ deploy web app ขึ้น cloud
