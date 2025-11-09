import reflex as rx
from app.states.auth_state import AuthState
from app.states.dashboard_state import DashboardState


def supervisor_dashboard() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            _header(),
            rx.el.div(
                rx.el.div(
                    _manage_users_card(),
                    _upload_results_card(),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-6 items-start",
                ),
                rx.el.div(
                    _stats_card(),
                    _teacher_files_card(),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-6 items-start mt-6",
                ),
                class_name="w-full max-w-6xl",
            ),
            class_name="flex flex-col items-center w-full",
        ),
        class_name="font-['Inter'] bg-gray-100 min-h-screen p-6",
        dir="rtl",
    )


def _header() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            rx.icon("cloud", class_name="inline-block ml-2"),
            "سمارت كلاود",
            class_name="text-2xl font-bold text-gray-800",
        ),
        rx.el.button(
            "رجوع",
            rx.icon("arrow-right", class_name="mr-2"),
            on_click=AuthState.logout,
            class_name="flex items-center bg-white text-gray-700 font-semibold py-2 px-4 rounded-lg shadow-sm hover:bg-gray-50",
        ),
        class_name="flex items-center justify-between w-full max-w-6xl mx-auto mb-8",
    )


def _manage_users_card() -> rx.Component:
    return rx.el.div(
        _card_header("إدارة المستخدمين", "users"),
        rx.el.form(
            _user_input("حذف طالب (بالرقم الجامعي)", "أدخل الرقم الجامعي"),
            rx.el.button(
                "حذف",
                class_name="w-full bg-red-500 text-white font-semibold py-2 rounded-md hover:bg-red-600",
            ),
            on_submit=lambda data: DashboardState.delete_user(data, "student"),
            class_name="space-y-4 border-b pb-4",
        ),
        rx.el.form(
            _user_input("حذف استاذ (باسم المستخدم)", "أدخل اسم المستخدم"),
            rx.el.button(
                "حذف",
                class_name="w-full bg-red-500 text-white font-semibold py-2 rounded-md hover:bg-red-600",
            ),
            on_submit=lambda data: DashboardState.delete_user(data, "teacher"),
            class_name="space-y-4 pt-4",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm",
    )


def _user_input(label: str, placeholder: str) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="text-sm font-medium text-gray-700"),
        rx.el.input(
            placeholder=placeholder,
            class_name="mt-1 block w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md text-sm shadow-sm",
        ),
    )


def _upload_results_card() -> rx.Component:
    return rx.el.div(
        _card_header("رفع النتائج", "upload"),
        rx.el.label(
            "السنة الأكاديمية", class_name="text-sm font-medium text-gray-700 mb-1"
        ),
        rx.el.select(
            rx.foreach(
                DashboardState.academic_years,
                lambda year: rx.el.option(year, value=year),
            ),
            class_name="w-full bg-gray-50 border border-gray-300 rounded-md py-2 px-3 mb-4",
        ),
        rx.el.label(
            "رفع ملف النتائج", class_name="text-sm font-medium text-gray-700 mb-1"
        ),
        rx.upload.root(
            rx.el.div(
                rx.icon("file-archive", class_name="text-gray-400 h-10 w-10"),
                rx.el.p("اسحب الملف هنا أو اضغط للاختيار", class_name="text-gray-500"),
                rx.el.p("PDF أو Excel", class_name="text-xs text-gray-400"),
                class_name="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-lg text-center h-40",
            ),
            class_name="w-full",
        ),
        rx.el.button(
            "رفع النتائج",
            rx.icon("upload", class_name="mr-2"),
            class_name="mt-4 w-full flex items-center justify-center bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm",
    )


def _stats_card() -> rx.Component:
    return rx.el.div(
        _card_header("التقارير والإحصاءات", "bar-chart-2"),
        rx.el.div(
            _stat_item(
                "اجمالي الأساتذة", "78", "bg-green-100 text-green-700", "user-check"
            ),
            _stat_item("اجمالي الطلاب", "1,245", "bg-blue-100 text-blue-700", "users"),
            _stat_item(
                "استخدام التخزين السحابي",
                "65% مستخدم (13GB من 20GB)",
                "bg-yellow-100 text-yellow-700",
                "database",
            ),
            _stat_item(
                "الملفات المرفوعة", "2,310", "bg-purple-100 text-purple-700", "file"
            ),
            class_name="grid grid-cols-2 gap-4",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm",
    )


def _stat_item(label, value, color_class, icon_name) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon_name, class_name="h-6 w-6"),
                class_name=f"p-2 rounded-lg {color_class}",
            ),
            rx.el.p(label, class_name="text-sm font-medium text-gray-500"),
            class_name="flex items-center space-x-2 rtl:space-x-reverse",
        ),
        rx.el.p(value, class_name="text-xl font-bold text-gray-800 mt-1"),
        class_name="bg-gray-50 p-4 rounded-lg",
    )


def _teacher_files_card() -> rx.Component:
    return rx.el.div(
        _card_header("استعراض ملفات الأساتذة", "file-text"),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("اسم الملف", class_name="py-2 px-4 text-right"),
                        rx.el.th("السنة", class_name="py-2 px-4 text-right"),
                        rx.el.th("النوع", class_name="py-2 px-4 text-right"),
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        DashboardState.teacher_files,
                        lambda file: rx.el.tr(
                            rx.el.td(file["name"], class_name="py-2 px-4"),
                            rx.el.td(file["year"], class_name="py-2 px-4"),
                            rx.el.td(
                                rx.el.span(
                                    file["type"],
                                    class_name="px-2 py-1 text-xs font-semibold rounded-full bg-gray-200 text-gray-700",
                                ),
                                class_name="py-2 px-4",
                            ),
                            class_name="border-b",
                        ),
                    )
                ),
                class_name="w-full text-sm",
            ),
            class_name="overflow-x-auto",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm",
    )


def _card_header(title: str, icon_name: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon_name, class_name="text-blue-600"),
        rx.el.h2(title, class_name="font-bold text-lg text-gray-800"),
        class_name="flex items-center space-x-3 rtl:space-x-reverse mb-4",
    )