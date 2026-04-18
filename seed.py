"""Seed initial admin + sample board games."""
from database import SessionLocal, engine, Base
from models import User, BoardGame
from auth import hash_password


def reset():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)


def run():
    db = SessionLocal()
    try:
        db.add_all([
            User(username="admin", email="admin@example.com",
                 password_hash=hash_password("admin1234"), role="admin"),
            User(username="demo", email="demo@example.com",
                 password_hash=hash_password("demo1234"), role="user"),
        ])
        db.commit()

        db.add_all([
            BoardGame(name="Catan", description="เกมสร้างอาณานิคมบนเกาะ Catan", language="th"),
            BoardGame(name="Ticket to Ride", description="สร้างเส้นทางรถไฟข้ามทวีป", language="th"),
            BoardGame(name="Carcassonne", description="วางแผ่นกระเบื้องสร้างเมือง", language="th"),
            BoardGame(name="Wingspan", description="เกมสะสมนกและระบบนิเวศ", language="th"),
        ])
        db.commit()

        print("✅ Seeded: admin/admin1234, demo/demo1234 + 4 games")
    finally:
        db.close()


if __name__ == "__main__":
    reset()
    run()
