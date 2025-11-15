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
    semester: Optional[str] = None  # NEW: Add this line for student's semester
    
    # Relationships
    uploaded_files: List["UploadedFile"] = Relationship(back_populates="uploaded_by")
    allowed_students_added: List["AllowedStudent"] = Relationship()
    allowed_teachers_added: List["AllowedTeacher"] = Relationship()
    semester_results_uploaded: List["SemesterResult"] = Relationship()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class UploadedFile(rx.Model, table=True):
    """Model for storing uploaded files."""
    
    filename: str
    stored_filename: str
    file_type: str
    file_description: Optional[str] = None
    semester: str
    uploaded_by_id: int = Field(foreign_key="user.id")
    upload_date: datetime = Field(default_factory=datetime.now)
    file_size: Optional[int] = None
    file_path: str
    
    uploaded_by: Optional["User"] = Relationship(back_populates="uploaded_files")


class AllowedStudent(rx.Model, table=True):
    """Whitelist of student numbers allowed to register."""
    
    student_number: str = Field(unique=True, index=True)  # 6 digits
    is_registered: bool = False  # Has student created account?
    added_by_id: int = Field(foreign_key="user.id")  # Which supervisor added it
    added_date: datetime = Field(default_factory=datetime.now)


class AllowedTeacher(rx.Model, table=True):
    """Whitelist of teacher emails allowed to register."""
    
    university_email: str = Field(unique=True, index=True)  # Must end with @nilevalley.edu.sd
    is_registered: bool = False  # Has teacher created account?
    added_by_id: int = Field(foreign_key="user.id")  # Which supervisor added it
    added_date: datetime = Field(default_factory=datetime.now)


class SemesterResult(rx.Model, table=True):
    """Semester results files uploaded by supervisor."""
    
    semester: str  # الفصل الدراسي
    filename: str  # Original filename
    stored_filename: str  # Unique filename on server
    file_path: str  # Full path to file
    file_size: Optional[int] = None
    uploaded_by_id: int = Field(foreign_key="user.id")  # Supervisor who uploaded
    upload_date: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = None  # Optional description


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