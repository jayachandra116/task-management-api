import os
import sys
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import User, UserRole
from app.core.security import get_password_hash


ADMIN_EMAIL = os.getenv("FIRST_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("FIRST_ADMIN_PASSWORD")

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = DATABASE_URL.replace("@db:", "@localhost:")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_admin():
    if not ADMIN_PASSWORD:
        print("Error: ADMIN_PASSWORD environment variable is not set")
        sys.exit(1)
    try:
        db = SessionLocal()
        existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if existing:
            print("Admin already exists")
            return
        admin = User(
            email=ADMIN_EMAIL,
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin created: {ADMIN_EMAIL}")
    except Exception as e:
        db.rollback()
        print(f"Error creating admin: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
