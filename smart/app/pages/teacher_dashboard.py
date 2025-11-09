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
                    icon="file-edit",
                    file_type="homework",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-5xl mb-8",
            ),
            # Files list
            _uploaded_files_section(),
            class_name="flex flex-col items-center w-full",
        ),
        on_mount=FileState.load_files,
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
    return rx.el.div(
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
                class_name="w-full bg-gray-50 border border-gray-300 rounded-md py-2 px-3 text-sm",
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
                class_name="w-full bg-gray-50 border border-gray-300 rounded-md py-2 px-3 text-sm",
            ),
            class_name="mb-4",
        ),
        
        # File upload area
        rx.upload(
            rx.el.div(
                rx.icon("cloud_upload", class_name="text-blue-500 h-10 w-10"),
                rx.el.p("اختر ملف", class_name="font-semibold text-gray-700"),
                rx.el.p("أو اسحب الملف وأسقطه هنا", class_name="text-sm text-gray-500"),
                rx.vstack(
                    rx.foreach(rx.selected_files(f"upload_{file_type}"), rx.text),
                ),
                class_name="flex flex-col items-center justify-center p-6 bg-blue-50/50 border-2 border-dashed border-blue-200 rounded-lg text-center h-40",
            ),
            id=f"upload_{file_type}",
            class_name="w-full cursor-pointer",
        ),
        
        # Upload button
        rx.el.button(
            "رفع الملف",
            on_click=[
                FileState.set_file_type(file_type),
                FileState.handle_upload(rx.upload_files(upload_id=f"upload_{file_type}"))
            ],
            class_name="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors mt-4",
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


def _file_card(file: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("file", class_name="text-blue-600 h-8 w-8"),
            rx.el.div(
                rx.el.h3(
                    file["file_description"],
                    class_name="font-semibold text-gray-800 text-sm",
                ),
                rx.el.p(
                    file["semester"],
                    class_name="text-xs text-gray-500",
                ),
                class_name="flex-1",
            ),
            class_name="flex items-start gap-3 mb-3",
        ),
        rx.el.div(
            rx.el.p(f"الحجم: {file['file_size']}", class_name="text-xs text-gray-600"),
            rx.el.p(f"التاريخ: {file['upload_date']}", class_name="text-xs text-gray-600"),
            class_name="mb-3",
        ),
        rx.el.button(
            "حذف",
            class_name="w-full bg-red-500 text-white text-sm py-2 rounded-lg hover:bg-red-600",
        ),
        class_name="bg-white p-4 rounded-lg shadow",
    )