import reflex as rx
from sqlmodel import select
from typing import List
import os
from datetime import datetime
from app.models import UploadedFile, User


class FileInfo(rx.Base):
    """Type for file information."""
    id: int
    filename: str
    file_description: str
    semester: str
    file_type: str
    upload_date: str
    uploaded_by: str
    file_size: str
    file_path: str


class FileState(rx.State):
    """State for managing file uploads and downloads."""
    
    # Upload form fields
    file_description: str = ""
    selected_semester: str = "الفصل السابع"
    file_type: str = "lecture"  # lecture, homework, result
    
    # Files list - using proper type now
    uploaded_files: List[FileInfo] = []
    
    # Upload state tracking - CRITICAL FIX
    is_uploading: bool = False
    current_upload_id: str = ""
    
    # Delete state tracking - CRITICAL FIX
    is_deleting: bool = False
    deleting_file_id: int = 0
    
    # Cache username to avoid auth issues - CRITICAL FIX
    cached_username: str = ""
    
    # ADD THIS: Store auth state reference
    _auth_current_username: str = ""
    
    # Available semesters
    semesters: list[str] = [
        "الفصل الأول",
        "الفصل الثاني", 
        "الفصل الثالث",
        "الفصل الرابع",
        "الفصل الخامس",
        "الفصل السادس",
        "الفصل السابع",
        "الفصل الثامن",
        "الفصل التاسع",
        "الفصل العاشر",
    ]
    
    @rx.event
    def set_username_from_auth(self, username: str):
        """Set username from auth state. Called from UI."""
        self.cached_username = username
        self._auth_current_username = username
        print(f"✓ Username set from auth: {username}")
    
    @rx.event
    def set_file_description(self, value: str):
        self.file_description = value
    
    @rx.event
    def set_selected_semester(self, value: str):
        self.selected_semester = value
    
    @rx.event
    def set_file_type(self, value: str):
        self.file_type = value
    
    @rx.event
    async def upload_lecture(self, files: list[rx.UploadFile]):
        """Upload lecture file."""
        # Prevent concurrent uploads
        if self.is_uploading:
            yield rx.toast.warning("جاري رفع ملف، الرجاء الانتظار")
            return
            
        self.file_type = "lecture"
        self.current_upload_id = "upload_lecture"
        async for event in self.handle_upload(files):
            yield event
    
    @rx.event
    async def upload_homework(self, files: list[rx.UploadFile]):
        """Upload homework file."""
        # Prevent concurrent uploads
        if self.is_uploading:
            yield rx.toast.warning("جاري رفع ملف، الرجاء الانتظار")
            return
            
        self.file_type = "homework"
        self.current_upload_id = "upload_homework"
        async for event in self.handle_upload(files):
            yield event
    
    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle file upload from teacher."""
        if not files:
            yield rx.toast.error("الرجاء اختيار ملف")
            self.is_uploading = False
            return
        
        if not self.file_description:
            yield rx.toast.error("الرجاء إدخال اسم الملف")
            self.is_uploading = False
            return
        
        # Set uploading flag
        self.is_uploading = True
        
        try:
            # SIMPLIFIED APPROACH: Get username from database by checking who's logged in as teacher
            current_username = None
            
            # First try cached username
            if self.cached_username:
                current_username = self.cached_username
                print(f"Using cached username: {current_username}")
            
            # If no cache, try to get from AuthState
            if not current_username:
                from app.states.auth_state import AuthState
                try:
                    auth_state = await self.get_state(AuthState)
                    if auth_state and hasattr(auth_state, 'current_username'):
                        current_username = auth_state.current_username
                        if current_username:
                            self.cached_username = current_username
                            print(f"Fetched and cached username: {current_username}")
                except Exception as e:
                    print(f"Error getting auth state: {e}")
            
            # Last resort: Get from cookie/session token
            if not current_username:
                try:
                    # Try to get from router session
                    if hasattr(self, 'router') and hasattr(self.router, 'session'):
                        # This might have session info
                        session_data = self.router.session
                        print(f"Router session data: {session_data}")
                except Exception as e:
                    print(f"Error getting session: {e}")
            
            # FALLBACK: Query database for any teacher (for testing only)
            if not current_username:
                print("WARNING: Using fallback - getting first teacher from database")
                with rx.session() as session:
                    teacher = session.exec(
                        select(User).where(User.role == "teacher")
                    ).first()
                    if teacher:
                        current_username = teacher.username
                        self.cached_username = current_username
                        print(f"Fallback username: {current_username}")
            
            if not current_username:
                yield rx.toast.error("خطأ في المصادقة - الرجاء تسجيل الدخول مجدداً")
                return
            
            for file in files:
                try:
                    # Create uploads directory inside assets (so Reflex serves it)
                    upload_dir = "assets/uploaded_files"
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Generate unique filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    original_filename = file.filename
                    file_extension = os.path.splitext(original_filename)[1]
                    stored_filename = f"{timestamp}_{self.file_type}_{original_filename}"
                    file_path = os.path.join(upload_dir, stored_filename)
                    
                    # Save file
                    file_data = await file.read()
                    with open(file_path, "wb") as f:
                        f.write(file_data)
                    
                    # Save to database
                    with rx.session() as session:
                        # Get current user from database using stored username
                        user = session.exec(
                            select(User).where(User.username == current_username)
                        ).first()
                        
                        if not user:
                            yield rx.toast.error("خطأ في العثور على المستخدم")
                            continue
                        
                        new_file = UploadedFile(
                            filename=original_filename,
                            stored_filename=stored_filename,
                            file_type=self.file_type,
                            file_description=self.file_description,
                            semester=self.selected_semester,
                            uploaded_by_id=user.id,
                            file_size=len(file_data),
                            file_path=file_path
                        )
                        
                        session.add(new_file)
                        session.commit()
                    
                    yield rx.toast.success(f"تم رفع الملف بنجاح: {original_filename}")
                    
                except Exception as e:
                    yield rx.toast.error(f"خطأ في رفع الملف: {str(e)}")
                    print(f"Upload error: {e}")  # Debug log
            
            # CRITICAL: Clear form and upload component
            self.file_description = ""
            
            # Clear the upload component by calling clear_files
            yield rx.clear_selected_files(self.current_upload_id)
            
            # Refresh files list AFTER all uploads
            yield FileState.load_files()
            
        except Exception as e:
            yield rx.toast.error(f"خطأ عام: {str(e)}")
            print(f"General upload error: {e}")  # Debug log
            
        finally:
            # Always reset uploading flag
            self.is_uploading = False
            self.current_upload_id = ""
    
    @rx.event
    def load_files(self, semester: str = ""):
        """Load files for a specific semester or all files."""
        with rx.session() as session:
            query = select(UploadedFile, User).join(User)
            
            # Only filter by semester if provided
            if semester and isinstance(semester, str):
                query = query.where(UploadedFile.semester == semester)
            
            results = session.exec(query).all()
            
            self.uploaded_files = [
                FileInfo(
                    id=file.id,
                    filename=file.filename,
                    file_description=file.file_description or "",
                    semester=file.semester,
                    file_type=file.file_type,
                    upload_date=file.upload_date.strftime("%Y-%m-%d %H:%M"),
                    uploaded_by=user.full_name or user.username,
                    file_size=self._format_file_size(file.file_size or 0),
                    file_path=file.file_path,
                )
                for file, user in results
            ]
    
    @rx.event
    async def load_student_files(self):
        """Load files for logged-in student's semester only."""
        from app.states.auth_state import AuthState
        
        # CRITICAL FIX: await the coroutine!
        auth_state = await self.get_state(AuthState)
        current_username = auth_state.current_username if auth_state else None
        
        if not current_username:
            self.uploaded_files = []
            return
        
        with rx.session() as session:
            # Get current user
            current_user = session.exec(
                select(User).where(User.username == current_username)
            ).first()
            
            if not current_user or not current_user.semester:
                self.uploaded_files = []
                return
            
            # Load files only from student's semester
            query = select(UploadedFile, User).join(User).where(
                UploadedFile.semester == current_user.semester
            )
            
            results = session.exec(query).all()
            
            self.uploaded_files = [
                FileInfo(
                    id=file.id,
                    filename=file.filename,
                    file_description=file.file_description or "",
                    semester=file.semester,
                    file_type=file.file_type,
                    upload_date=file.upload_date.strftime("%Y-%m-%d %H:%M"),
                    uploaded_by=user.full_name or user.username,
                    file_size=self._format_file_size(file.file_size or 0),
                    file_path=file.file_path,
                )
                for file, user in results
            ]
    
    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """Format file size to human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    @rx.event
    def download_file(self, file_id: int):
        """Trigger file download."""
        with rx.session() as session:
            file = session.get(UploadedFile, file_id)
            if file:
                # Convert path to URL format (remove 'assets/' and add leading '/')
                url_path = "/" + file.file_path.replace("assets/", "")
                return rx.download(url_path, filename=file.filename)

    @rx.event
    async def delete_file(self, file_id: int):
        """Delete a file."""
        print(f"Delete file called with ID: {file_id}")  # Debug
        
        if not file_id:
            yield rx.toast.error("معرف الملف غير صالح")
            return
        
        try:
            file_to_delete = None
            
            with rx.session() as session:
                file_to_delete = session.get(UploadedFile, file_id)
                
                if not file_to_delete:
                    yield rx.toast.error("لم يتم العثور على الملف")
                    return
                
                file_path = file_to_delete.file_path
                
                # Delete from database first
                session.delete(file_to_delete)
                session.commit()
                print(f"File deleted from database: {file_id}")  # Debug
            
            # Delete file from filesystem (outside session)
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"File deleted from filesystem: {file_path}")  # Debug
            except Exception as fs_error:
                print(f"Filesystem delete error: {fs_error}")
                # Don't fail if file doesn't exist on disk
            
            yield rx.toast.success("تم حذف الملف بنجاح")
            
            # CRITICAL FIX: Reload files list properly
            # Call load_files and get its result
            self.load_files()
            print(f"Files reloaded, count: {len(self.uploaded_files)}")  # Debug
            
        except Exception as e:
            yield rx.toast.error(f"خطأ في حذف الملف: {str(e)}")
            print(f"Delete error: {e}")
            import traceback
            traceback.print_exc()