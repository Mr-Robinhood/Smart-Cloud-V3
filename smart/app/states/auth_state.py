import reflex as rx
from typing import Literal
from sqlmodel import select
from app.models import User, AllowedStudent, AllowedTeacher


class AuthState(rx.State):
    """The authentication state for the app."""

    is_authenticated: bool = False
    current_user_role: Literal["student", "teacher", "supervisor", ""] = ""
    current_username: str = ""
    login_role: Literal["student", "teacher", "supervisor"] = "student"
    signup_type: Literal["student", "teacher"] = "student"
    form_data: dict = {}

    @rx.event
    def handle_input(self, data: dict):
        self.form_data = data

    @rx.event
    def set_login_role(self, role: Literal["student", "teacher", "supervisor"]):
        """Set the role for the login form."""
        self.login_role = role

    @rx.event
    def set_signup_type(self, signup_type: Literal["student", "teacher"]):
        """Set the type for the signup form."""
        self.signup_type = signup_type

    @rx.event
    def login(self, form_data: dict):
        """Handle user login with database authentication."""
        # For students, they use university_id, for teachers/supervisors they use username
        username = form_data.get("username", "")
        university_id = form_data.get("university_id", "")
        password = form_data.get("password", "")
        
        # Determine which identifier to use
        login_identifier = username if username else university_id
        
        if not login_identifier or not password:
            yield rx.toast.error("Please enter username and password")
            return
        
        # Query database for user (check both username and university_id)
        with rx.session() as session:
            if username:
                user = session.exec(
                    select(User).where(User.username == username)
                ).first()
            else:
                user = session.exec(
                    select(User).where(User.university_id == university_id)
                ).first()
            
            if not user:
                yield rx.toast.error("Invalid username or password")
                return
            
            # Verify password
            if not user.verify_password(password):
                yield rx.toast.error("Invalid username or password")
                return
            
            # Check if user role matches selected role
            if user.role != self.login_role:
                yield rx.toast.error(f"This account is not a {self.login_role} account")
                return
            
            # Login successful
            self.is_authenticated = True
            self.current_user_role = user.role
            self.current_username = user.username
            
            yield rx.toast.success(f"Welcome back, {user.full_name or user.username}!")
            
            # Redirect based on role
            if user.role == "student":
                return rx.redirect("/student-dashboard")
            elif user.role == "teacher":
                return rx.redirect("/teacher-dashboard")
            elif user.role == "supervisor":
                return rx.redirect("/supervisor-dashboard")

    @rx.event
    def logout(self):
        """Log the user out."""
        self.is_authenticated = False
        self.current_user_role = ""
        self.current_username = ""
        yield rx.toast.info("Logged out successfully")
        return rx.redirect("/login")

    @rx.event
    def check_auth(self):
        """Check if the user is authenticated."""
        if not self.is_authenticated:
            return rx.redirect("/login")

    @rx.event
    def create_student_account(self, form_data: dict):
        """Handle student account creation."""
        username = form_data.get("username", "")
        email = form_data.get("email", "")
        password = form_data.get("password", "")
        confirm_password = form_data.get("confirm_password", "")
        full_name = form_data.get("full_name", "")
        university_id = form_data.get("university_id", "")
        
        # Validation
        if not username or not email or not password or not university_id:
            yield rx.toast.error("Please fill in all required fields")
            return
        
        # NEW: Validate student number format (6 digits)
        if not university_id.isdigit() or len(university_id) != 6:
            yield rx.toast.error("رقم الطالب يجب أن يكون 6 أرقام")
            return
        
        if password != confirm_password:
            yield rx.toast.error("Passwords do not match")
            return
        
        if len(password) < 6:
            yield rx.toast.error("Password must be at least 6 characters")
            return
        
        # Create user in database
        with rx.session() as session:
            # NEW: Check if student number is in whitelist
            allowed = session.exec(
                select(AllowedStudent).where(AllowedStudent.student_number == university_id)
            ).first()
            
            if not allowed:
                yield rx.toast.error("رقم الطالب غير مسموح به. الرجاء التواصل مع المشرف")
                return
            
            if allowed.is_registered:
                yield rx.toast.error("هذا الرقم مسجل مسبقاً")
                return
            
            # Check if username already exists
            existing_user = session.exec(
                select(User).where(User.username == username)
            ).first()
            
            if existing_user:
                yield rx.toast.error("Username already exists")
                return
            
            # Check if email already exists
            existing_email = session.exec(
                select(User).where(User.email == email)
            ).first()
            
            if existing_email:
                yield rx.toast.error("Email already exists")
                return
            
            # Create new student user
            new_user = User(
                username=username,
                email=email,
                password_hash=User.hash_password(password),
                role="student",
                full_name=full_name or None,
                university_id=university_id or None
            )
            
            session.add(new_user)
            
            # NEW: Mark student number as registered
            allowed.is_registered = True
            
            session.commit()
            
            yield rx.toast.success("Student account created successfully!")
            return rx.redirect("/login")

    @rx.event
    def create_teacher_account(self, form_data: dict):
        """Handle teacher account creation."""
        username = form_data.get("username", "")
        email = form_data.get("email", "")
        password = form_data.get("password", "")
        confirm_password = form_data.get("confirm_password", "")
        full_name = form_data.get("full_name", "")
        university_id = form_data.get("university_id", "")
        
        # Validation
        if not username or not email or not password or not university_id:
            yield rx.toast.error("Please fill in all required fields")
            return
        
        if password != confirm_password:
            yield rx.toast.error("Passwords do not match")
            return
        
        if len(password) < 6:
            yield rx.toast.error("Password must be at least 6 characters")
            return
        
        # Create teacher in database
        with rx.session() as session:
            # Check if username already exists
            existing_user = session.exec(
                select(User).where(User.username == username)
            ).first()
            
            if existing_user:
                yield rx.toast.error("Username already exists")
                return
            
            # Check if email already exists
            existing_email = session.exec(
                select(User).where(User.email == email)
            ).first()
            
            if existing_email:
                yield rx.toast.error("Email already exists")
                return
            
            # Create new teacher user
            new_user = User(
                username=username,
                email=email,
                password_hash=User.hash_password(password),
                role="teacher",
                full_name=full_name or None
            )
            
            session.add(new_user)
            session.commit()
            
            yield rx.toast.success("Teacher account created successfully!")
            return rx.redirect("/login")