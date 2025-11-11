import reflex as rx
from sqlmodel import select
from typing import List
import os
from datetime import datetime
from app.models import User, AllowedStudent, AllowedTeacher, SemesterResult, UploadedFile


class UserInfo(rx.Base):
    """Type for user information display."""
    id: int
    username: str
    email: str
    role: str
    full_name: str
    university_id: str


class AllowedStudentInfo(rx.Base):
    """Type for allowed student display."""
    id: int
    student_number: str
    is_registered: bool
    added_date: str


class AllowedTeacherInfo(rx.Base):
    """Type for allowed teacher display."""
    id: int
    university_email: str
    is_registered: bool
    added_date: str


class SupervisorState(rx.State):
    """State for supervisor dashboard functionality."""
    
    # User lists
    all_students: List[UserInfo] = []
    all_teachers: List[UserInfo] = []
    
    # Whitelist data
    allowed_students: List[AllowedStudentInfo] = []
    allowed_teachers: List[AllowedTeacherInfo] = []
    
    # Forms
    new_student_numbers: str = ""  # Comma-separated student numbers
    new_teacher_emails: str = ""  # Comma-separated emails
    
    # Results upload
    result_semester: str = "الفصل السابع"
    result_description: str = ""
    
    semesters: list[str] = [
        "الفصل الأول", "الفصل الثاني", "الفصل الثالث", "الفصل الرابع",
        "الفصل الخامس", "الفصل السادس", "الفصل السابع", "الفصل الثامن",
        "الفصل التاسع", "الفصل العاشر",
    ]
    
    # ========== Form Setters ==========
    @rx.event
    def set_new_student_numbers(self, value: str):
        self.new_student_numbers = value
    
    @rx.event
    def set_new_teacher_emails(self, value: str):
        self.new_teacher_emails = value
    
    @rx.event
    def set_result_semester(self, value: str):
        self.result_semester = value
    
    @rx.event
    def set_result_description(self, value: str):
        self.result_description = value
    
    # ========== Load Users ==========
    @rx.event
    def load_all_users(self):
        """Load all students and teachers."""
        with rx.session() as session:
            # Load students
            students = session.exec(
                select(User).where(User.role == "student")
            ).all()
            
            self.all_students = [
                UserInfo(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    role=user.role,
                    full_name=user.full_name or "",
                    university_id=user.university_id or "",
                )
                for user in students
            ]
            
            # Load teachers
            teachers = session.exec(
                select(User).where(User.role == "teacher")
            ).all()
            
            self.all_teachers = [
                UserInfo(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    role=user.role,
                    full_name=user.full_name or "",
                    university_id=user.university_id or "",
                )
                for user in teachers
            ]
    
    # ========== Delete User ==========
    @rx.event
    def delete_user(self, user_id: int):
        """Delete a user by ID."""
        with rx.session() as session:
            user = session.get(User, user_id)
            if user:
                if user.role == "supervisor":
                    yield rx.toast.error("لا يمكن حذف المشرف")
                    return
                
                session.delete(user)
                session.commit()
                yield rx.toast.success(f"تم حذف {user.username} بنجاح")
                yield self.load_all_users()
    
    # ========== Add Allowed Students ==========
    @rx.event
    async def add_allowed_students(self):
        """Add student numbers to whitelist."""
        from app.states.auth_state import AuthState
        
        if not self.new_student_numbers:
            yield rx.toast.error("الرجاء إدخال أرقام الطلاب")
            return
        
        # Get current supervisor
        auth_state = await self.get_state(AuthState)
        
        with rx.session() as session:
            supervisor = session.exec(
                select(User).where(User.username == auth_state.current_username)
            ).first()
            
            if not supervisor:
                yield rx.toast.error("خطأ في المصادقة")
                return
            
            # Split by comma and clean
            numbers = [num.strip() for num in self.new_student_numbers.split(",")]
            added_count = 0
            
            for num in numbers:
                # Validate 6 digits
                if not num.isdigit() or len(num) != 6:
                    yield rx.toast.warning(f"رقم غير صالح: {num} (يجب أن يكون 6 أرقام)")
                    continue
                
                # Check if already exists
                exists = session.exec(
                    select(AllowedStudent).where(AllowedStudent.student_number == num)
                ).first()
                
                if exists:
                    yield rx.toast.warning(f"الرقم {num} موجود مسبقاً")
                    continue
                
                # Add to whitelist
                new_allowed = AllowedStudent(
                    student_number=num,
                    added_by_id=supervisor.id,
                )
                session.add(new_allowed)
                added_count += 1
            
            session.commit()
            
            if added_count > 0:
                yield rx.toast.success(f"تم إضافة {added_count} رقم طالب بنجاح")
                self.new_student_numbers = ""
                yield self.load_allowed_students()
    
    # ========== Add Allowed Teachers ==========
    @rx.event
    async def add_allowed_teachers(self):
        """Add teacher emails to whitelist."""
        from app.states.auth_state import AuthState
        
        if not self.new_teacher_emails:
            yield rx.toast.error("الرجاء إدخال البريد الإلكتروني")
            return
        
        # Get current supervisor
        auth_state = await self.get_state(AuthState)
        
        with rx.session() as session:
            supervisor = session.exec(
                select(User).where(User.username == auth_state.current_username)
            ).first()
            
            if not supervisor:
                yield rx.toast.error("خطأ في المصادقة")
                return
            
            # Split by comma and clean
            emails = [email.strip() for email in self.new_teacher_emails.split(",")]
            added_count = 0
            
            for email in emails:
                # Validate email domain
                if not email.endswith("@nilevalley.edu.sd"):
                    yield rx.toast.warning(f"بريد غير صالح: {email} (يجب أن ينتهي بـ @nilevalley.edu.sd)")
                    continue
                
                # Check if already exists
                exists = session.exec(
                    select(AllowedTeacher).where(AllowedTeacher.university_email == email)
                ).first()
                
                if exists:
                    yield rx.toast.warning(f"البريد {email} موجود مسبقاً")
                    continue
                
                # Add to whitelist
                new_allowed = AllowedTeacher(
                    university_email=email,
                    added_by_id=supervisor.id,
                )
                session.add(new_allowed)
                added_count += 1
            
            session.commit()
            
            if added_count > 0:
                yield rx.toast.success(f"تم إضافة {added_count} بريد إلكتروني بنجاح")
                self.new_teacher_emails = ""
                yield self.load_allowed_teachers()
    
    # ========== Load Whitelists ==========
    @rx.event
    def load_allowed_students(self):
        """Load allowed students list."""
        with rx.session() as session:
            allowed = session.exec(select(AllowedStudent)).all()
            self.allowed_students = [
                AllowedStudentInfo(
                    id=s.id,
                    student_number=s.student_number,
                    is_registered=s.is_registered,
                    added_date=s.added_date.strftime("%Y-%m-%d"),
                )
                for s in allowed
            ]
    
    @rx.event
    def load_allowed_teachers(self):
        """Load allowed teachers list."""
        with rx.session() as session:
            allowed = session.exec(select(AllowedTeacher)).all()
            self.allowed_teachers = [
                AllowedTeacherInfo(
                    id=t.id,
                    university_email=t.university_email,
                    is_registered=t.is_registered,
                    added_date=t.added_date.strftime("%Y-%m-%d"),
                )
                for t in allowed
            ]
    
    # ========== Delete Files ==========
    @rx.event
    def delete_file(self, file_id: int):
        """Delete a file uploaded by teacher."""
        with rx.session() as session:
            file = session.get(UploadedFile, file_id)
            if file:
                # Delete physical file
                if os.path.exists(file.file_path):
                    os.remove(file.file_path)
                
                # Delete from database
                session.delete(file)
                session.commit()
                yield rx.toast.success("تم حذف الملف بنجاح")