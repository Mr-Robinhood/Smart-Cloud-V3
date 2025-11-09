import reflex as rx


class DashboardState(rx.State):
    """State for the dashboards."""

    academic_years: list[str] = [
        "السنة الأولى - الفصل الأول",
        "السنة الأولى - الفصل الثاني",
        "السنة الثانية",
        "السنة الثالثة",
    ]
    teacher_files: list[dict[str, str]] = [
        {"name": "محاضرة 1 - البرمجة", "year": "السنة الثانية", "type": "PDF"},
        {"name": "واجب الرياضيات", "year": "السنة الأولى", "type": "Word"},
        {"name": "مشروع قواعد البيانات", "year": "السنة الثالثة", "type": "ZIP"},
    ]

    @rx.event
    def delete_user(self, form_data: dict, role: str):
        """Placeholder for deleting a user."""
        identifier = list(form_data.values())[0]
        yield rx.toast.info(f"Attempting to delete {role}: {identifier}")