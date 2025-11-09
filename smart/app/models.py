import reflex as rx
from sqlmodel import Field, Session, select, Relationship
from typing import Optional, List
import bcrypt
from datetime import datetime


class User(rx.Model, table=True):
    """User model for authentication."""
    
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str  # Can be "student", "teacher", or "supervisor"
    full_name: Optional[str] = None
    university_id: Optional[str] = None
    
    # NEW: Add this relationship line
    uploaded_files: List["UploadedFile"] = Relationship(back_populates="uploaded_by")
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


# NEW: Add this entire class
class UploadedFile(rx.Model, table=True):
    """Model for storing uploaded files."""
    
    filename: str  # Original filename (e.g., "lecture1.pdf")
    stored_filename: str  # Unique filename on server (e.g., "20241108_143022_lecture_lecture1.pdf")
    file_type: str  # "lecture", "homework", or "result"
    file_description: Optional[str] = None  # اسم الملف/الوصف from form
    semester: str  # الفصل الدراسي (e.g., "الفصل السابع")
    uploaded_by_id: int = Field(foreign_key="user.id")  # Which teacher uploaded it
    upload_date: datetime = Field(default_factory=datetime.now)  # When it was uploaded
    file_size: Optional[int] = None  # Size in bytes
    file_path: str  # Full path to file (e.g., "uploaded_files/20241108_143022_lecture_lecture1.pdf")
    
    # Relationship - connects to User model
    uploaded_by: Optional["User"] = Relationship(back_populates="uploaded_files")


def create_default_users():
    """Create default users if they don't exist."""
    with rx.session() as session:
        # Check if admin already exists
        admin = session.exec(
            select(User).where(User.username == "admin")
        ).first()
        
        if not admin:
            # Create default supervisor account
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=User.hash_password("admin123"),
                role="supervisor",
                full_name="System Administrator"
            )
            session.add(admin_user)
            session.commit()
            print("✅ Default admin user created: username='admin', password='admin123'")
        else:
            print("ℹ️ Admin user already exists")