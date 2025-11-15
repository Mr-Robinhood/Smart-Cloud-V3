import reflex as rx
from app.states.auth_state import AuthState
from app.states.file_state import FileState


def teacher_dashboard() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            _header(),
            rx.el.div(
                _upload_card(
                    title="رفع ملف محاضرة أو مرجع",
                    icon="file-text",
                    file_type="lecture",
                ),
                _upload_card(
                    title="رفع فروض منزلية (H.W)",
                    icon="file-text",
                    file_type="homework",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-5xl mb-8",
            ),
            # Files list
            _uploaded_files_section(),
            class_name="flex flex-col items-center w-full",
        ),
        # Initialize - pass username directly from AuthState
        on_mount=[
            FileState.set_username_from_auth(AuthState.current_username),
            FileState.load_files,
        ],
        class_name="font-['Inter'] bg-gradient-to-b from-blue-600 to-blue-500 min-h-screen p-8",
        dir="rtl",
    )


def _header() -> rx.Component:
    return rx.el.div(
        rx.el.h1("لوحة تحكم الأستاذ", class_name="text-2xl font-bold text-white"),
        rx.el.button(
            "تسجيل الخروج",
            on_click=AuthState.logout,
            class_name="bg-white/20 text-white font-semibold py-2 px-4 rounded-lg hover:bg-white/30 transition-colors",
        ),
        class_name="flex items-center justify-between w-full max-w-5xl mx-auto mb-10",
    )


def _upload_card(title: str, icon: str, file_type: str) -> rx.Component:
    # Determine which upload handler to use
    upload_handler = FileState.upload_lecture if file_type == "lecture" else FileState.upload_homework
    upload_id = f"upload_{file_type}"
    
    return rx.el.div(
        # Store username in a hidden field that FileState can access
        rx.el.input(
            type="hidden",
            id=f"username_field_{file_type}",
            value=AuthState.current_username,
        ),
        
        rx.el.div(
            rx.icon(icon, class_name="text-blue-600"),
            rx.el.h2(title, class_name="font-bold text-lg text-gray-800"),
            class_name="flex items-center space-x-3 rtl:space-x-reverse mb-6",
        ),
        
        # File description input
        rx.el.div(
            rx.el.label("اسم الملف", class_name="text-sm font-medium text-gray-700 mb-1"),
            rx.el.input(
                value=FileState.file_description,
                on_change=FileState.set_file_description,
                placeholder="مثال: قواعد البيانات 2 - المحاضرة 3",
                disabled=FileState.is_uploading,  # Disable during upload
                class_name="w-full bg-gray-50 border border-gray-300 rounded-md py-2 px-3 text-sm disabled:opacity-50",
            ),
            class_name="mb-4",
        ),
        
        # Semester select
        rx.el.div(
            rx.el.label("الفصل الدراسي", class_name="text-sm font-medium text-gray-700 mb-1"),
            rx.select(
                FileState.semesters,
                value=FileState.selected_semester,
                on_change=FileState.set_selected_semester,
                disabled=FileState.is_uploading,  # Disable during upload
                class_name="w-full bg-gray-50 border border-gray-300 rounded-md py-2 px-3 text-sm",
            ),
            class_name="mb-4",
        ),
        
        # File upload area
        rx.upload(
            rx.el.div(
                rx.cond(
                    FileState.is_uploading & (FileState.current_upload_id == upload_id),
                    # Uploading state
                    rx.el.div(
                        rx.el.div(
                            class_name="animate-spin h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full"
                        ),
                        rx.el.p("جاري الرفع...", class_name="font-semibold text-gray-700 mt-2"),
                        class_name="flex flex-col items-center justify-center",
                    ),
                    # Normal state
                    rx.el.div(
                        rx.icon("cloud_upload", class_name="text-blue-500 h-10 w-10"),
                        rx.el.p("اختر ملف", class_name="font-semibold text-gray-700"),
                        rx.el.p("أو اسحب الملف وأسقطه هنا", class_name="text-sm text-gray-500"),
                        rx.vstack(
                            rx.foreach(
                                rx.selected_files(upload_id), 
                                lambda f: rx.text(f, class_name="text-sm text-blue-600 mt-2")
                            ),
                        ),
                        class_name="flex flex-col items-center justify-center",
                    ),
                ),
                class_name="flex flex-col items-center justify-center p-6 bg-blue-50/50 border-2 border-dashed border-blue-200 rounded-lg text-center h-40",
            ),
            id=upload_id,
            disabled=FileState.is_uploading,  # Disable during upload
            class_name="w-full cursor-pointer",
        ),
        
        # Upload button - uses correct handler based on file_type
        rx.el.button(
            rx.cond(
                FileState.is_uploading & (FileState.current_upload_id == upload_id),
                "جاري الرفع...",
                "رفع الملف",
            ),
            on_click=upload_handler(
                rx.upload_files(upload_id=upload_id)
            ),
            disabled=FileState.is_uploading,  # Disable during upload
            class_name="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors mt-4 disabled:opacity-50 disabled:cursor-not-allowed",
        ),
        
        class_name="bg-white p-6 rounded-2xl shadow-lg",
    )


def _uploaded_files_section() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "الملفات المرفوعة",
            class_name="text-xl font-bold text-white mb-4",
        ),
        rx.el.div(
            rx.cond(
                FileState.uploaded_files.length() > 0,
                rx.foreach(
                    FileState.uploaded_files,
                    lambda file: _file_card(file),
                ),
                rx.el.p(
                    "لا توجد ملفات مرفوعة بعد",
                    class_name="text-white/80 text-center py-8",
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",
        ),
        class_name="w-full max-w-5xl bg-white/10 p-6 rounded-2xl",
    )


def _file_card(file) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("file", class_name="text-blue-600 h-8 w-8"),
            rx.el.div(
                rx.el.h3(
                    file.file_description,
                    class_name="font-semibold text-gray-800 text-sm",
                ),
                rx.el.p(
                    file.semester,
                    class_name="text-xs text-gray-500",
                ),
                class_name="flex-1",
            ),
            class_name="flex items-start gap-3 mb-3",
        ),
        rx.el.div(
            rx.el.p(f"الحجم: {file.file_size}", class_name="text-xs text-gray-600"),
            rx.el.p(f"التاريخ: {file.upload_date}", class_name="text-xs text-gray-600"),
            class_name="mb-3",
        ),
        rx.el.div(
            rx.el.button(
                "تحميل",
                on_click=FileState.download_file(file.id),
                disabled=FileState.is_deleting & (FileState.deleting_file_id == file.id),
                class_name="flex-1 bg-blue-500 text-white text-sm py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50",
            ),
            rx.el.button(
                rx.cond(
                    FileState.is_deleting & (FileState.deleting_file_id == file.id),
                    "جاري الحذف...",
                    "حذف",
                ),
                on_click=FileState.delete_file(file.id),
                disabled=FileState.is_deleting,
                class_name="flex-1 bg-red-500 text-white text-sm py-2 rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            class_name="flex gap-2",
        ),
        class_name="bg-white p-4 rounded-lg shadow",
    )