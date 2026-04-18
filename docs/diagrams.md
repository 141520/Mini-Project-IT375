# BoardGame AI — Diagrams

## วิธีดู
- **UseCase / Architecture (Mermaid):** วางโค้ดใน [mermaid.live](https://mermaid.live)
- **UseCase (PlantUML):** วางโค้ดใน [plantuml.com/plantuml](https://www.plantuml.com/plantuml/uml/)

---

## 1. Use Case Diagram (PlantUML)

```plantuml
@startuml BoardGame_AI_UseCase

skinparam actorStyle awesome
skinparam packageStyle rectangle
skinparam usecase {
  BackgroundColor #FFF8F1
  BorderColor #F59E0B
  ArrowColor #374151
  ActorBorderColor #374151
  ActorBackgroundColor #FEF3C7
}

left to right direction

actor "👤 User" as User
actor "🔧 Admin" as Admin
actor "🤖 Gemini AI" as AI <<external>>

rectangle "BoardGame AI System" {

  package "Authentication" {
    usecase "สมัครสมาชิก" as UC_Register
    usecase "เข้าสู่ระบบ (JWT)" as UC_Login
    usecase "ออกจากระบบ" as UC_Logout
  }

  package "Board Game" {
    usecase "ดูรายการบอร์ดเกม" as UC_ListGames
    usecase "ค้นหาบอร์ดเกม" as UC_SearchGames
    usecase "กรองตามหมวด" as UC_FilterCat
    usecase "ปักหมุดเกมโปรด" as UC_Favorite
  }

  package "Chat & RAG" {
    usecase "ถามคำถามกติกา" as UC_Ask
    usecase "ถามข้ามทุกเกม" as UC_MultiAsk
    usecase "ดูประวัติแชท" as UC_History
    usecase "ปักหมุดแชท" as UC_PinChat
    usecase "ลบประวัติแชท" as UC_DeleteChat
    usecase "ให้คะแนนคำตอบ" as UC_Rate
    usecase "คัดลอกคำตอบ" as UC_Copy
  }

  package "Admin Management" {
    usecase "เพิ่มบอร์ดเกม + PDF" as UC_AddGame
    usecase "Index PDF (RAG)" as UC_IndexPDF
    usecase "ลบบอร์ดเกม" as UC_DeleteGame
    usecase "จัดการผู้ใช้" as UC_ManageUser
    usecase "ดูสถิติระบบ" as UC_Stats
  }

}

' User flows
User --> UC_Register
User --> UC_Login
User --> UC_Logout
User --> UC_ListGames
User --> UC_SearchGames
User --> UC_FilterCat
User --> UC_Favorite
User --> UC_Ask
User --> UC_MultiAsk
User --> UC_History
User --> UC_PinChat
User --> UC_DeleteChat
User --> UC_Rate
User --> UC_Copy

' Admin flows (inherits User)
Admin --|> User
Admin --> UC_AddGame
Admin --> UC_IndexPDF
Admin --> UC_DeleteGame
Admin --> UC_ManageUser
Admin --> UC_Stats

' AI external
UC_Ask ..> AI : <<uses>>
UC_MultiAsk ..> AI : <<uses>>
UC_IndexPDF ..> AI : <<translates query>>

' Include
UC_Ask ..> UC_Login : <<include>>
UC_MultiAsk ..> UC_Login : <<include>>

@enduml
```

---

## 2. System Architecture Diagram (Mermaid)

```mermaid
graph TB
    subgraph CLIENT["🌐 Client Layer"]
        Browser["Browser / PWA"]
    end

    subgraph CLOUD["☁️ Render Cloud (mini-project-it375.onrender.com)"]
        subgraph WEB["🖥️ Presentation Layer"]
            Jinja["Jinja2 Templates\n(HTML Pages)"]
            Static["Static Files\nCSS / JS / Uploads"]
        end

        subgraph API["⚡ FastAPI Application"]
            AuthAPI["🔐 /api/v1/auth\nRegister · Login · JWT"]
            GamesAPI["🎲 /api/v1/games\nList · Search · Favorite"]
            ChatAPI["💬 /api/v1/chat\nAsk · History · Rate · Pin"]
            AdminAPI["⚙️ /api/v1/admin\nGames · Users · Stats"]
        end

        subgraph SERVICE["🧠 Business Logic Layer"]
            RAG["rag_service.py\nPrompt + Answer"]
            PDF["pdf_parser.py\nExtract + Chunk"]
            VS["vector_store.py\nTF-IDF Search"]
            Auth["auth.py\nJWT + bcrypt"]
        end

        subgraph DATA["🗄️ Data Layer"]
            SQLite[("SQLite DB\nboardgame.sqlite3")]
            Pickle[("TF-IDF Index\n*.pkl files")]
            Files["PDF + Image\nUploads /data"]
        end
    end

    subgraph EXTERNAL["🔌 External Services"]
        Gemini["Google Gemini API\ngemini-1.5-flash\n(Generate Answer + Translate)"]
        GitHub["GitHub\ngithub.com/141520/\nMini-Project-IT375"]
    end

    Browser -->|"HTTPS Request"| Jinja
    Browser -->|"REST API"| AuthAPI
    Browser -->|"REST API"| GamesAPI
    Browser -->|"REST API"| ChatAPI
    Browser -->|"REST API (Admin)"| AdminAPI

    AuthAPI --> Auth
    GamesAPI --> SQLite
    ChatAPI --> RAG
    ChatAPI --> SQLite
    AdminAPI --> PDF
    AdminAPI --> SQLite

    RAG -->|"translate TH→EN"| Gemini
    RAG -->|"generate answer"| Gemini
    RAG --> VS
    PDF --> VS
    VS --> Pickle

    Auth --> SQLite
    RAG --> SQLite

    GitHub -->|"Auto Deploy"| CLOUD

    style CLIENT fill:#FEF3C7,stroke:#F59E0B
    style CLOUD fill:#EFF6FF,stroke:#3B82F6
    style EXTERNAL fill:#F0FDF4,stroke:#22C55E
    style API fill:#FFF7ED,stroke:#FB923C
    style SERVICE fill:#FAF5FF,stroke:#A855F7
    style DATA fill:#F0F9FF,stroke:#0EA5E9
```

---

## 3. Database ER Diagram (Mermaid)

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string email
        string password_hash
        string role
        bool is_active
        datetime created_at
    }

    BOARD_GAME {
        int id PK
        string name
        string description
        string image
        string pdf_path
        string language
        string category
        bool is_indexed
        int total_pages
        datetime created_at
    }

    CONVERSATION {
        int id PK
        int user_id FK
        int game_id FK
        string title
        bool is_pinned
        datetime created_at
    }

    MESSAGE {
        int id PK
        int conversation_id FK
        string role
        text content
        text citations
        int rating
        datetime created_at
    }

    FAVORITE {
        int id PK
        int user_id FK
        int game_id FK
        datetime created_at
    }

    USER ||--o{ CONVERSATION : "has"
    USER ||--o{ FAVORITE : "saves"
    BOARD_GAME ||--o{ CONVERSATION : "used in"
    BOARD_GAME ||--o{ FAVORITE : "saved by"
    CONVERSATION ||--o{ MESSAGE : "contains"
```
