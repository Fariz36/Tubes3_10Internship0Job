import flet as ft
import os
import subprocess

def create_candidate_card(candidate_data, on_summary_click_callback, on_view_cv_click_callback):
    def handle_summary_click(e):
        on_summary_click_callback(e, candidate_data)

    def handle_view_cv_click(e, cv_path):
        on_view_cv_click_callback(e, candidate_data, cv_path)

            
    data = candidate_data.get("matched_keywords", {})

    keyword_controls = [
        ft.Text(f"{i}. {kw}: {count} occurrences", color="#444444", size=12)
        for i, (kw, count) in enumerate(zip(data["keywords"], data["matched_queries"]), 1)
    ]

    card_content = ft.Column([
        ft.Row([
            ft.Container(
                content=ft.Text(
                    candidate_data["first_name"] + " " + candidate_data["last_name"], 
                    weight=ft.FontWeight.BOLD, 
                    color="black", 
                    size=18,
                    overflow=ft.TextOverflow.ELLIPSIS, 
                    no_wrap=True 
                ),
                expand=True 
            ),
            ft.Container(
                content=ft.Text(f"{data['total_matched']} Matched", color="#1e1e2f", size=10, weight=ft.FontWeight.BOLD),
                bgcolor="#B7E5B4", padding=ft.padding.symmetric(horizontal=8, vertical=4), border_radius=5
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Text("Matched keywords:", color="#444444", size=12, weight=ft.FontWeight.BOLD),
        
        ft.Column(
            controls=keyword_controls, 
            spacing=2,
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE
        ),
        
        ft.Row([
            ft.ElevatedButton("Summary", bgcolor="#4E4E6A", color="white", on_click=handle_summary_click),
            ft.ElevatedButton("View CV", bgcolor="#4E4E6A", color="white", on_click=lambda e: handle_view_cv_click(e, candidate_data["cv_path"])),
        ], spacing=10, alignment=ft.MainAxisAlignment.END)
    ], 
    spacing=8,
    expand=True 
    )

    return ft.Container(
        content=card_content,
        bgcolor="#ffffff", 
        border_radius=10, 
        padding=20,
    )