import reflex as rx
from app.states.supervisor_state import SupervisorState
from app.states.auth_state import AuthState


def section_title(text: str):
    return rx.heading(text, size="5", margin_bottom="8px")


def users_table(title: str, items, is_teacher: bool = False):
    cols = ["Username", "Email", "University ID", "Actions"]
    header = rx.table.row(*[rx.table.column_header_cell(c) for c in cols])

    def render_row(u):
        return rx.table.row(
            rx.table.cell(u.username),
            rx.table.cell(u.email),
            rx.table.cell(u.university_id),
            rx.table.cell(
                rx.button(
                    "Delete",
                    color_scheme="red",
                    size="1",
                    on_click=SupervisorState.delete_user(u.id),
                )
            ),
        )

    return rx.card(
        rx.vstack(
            section_title(title),
            # ✅ Scrollable table container
            rx.box(
                rx.table.root(
                    rx.table.header(header),
                    rx.cond(
                        items.length() > 0,
                        rx.table.body(rx.foreach(items, render_row)),
                        rx.table.body(
                            rx.table.row(
                                rx.table.cell("No data", col_span=len(cols))
                            )
                        ),
                    ),
                    variant="surface",
                    size="1",
                ),
                overflow_x="auto",
                width="100%",
                max_width="100%",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        size="1",
        width="100%",
    )



def whitelist_form_students():
    return rx.card(
        rx.vstack(
            section_title("Whitelist: Students"),
            rx.text("Enter student numbers (comma-separated). Must be 6 digits."),
            rx.hstack(
                rx.input(
                    placeholder="e.g. 123456, 234567, 345678",
                    value=SupervisorState.new_student_numbers,
                    on_change=SupervisorState.set_new_student_numbers,
                    width="100%",
                ),
                rx.button(
                    "Add",
                    on_click=SupervisorState.add_allowed_students,
                    color_scheme="green",
                ),
                spacing="3",
                width="100%",
            ),
            whitelist_table_students(),
            spacing="3",
            align="start",
            width="100%",
        ),
        size="3",
        width="100%",
    )


def whitelist_table_students():
    cols = ["Student number", "Registered", "Added date"]
    header = rx.table.row(*[rx.table.column_header_cell(c) for c in cols])
    
    def render_row(s):
        return rx.table.row(
            rx.table.cell(s.student_number),
            rx.table.cell(rx.cond(s.is_registered, "Yes", "No")),
            rx.table.cell(s.added_date),
        )
    
    return rx.table.root(
        rx.table.header(header),
        rx.cond(
            SupervisorState.allowed_students.length() > 0,
            rx.table.body(rx.foreach(SupervisorState.allowed_students, render_row)),
            rx.table.body(
                rx.table.row(rx.table.cell("No students in whitelist", col_span=len(cols)))
            ),
        ),
        variant="surface",
        size="3",
        width="100%",
    )


def whitelist_form_teachers():
    return rx.card(
        rx.vstack(
            section_title("Whitelist: Teachers"),
            rx.text("Enter teacher emails (comma-separated). Must end with @nilevalley.edu.sd"),
            rx.hstack(
                rx.input(
                    placeholder="e.g. a@nilevalley.edu.sd, b@nilevalley.edu.sd",
                    value=SupervisorState.new_teacher_emails,
                    on_change=SupervisorState.set_new_teacher_emails,
                    width="100%",
                ),
                rx.button(
                    "Add",
                    on_click=SupervisorState.add_allowed_teachers,
                    color_scheme="green",
                ),
                spacing="3",
                width="100%",
            ),
            whitelist_table_teachers(),
            spacing="3",
            align="start",
            width="100%",
        ),
        size="3",
        width="100%",
    )


def whitelist_table_teachers():
    cols = ["Email", "Registered", "Added date"]
    header = rx.table.row(*[rx.table.column_header_cell(c) for c in cols])
    
    def render_row(t):
        return rx.table.row(
            rx.table.cell(t.university_email),
            rx.table.cell(rx.cond(t.is_registered, "Yes", "No")),
            rx.table.cell(t.added_date),
        )
    
    return rx.table.root(
        rx.table.header(header),
        rx.cond(
            SupervisorState.allowed_teachers.length() > 0,
            rx.table.body(rx.foreach(SupervisorState.allowed_teachers, render_row)),
            rx.table.body(
                rx.table.row(rx.table.cell("No teachers in whitelist", col_span=len(cols)))
            ),
        ),
        variant="surface",
        size="3",
        width="100%",
    )

def navbar():
    return rx.hstack(
        # ✅ Right side: Arabic navigation buttons
        rx.hstack(
            rx.button("إدارة المستخدمين", variant="ghost"),
            rx.button("النتائج", variant="ghost"),
            rx.button("الملفات", variant="ghost"),
            rx.button("حالة النظام", variant="ghost"),
            spacing="4",
        ),

        # ✅ Left side: App title + Logout
        rx.hstack(
            rx.heading("نظام المشرف", size="5", color="blue.600"),
            rx.button(
                "تسجيل الخروج",
                on_click=AuthState.logout,
                color_scheme="red",
            ),
            spacing="3",
        ),

        justify="between",
        align="center",
        padding="16px",
        background_color="gray.100",
        border_bottom="1px solid #ddd",
        width="100%",
        direction="row-reverse",   # 👈 aligns layout right-to-left
        font_family="'Cairo', sans-serif",
        position="sticky",  # stays at top on scroll
        top="0",
        z_index="1000",
    )


def supervisor_dashboard():
    return rx.vstack(
         # ✅ Navbar first
        navbar(),
        # Header
        rx.hstack(
            section_title("Supervisor Dashboard"),
            rx.button(
                "Logout",
                on_click=AuthState.logout,
                color_scheme="red",
            ),
            justify="between",
            width="100%",
        ),
        
        # User management section
        rx.button(
            "Load All Users",
            on_click=SupervisorState.load_all_users,
            color_scheme="blue",
        ),
        users_table("Students", SupervisorState.all_students),
        users_table("Teachers", SupervisorState.all_teachers, is_teacher=True),
        
        # Whitelist sections
        whitelist_form_students(),
        whitelist_form_teachers(),
        
        spacing="4",
        align="start",
        width="100%",
        padding="20px",
    )