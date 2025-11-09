import reflex as rx
from app.states.auth_state import AuthState


def login() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                _login_tabs(),
                rx.el.form(
                    rx.cond(
                        AuthState.login_role == "student",
                        _student_login_form(),
                        _teacher_supervisor_login_form(),
                    ),
                    rx.el.button(
                        "تسجيل الدخول",
                        type="submit",
                        class_name="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors mt-4",
                    ),
                    rx.el.a(
                        "نسيت كلمة المرور؟",
                        href="#",
                        class_name="block text-center text-sm text-blue-600 hover:underline mt-4",
                    ),
                    on_submit=AuthState.login,
                ),
                rx.el.div(
                    rx.el.p("ليس لديك حساب؟", class_name="text-sm text-gray-600"),
                    rx.el.a(
                        "إنشاء حساب جديد",
                        href="/signup",
                        class_name="text-sm text-blue-600 hover:underline",
                    ),
                    class_name="flex items-center justify-center space-x-2 mt-6",
                ),
                class_name="w-full max-w-sm bg-white p-8 rounded-2xl shadow-lg",
            ),
            class_name="flex items-center justify-center min-h-screen bg-sky-100 p-4",
        ),
        dir="rtl",
        class_name="font-['Inter']",
    )


def _login_tabs() -> rx.Component:
    return rx.el.div(
        _tab_button("student", "طالب"),
        _tab_button("teacher", "أستاذ"),
        _tab_button("supervisor", "مشرف"),
        class_name="flex items-center justify-between bg-gray-200 p-1 rounded-full mb-6",
    )


def _tab_button(role: str, text: str) -> rx.Component:
    is_active = AuthState.login_role == role
    return rx.el.button(
        text,
        on_click=lambda: AuthState.set_login_role(role),
        class_name=rx.cond(
            is_active,
            "flex-1 py-2 px-4 rounded-full text-sm font-semibold bg-white text-blue-600 shadow-sm",
            "flex-1 py-2 px-4 rounded-full text-sm font-semibold text-gray-500",
        ),
    )


def _student_login_form() -> rx.Component:
    return rx.el.div(
        _form_input("university_id", "رقم الجامعة", "text"),
        _form_input("password", "كلمة المرور", "password"),
        class_name="space-y-4",
    )


def _teacher_supervisor_login_form() -> rx.Component:
    return rx.el.div(
        _form_input("username", "اسم المستخدم", "text"),
        _form_input("password", "كلمة المرور", "password"),
        class_name="space-y-4",
    )


def _form_input(name: str, placeholder: str, type: str) -> rx.Component:
    return rx.el.div(
        rx.el.label(placeholder, class_name="text-sm font-medium text-gray-700"),
        rx.el.input(
            name=name,
            placeholder=placeholder,
            type=type,
            required=True,
            class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500",
        ),
    )