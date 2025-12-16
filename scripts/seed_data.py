"""Seed initial data for the database."""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'services', 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

from src.v1.db.base import SessionLocal, engine, Base
from src.v1.models.bucket import ResumeBucket
from src.v1.models.user import User
from src.v1.core.security import get_password_hash
from src.v1.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()


def seed_buckets():
    """Seed resume buckets."""
    buckets = [
        {"name": "AI", "description": "Artificial Intelligence and Machine Learning"},
        {"name": "Full Stack", "description": "Full Stack Development"},
        {"name": "DevOps", "description": "DevOps and Infrastructure"},
        {"name": "Sales", "description": "Sales and Business Development"},
        {"name": "Operations", "description": "Operations and Management"},
        {"name": "HR", "description": "Human Resources"},
    ]
    
    for bucket_data in buckets:
        existing = db.query(ResumeBucket).filter(ResumeBucket.name == bucket_data["name"]).first()
        if not existing:
            bucket = ResumeBucket(**bucket_data)
            db.add(bucket)
            print(f"Created bucket: {bucket_data['name']}")
    
    db.commit()


def seed_admin_user():
    """Seed admin user."""
    existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not existing:
        admin_user = User(
            email=settings.ADMIN_EMAIL,
            username=settings.ADMIN_USERNAME,
            role="admin",
            password_hash=get_password_hash(settings.ADMIN_PASSWORD),
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        print(f"Created admin user: {settings.ADMIN_EMAIL}")
    else:
        print(f"Admin user already exists: {settings.ADMIN_EMAIL}")


if __name__ == "__main__":
    print("Seeding database...")
    seed_buckets()
    seed_admin_user()
    print("Done!")

