"""Seed initial admin user. Safe to run multiple times (idempotent)."""
from database import SessionLocal, engine, Base
from models import User, BoardGame
from auth import hash_password

# Create tables if not exist (never drops)
Base.metadata.create_all(bind=engine)


def run():
    db = SessionLocal()
    try:
        # Only insert if not already exists
        if not db.query(User).filter_by(username="admin").first():
            db.add(User(
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin1234"),
                role="admin",
            ))
            print("✅ Created admin user")
        else:
            print("ℹ️  admin user already exists — skipped")

        if not db.query(User).filter_by(username="demo").first():
            db.add(User(
                username="demo",
                email="demo@example.com",
                password_hash=hash_password("demo1234"),
                role="user",
            ))
            print("✅ Created demo user")

        db.commit()
        print("✅ Seed complete")
    except Exception as e:
        db.rollback()
        print(f"⚠️  Seed error (non-fatal): {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
