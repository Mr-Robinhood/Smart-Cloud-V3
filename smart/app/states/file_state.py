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
    def set_file_description(self, value: str):
        self.file_description = value
    
    @rx.event
    def set_selected_semester(self, value: str):
        self.selected_semester = value
    
    @rx.event
    def set_file_type(self, value: str):
        self.file_type = value
    
    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle file upload from teacher."""
        from app.states.auth_state import AuthState
        
        if not files:
            yield rx.toast.error("الرجاء اختيار ملف")
            return
        
        if not self.file_description:
            yield rx.toast.error("الرجاء إدخال اسم الملف")
            return
        
        # Get current user
        auth_state = await self.get_state(AuthState)
        
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
                    # Get current user from database
                    user = session.exec(
                        select(User).where(User.username == auth_state.current_username)
                    ).first()
                    
                    if not user:
                        yield rx.toast.error("خطأ في المصادقة")
                        return
                    
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
                
                # Clear form
                self.file_description = ""
                
                # Refresh files list
                yield self.load_files()
                
            except Exception as e:
                yield rx.toast.error(f"خطأ في رفع الملف: {str(e)}")
    
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
                {
                    "id": file.id,
                    "filename": file.filename,
                    "file_description": file.file_description,
                    "semester": file.semester,
                    "file_type": file.file_type,
                    "upload_date": file.upload_date.strftime("%Y-%m-%d %H:%M"),
                    "uploaded_by": user.full_name or user.username,
                    "file_size": self._format_file_size(file.file_size),
                    "file_path": file.file_path,
                }
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