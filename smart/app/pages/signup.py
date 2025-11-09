import reflex as rx
from app.states.auth_state import AuthState


def signup() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "إنشاء حساب جديد",
                    class_name="text-2xl font-bold text-gray-800 mb-6 text-center",
                ),
                # Tabs for Student and Teacher
                rx.el.div(
                    rx.el.button(
                        "طالب",
                        on_click=AuthState.set_signup_type("student"),
                        class_name=rx.cond(
                            AuthState.signup_type == "student",
                            "flex-1 py-2 px-4 bg-blue-600 text-white font-medium rounded-t-lg",
                            "flex-1 py-2 px-4 bg-gray-200 text-gray-700 font-medium rounded-t-lg hover:bg-gray-300"
                        ),
                    ),
                    rx.el.button(
                        "معلم",
                        on_click=AuthState.set_signup_type("teacher"),
                        class_name=rx.cond(
                            AuthState.signup_type == "teacher",
                            "flex-1 py-2 px-4 bg-blue-600 text-white font-medium rounded-t-lg",
                            "flex-1 py-2 px-4 bg-gray-200 text-gray-700 font-medium rounded-t-lg hover:bg-gray-300"
                        ),
                    ),
                    class_name="flex gap-1 mb-6",
                ),
                # Student Form
                rx.cond(
                    AuthState.signup_type == "student",
                    rx.el.form(
                        rx.el.div(
                            _form_input("full_name", "الاسم الكامل", "text"),
                            _form_input("username", "اسم المستخدم", "text"),
                            _form_input("university_id", "الرقم الجامعي", "text"),
                            _form_input("email", "البريد الإلكتروني", "email"),
                            _form_input("password", "كلمة المرور", "password"),
                            _form_input(
                                "confirm_password", "تأكيد كلمة المرور", "password"
                            ),
                            class_name="space-y-4",
                        ),
                        rx.el.button(
                            "إنشاء حساب طالب",
                            type="submit",
                            class_name="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors mt-6",
                        ),
                        on_submit=AuthState.create_student_account,
                        class_name="w-full",
                    ),
                ),
                # Teacher Form
                rx.cond(
                    AuthState.signup_type == "teacher",
                    rx.el.form(
                        rx.el.div(
                            _form_input("full_name", "الاسم الكامل", "text"),
                            _form_input("username", "اسم المستخدم", "text"),
                            _form_input("university_id", "الرقم الجامعي", "text"),
                            _form_input("email", "البريد الإلكتروني", "email"),
                            _form_input("password", "كلمة المرور", "password"),
                            _form_input(
                                "confirm_password", "تأكيد كلمة المرور", "password"
                            ),
                            class_name="space-y-4",
                        ),
                        rx.el.button(
                            "إنشاء حساب معلم",
                            type="submit",
                            class_name="w-full bg-green-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-green-700 transition-colors mt-6",
                        ),
                        on_submit=AuthState.create_teacher_account,
                        class_name="w-full",
                    ),
                ),
                rx.el.div(
                    rx.el.p("لديك حساب بالفعل؟", class_name="text-sm text-gray-600"),
                    rx.el.a(
                        "تسجيل الدخول",
                        href="/login",
                        class_name="text-sm text-blue-600 hover:underline mr-2",
                    ),
                    class_name="flex items-center justify-center mt-4",
                ),
                class_name="w-full max-w-md bg-white p-8 rounded-2xl shadow-lg",
            ),
            class_name="flex items-center justify-center min-h-screen bg-sky-100 p-4",
        ),
        dir="rtl",
        class_name="font-['Inter']",
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