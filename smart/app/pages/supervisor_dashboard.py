import reflex as rx
from app.states.supervisor_state import SupervisorState
from app.states.auth_state import AuthState
from app.states.file_state import FileState


def section_title(text: str):
    return rx.heading(text, size="5", margin_bottom="8px")


# ========== STATISTICS DASHBOARD ==========
def stats_section():
    """Dashboard statistics overview."""
    return rx.card(
        rx.vstack(
            section_title("إحصائيات النظام"),
            rx.hstack(
                # Students stat
                rx.card(
                    rx.vstack(
                        rx.icon("users", size=40, color="blue.500"),
                        rx.text("عدد الطلاب", size="2", color="gray"),
                        rx.heading(SupervisorState.total_students, size="6", color="blue.600"),
                        align="center",
                        spacing="2",
                    ),
                    size="2",
                ),
                # Teachers stat
                rx.card(
                    rx.vstack(
                        rx.icon("user", size=40, color="green.500"),
                        rx.text("عدد الأساتذة", size="2", color="gray"),
                        rx.heading(SupervisorState.total_teachers, size="6", color="green.600"),
                        align="center",
                        spacing="2",
                    ),
                    size="2",
                ),
                # Allowed students
                rx.card(
                    rx.vstack(
                        rx.icon("user-check", size=40, color="purple.500"),
                        rx.text("أرقام مسموحة (طلاب)", size="2", color="gray"),
                        rx.heading(SupervisorState.total_allowed_students, size="6", color="purple.600"),
                        align="center",
                        spacing="2",
                    ),
                    size="2",
                ),
                # Allowed teachers
                rx.card(
                    rx.vstack(
                        rx.icon("mail", size=40, color="orange.500"),
                        rx.text("إيميلات مسموحة (أساتذة)", size="2", color="gray"),
                        rx.heading(SupervisorState.total_allowed_teachers, size="6", color="orange.600"),
                        align="center",
                        spacing="2",
                    ),
                    size="2",
                ),
                spacing="4",
                width="100%",
                wrap="wrap",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        width="100%",
        style={"direction": "rtl", "textAlign": "right"}
    )


# ========== USERS TABLE ==========
def users_table(title: str, items, is_teacher: bool = False):
    cols = ["الاسم", "الايميل", "ID", "Actions"]
    header = rx.table.row(*[rx.table.column_header_cell(c) for c in cols])

    def render_row(u):
        return rx.table.row(
            rx.table.cell(u.username),
            rx.table.cell(u.email),
            rx.table.cell(u.university_id),
            rx.table.cell(
                rx.button(
                    "حذف",
                    color_scheme="red",
                    size="1",
                    on_click=SupervisorState.delete_user(u.id),
                )
            ),
        )

    return rx.card(
        rx.vstack(
            section_title(title),
            rx.box(
                rx.table.root(
                    rx.table.header(header),
                    rx.cond(
                        items.length() > 0,
                        rx.table.body(rx.foreach(items, render_row)),
                        rx.table.body(
                            rx.table.row(
                                rx.table.cell("لا توجد بيانات", col_span=len(cols))
                            )
                        ),
                    ),
                    variant="surface",
                    size="1",
                ),
                overflow_x="auto",
                width="100%",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        size="1",
        width="100%",
        style={"direction": "rtl", "textAlign": "right"}
    )


# ========== WHITELIST FORMS ==========
def whitelist_form_students():
    return rx.card(
        rx.vstack(
            section_title("جدول: الطلاب المسموح لهم"),
            rx.text("ادخل الرقم الجامعي للطالب (6 أرقام)"),
            rx.hstack(
                rx.input(
                    placeholder="مثال: 123456, 234567, 345678",
                    value=SupervisorState.new_student_numbers,
                    on_change=SupervisorState.set_new_student_numbers,
                    width="100%",
                ),
                rx.button(
                    "إضافة",
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
        style={"direction": "rtl", "textAlign": "right"}
    )


def whitelist_table_students():
    cols = ["رقم الطالب", "مسجل", "تاريخ الإضافة"]
    header = rx.table.row(*[rx.table.column_header_cell(c) for c in cols])

    def render_row(s):
        return rx.table.row(
            rx.table.cell(s.student_number),
            rx.table.cell(rx.cond(s.is_registered, "نعم", "لا")),
            rx.table.cell(s.added_date),
        )

    return rx.table.root(
        rx.table.header(header),
        rx.cond(
            SupervisorState.allowed_students.length() > 0,
            rx.table.body(rx.foreach(SupervisorState.allowed_students, render_row)),
            rx.table.body(
                rx.table.row(rx.table.cell("لا يوجد طلاب في القائمة", col_span=len(cols)))
            ),
        ),
        variant="surface",
        size="3",
        width="100%",
        style={"direction": "rtl", "textAlign": "right"}
    )


def whitelist_form_teachers():
    return rx.card(
        rx.vstack(
            section_title("جدول: الأساتذة المسموح لهم"),
            rx.text("ادخل إيميل الأستاذ (@nilevalley.edu.sd)"),
            rx.hstack(
                rx.input(
                    placeholder="مثال: a@nilevalley.edu.sd",
                    value=SupervisorState.new_teacher_emails,
                    on_change=SupervisorState.set_new_teacher_emails,
                    width="100%",
                ),
                rx.button(
                    "إضافة",
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
        style={"direction": "rtl", "textAlign": "right"}
    )


def whitelist_table_teachers():
    cols = ["الإيميل", "مسجل", "تاريخ الإضافة"]
    header = rx.table.row(*[rx.table.column_header_cell(c) for c in cols])

    def render_row(t):
        return rx.table.row(
            rx.table.cell(t.university_email),
            rx.table.cell(rx.cond(t.is_registered, "نعم", "لا")),
            rx.table.cell(t.added_date),
        )

    return rx.table.root(
        rx.table.header(header),
        rx.cond(
            SupervisorState.allowed_teachers.length() > 0,
            rx.table.body(rx.foreach(SupervisorState.allowed_teachers, render_row)),
            rx.table.body(
                rx.table.row(rx.table.cell("لا يوجد أساتذة في القائمة", col_span=len(cols)))
            ),
        ),
        variant="surface",
        size="3",
        width="100%",
        style={"direction": "rtl", "textAlign": "right"}
    )


# ========== SEMESTER RESULTS UPLOAD ==========
def results_upload_section():
    return rx.card(
        rx.vstack(
            section_title("رفع نتائج الفصل الدراسي"),
            rx.text("قم برفع ملف النتائج (Excel/PDF) للفصل الدراسي"),
            
            # Semester selector
            rx.hstack(
                rx.text("اختر الفصل:", font_weight="bold"),
                rx.select(
                    SupervisorState.semesters,
                    value=SupervisorState.result_semester,
                    on_change=SupervisorState.set_result_semester,
                    width="200px",
                ),
                spacing="3",
            ),
            
            # Description input
            rx.input(
                placeholder="وصف النتيجة (مثال: نتائج نهائية - دور أول)",
                value=SupervisorState.result_description,
                on_change=SupervisorState.set_result_description,
                width="100%",
            ),
            
            # File upload
            rx.upload(
                rx.el.div(
                    rx.icon("cloud_upload", class_name="text-blue-500 h-10 w-10"),
                    rx.el.p("اختر ملف النتائج", class_name="font-semibold text-gray-700"),
                    rx.el.p("Excel أو PDF", class_name="text-sm text-gray-500"),
                    rx.vstack(
                        rx.foreach(rx.selected_files("upload_result"), rx.text),
                    ),
                    class_name="flex flex-col items-center justify-center p-6 bg-blue-50 border-2 border-dashed border-blue-200 rounded-lg text-center h-40",
                ),
                id="upload_result",
                class_name="w-full cursor-pointer",
            ),
            
            # Upload button
            rx.button(
                "رفع النتيجة",
                on_click=SupervisorState.upload_semester_result(
                    rx.upload_files(upload_id="upload_result")
                ),
                color_scheme="green",
                size="3",
            ),
            
            spacing="4",
            width="100%",
        ),
        size="3",
        width="100%",
        style={"direction": "rtl", "textAlign": "right"}
    )


# ========== FILE MANAGEMENT ==========
def files_management_section():
    """View and delete files uploaded by teachers."""
    return rx.card(
        rx.vstack(
            section_title("إدارة الملفات المرفوعة"),
            rx.text("عرض وحذف الملفات التي رفعها الأساتذة"),
            
            rx.button(
                "تحميل جميع الملفات",
                color_scheme="blue",
            ),
            
            # Files table
            rx.cond(
                FileState.uploaded_files.length() > 0,
                files_table(),
                rx.text("لا توجد ملفات", color="gray"),
            ),
            
            spacing="3",
            width="100%",
        ),
        size="3",
        width="100%",
        style={"direction": "rtl", "textAlign": "right"}
    )


def files_table():
    cols = ["اسم الملف", "الفصل", "النوع", "رفع بواسطة", "التاريخ", "الحجم", "إجراءات"]
    header = rx.table.row(*[rx.table.column_header_cell(c) for c in cols])

    def render_row(file):
        return rx.table.row(
            rx.table.cell(file.file_description),
            rx.table.cell(file.semester),
            rx.table.cell(file.file_type),
            rx.table.cell(file.uploaded_by),
            rx.table.cell(file.upload_date),
            rx.table.cell(file.file_size),
            rx.table.cell(
                rx.button(
                    "حذف",
                    color_scheme="red",
                    size="1",
                    on_click=SupervisorState.delete_file(file.id),
                )
            ),
        )

    return rx.table.root(
        rx.table.header(header),
        rx.table.body(rx.foreach(FileState.uploaded_files, render_row)),
        variant="surface",
        size="2",
        width="100%",
        style={"direction": "rtl", "textAlign": "right"}
    )


# ========== NAVBAR ==========
def supervisor_navbar():
    brand_section = rx.hstack(
        rx.heading("نظام المشرف", size="5", color="blue.600"),
        rx.button(
            "تسجيل الخروج",
            on_click=AuthState.logout,
            color_scheme="red",
            variant="soft",
            display={"base": "none", "md": "flex"}
        ),
        spacing="4",
        align="center",
        direction="row-reverse",
    )

    mobile_nav = rx.menu.root(
        rx.menu.trigger(
            rx.icon(tag="menu", size=28, cursor="pointer"),
        ),
        rx.menu.content(
            rx.menu.item("تسجيل الخروج", on_select=AuthState.logout, color="red.600"),
            align="end",
            style={"direction": "rtl", "textAlign": "right"}
        ),
        display={"base": "flex", "md": "none"}
    )

    return rx.hstack(
        rx.box(mobile_nav),
        brand_section,
        justify="between",
        align="center",
        padding_y="12px",
        padding_x="16px",
        background_color="gray.100",
        border_bottom="1px solid #ddd",
        width="100%",
        direction="row-reverse",
        position="sticky",
        top="0",
        z_index="1000",
    )


# ========== MAIN DASHBOARD ==========
def supervisor_dashboard():
    return rx.vstack(
        supervisor_navbar(),
        
        # Statistics at top
        stats_section(),
        
        # User Management
        rx.heading("إدارة المستخدمين", size="6", margin_top="20px"),
        rx.button(
            "تحميل المستخدمين",
            on_click=SupervisorState.load_all_users,
            color_scheme="blue",
        ),
        users_table("الطلاب", SupervisorState.all_students),
        users_table("الأساتذة", SupervisorState.all_teachers, is_teacher=True),
        
        # Whitelists
        rx.heading("إدارة القوائم المسموحة", size="6", margin_top="20px"),
        rx.button(
            "تحميل القوائم",
            on_click=[
                SupervisorState.load_allowed_students,
                SupervisorState.load_allowed_teachers,
            ],
            color_scheme="blue",
        ),
        whitelist_form_students(),
        whitelist_form_teachers(),
        
        # Results Upload
        rx.heading("إدارة النتائج", size="6", margin_top="20px"),
        results_upload_section(),
        
        # Files Management
        rx.heading("إدارة الملفات", size="6", margin_top="20px"),
        files_management_section(),
        
        spacing="4",
        align="start",
        width="100%",
        padding="20px",
        on_mount=[
            SupervisorState.load_all_users,
            SupervisorState.load_allowed_students,
            SupervisorState.load_allowed_teachers,
        ],
    )