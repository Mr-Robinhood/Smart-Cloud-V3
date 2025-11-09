import reflex as rx
from app.states.auth_state import AuthState
from app.states.file_state import FileState, FileInfo


def student_dashboard() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            # Header with logout
            rx.el.div(
                rx.el.h1("لوحة تحكم الطالب", class_name="text-3xl font-bold text-gray-800"),
                rx.el.button(
                    "تسجيل الخروج",
                    on_click=AuthState.logout,
                    class_name="bg-red-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-red-600 transition-colors",
                ),
                class_name="flex justify-between items-center w-full mb-8",
            ),
            
            # Welcome message
            rx.el.p("مرحباً بك في لوحة تحكم الطالب.", class_name="text-gray-600 mb-6"),
            
            # Semester tabs
            rx.el.div(
                rx.foreach(
                    FileState.semesters,
                    lambda semester: rx.el.button(
                        semester,
                        on_click=FileState.load_files(semester),
                        class_name="bg-white text-gray-800 border border-gray-300 hover:bg-blue-50 py-2 px-4 rounded-lg transition-colors text-sm font-semibold",
                    ),
                ),
                class_name="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 w-full mb-8",
            ),
            
            # Files section
            rx.el.div(
                rx.el.h2(
                    "الملفات المتاحة",
                    class_name="text-2xl font-bold text-gray-800 mb-4",
                ),
                rx.cond(
                    FileState.uploaded_files.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            FileState.uploaded_files,
                            _student_file_card,
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "لا توجد ملفات متاحة في هذا الفصل",
                            class_name="text-gray-500 text-center py-12",
                        ),
                        class_name="bg-white rounded-xl p-8 shadow-sm",
                    ),
                ),
                class_name="w-full",
            ),
            
            class_name="w-full max-w-6xl mx-auto flex flex-col items-center",
        ),
        on_mount=FileState.load_files,
        class_name="font-['Inter'] bg-sky-100 flex items-start justify-center min-h-screen p-8",
        dir="rtl",
    )


def _student_file_card(file: FileInfo) -> rx.Component:
    file_type_colors = {
        "lecture": "bg-blue-50 border-blue-200",
        "homework": "bg-yellow-50 border-yellow-200",
        "result": "bg-green-50 border-green-200",
    }
    
    file_type_labels = {
        "lecture": "محاضرة",
        "homework": "فرض منزلي",
        "result": "نتيجة",
    }
    
    return rx.el.div(
        # File icon and type badge
        rx.el.div(
            rx.icon(
                "file-text",
                class_name="text-blue-600 h-10 w-10",
            ),
            rx.el.span(
                file_type_labels.get(file.file_type, "ملف"),
                class_name="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full font-semibold",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        
        # File info
        rx.el.div(
            rx.el.h3(
                file.file_description,
                class_name="font-bold text-lg text-gray-800 mb-2",
            ),
            rx.el.p(
                f"الفصل: {file.semester}",
                class_name="text-sm text-gray-600 mb-1",
            ),
            rx.el.p(
                f"رفع بواسطة: {file.uploaded_by}",
                class_name="text-sm text-gray-600 mb-1",
            ),
            rx.el.p(
                f"التاريخ: {file.upload_date}",
                class_name="text-sm text-gray-500 mb-1",
            ),
            rx.el.p(
                f"الحجم: {file.file_size}",
                class_name="text-sm text-gray-500",
            ),
            class_name="mb-4",
        ),
        
        # Download button
        rx.link(
            rx.button(
                rx.icon("download", class_name="mr-2"),
                "تحميل الملف",
                class_name="w-full bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center",
            ),
            href=file.file_path.replace("assets/", "/"),
            is_external=True,
            download=True,
        ),
        
        class_name=f"bg-white border-2 {file_type_colors.get(file.file_type, 'bg-gray-50 border-gray-200')} p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow",
    )