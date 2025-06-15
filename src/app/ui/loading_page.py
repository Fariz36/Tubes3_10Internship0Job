import flet as ft
from itertools import cycle

def create_loading_view():
    loading_texts_iterator = cycle([
        "Loading data...",
        "Analyzing database...",
        "Searching for candidates...",
        "Filtering candidates..."
    ])

    status_text = ft.Text(
        value=next(loading_texts_iterator),
        size=16,
        color=ft.Colors.WHITE,
        text_align=ft.TextAlign.CENTER,
        width=300
    )

    progress_ring = ft.ProgressRing(
        width=32,
        height=32,
        stroke_width=4,
        color="#ED6C35"  
    )

    loading_view = ft.Column(
        controls=[
            ft.Text("10Internship0Job ATS", size=40, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(height=20),
            progress_ring,
            ft.Container(height=10),
            status_text,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )

    return loading_view, status_text, loading_texts_iterator