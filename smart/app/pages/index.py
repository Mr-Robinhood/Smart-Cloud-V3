import reflex as rx


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.icon("cloud", class_name="text-blue-500 w-24 h-24"),
                class_name="p-6 bg-white rounded-full shadow-lg mb-6",
            ),
            rx.el.h1("سمارت كلاود", class_name="text-4xl font-bold text-gray-800 mb-8"),
            rx.el.div(
                rx.el.a(
                    rx.el.button(
                        "إنشاء حساب جديد",
                        class_name="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors",
                    ),
                    href="/signup",
                    class_name="w-full",
                ),
                rx.el.a(
                    rx.el.button(
                        "تسجيل الدخول",
                        class_name="w-full bg-blue-400 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-500 transition-colors",
                    ),
                    href="/login",
                    class_name="w-full",
                ),
                class_name="w-full max-w-xs space-y-4",
            ),
            class_name="flex flex-col items-center justify-center text-center",
        ),
        class_name="font-['Inter'] bg-sky-100 flex items-center justify-center min-h-screen p-4",
        dir="rtl",
    )