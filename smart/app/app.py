import reflex as rx
from app.pages.index import index
from app.pages.login import login
from app.pages.signup import signup
from app.pages.teacher_dashboard import teacher_dashboard
from app.pages.supervisor_dashboard import supervisor_dashboard
from app.pages.student_dashboard import student_dashboard
from app.states.auth_state import AuthState
from app.models import create_default_users

app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/")
app.add_page(login, route="/login")
app.add_page(signup, route="/signup")
app.add_page(
    teacher_dashboard, route="/teacher-dashboard", on_load=AuthState.check_auth
)
app.add_page(
    supervisor_dashboard, route="/supervisor-dashboard", on_load=AuthState.check_auth
)
app.add_page(
    student_dashboard, route="/student-dashboard", on_load=AuthState.check_auth
)

# Create default admin user on startup
create_default_users()