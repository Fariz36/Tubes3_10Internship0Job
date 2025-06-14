import flet as ft
from dotenv import load_dotenv  # Add this import
import os
from db.controller.data_service import DataService
from ui.components import create_candidate_card
from db.models import init_database

# Load environment variables from .env file
load_dotenv()

# APPLICATION CLASS
class CVApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.data_service = DataService()
        self.keywords_field = None
        self.algorithm_toggle = None
        
        init_database() 

        # Modal controls
        self.modal_candidate_name = ft.Text(weight=ft.FontWeight.BOLD, color="white", size=22)
        self.modal_candidate_birthdate = ft.Text(color="#d3d3d3", size=12)
        self.modal_candidate_address = ft.Text(color="#d3d3d3", size=12)
        self.modal_candidate_phone = ft.Text(color="#d3d3d3", size=12)
        self.modal_skills_list = ft.Row(wrap=True, spacing=8)
        self.modal_job_history_list = ft.Column(spacing=8)
        self.modal_education_list = ft.Column(spacing=8)
        self.results_grid = ft.GridView(
            expand=1,
            runs_count=3,
            child_aspect_ratio=1.1, 
            spacing=20,
            run_spacing=20,
        )
        self.top_matches_input = ft.TextField(
            value="1",
            border_color="#4E4E6A",
            border_radius=10,
            width=70,
            height=50,
            text_align=ft.TextAlign.CENTER
        )
        self.total_cv_text = ft.Text("0 CV", color="white", size=24, weight=ft.FontWeight.BOLD)

    # Modal layer
    def open_summary_modal(self, e, candidate_data):
        print(f"Opening summary for: {candidate_data['name']}") # debug

        # Profile
        self.modal_candidate_name.value = candidate_data['name']
        self.modal_candidate_birthdate.value = f"Birthdate: {candidate_data['birthdate'].strftime('%d-%m-%Y')}"
        self.modal_candidate_address.value = f"Address: {candidate_data['address']}"
        self.modal_candidate_phone.value = f"Phone: {candidate_data['phone']}"
        
        # Skills
        self.modal_skills_list.controls.clear()
        for skill in candidate_data["skills"]:
            self.modal_skills_list.controls.append(
                ft.Container(
                    content=ft.Text(skill, color="white", size=12),
                    bgcolor="#4E4E6A",
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=15
                )
            )

        # Job History
        self.modal_job_history_list.controls.clear()
        for job in candidate_data["job_history"]:
             self.modal_job_history_list.controls.append(
                ft.Column([
                    ft.Text(job['position'], color="white", weight=ft.FontWeight.BOLD),
                    ft.Text(f"{job['company']} ({job['period']})", color="#d3d3d3", size=12),
                ])
             )

        # Education
        self.modal_education_list.controls.clear()
        for edu in candidate_data["education"]:
            self.modal_education_list.controls.append(
                ft.Column([
                    ft.Text(edu['degree'], color="white", weight=ft.FontWeight.BOLD),
                    ft.Text(f"{edu['institution']} ({edu['period']})", color="#d3d3d3", size=12),
                ])
            )
            
        self.modal_layer.visible = True
        self.page.update()

    def close_modal(self, e):
        self.modal_layer.visible = False
        self.page.update()

    # Search function
    def search_click(self, e):
        raw_text = self.keywords_field.value
        keywords = [k.strip() for k in raw_text.split(',') if k.strip()]

        try:
            top_n = int(self.top_matches_input.value)
        except (ValueError, TypeError):
            top_n = 1

        selected_algorithm = "BM" if self.algorithm_toggle.value else "KMP"

        top_candidates = self.data_service.search_candidates(
            keywords=keywords,
            top_n=top_n,
            algorithm=selected_algorithm
        )

        self.results_grid.controls.clear()
        if not top_candidates:
            self.results_grid.controls.append(
                ft.Text(
                    "No candidates found.", 
                    color="white", 
                    size=16, 
                    text_align=ft.TextAlign.CENTER
                )
            )
        else:
            for candidate in top_candidates:
                card = create_candidate_card(
                    candidate_data=candidate,
                    on_summary_click_callback=self.open_summary_modal
                )
                self.results_grid.controls.append(card)   
        
        self.page.update()

    # Top matches input value
    def change_top_matches(self, value):
        current_value = int(self.top_matches_input.value)
        new_value = max(1, current_value + value) 
        self.top_matches_input.value = str(new_value)
        self.page.update()

    # Modal Layer
    def _build_modal_layer(self):
        return ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.8, "black"),
            visible=False,
            on_click=self.close_modal, 
            content=ft.Container(
                width=800,
                height=600,
                bgcolor="#f1f1f1", 
                border_radius=10,
                padding=ft.padding.symmetric(vertical=15, horizontal=25),
                on_click=lambda e: None, 
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("CV Summary", weight=ft.FontWeight.BOLD, size=20, color="black"),
                                ft.IconButton(ft.Icons.CLOSE, on_click=self.close_modal, icon_color="black")
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        # Profile and Skills containers
                        ft.Row(
                            [
                                # Profile column
                                ft.Container(
                                    expand=True, 
                                    content=ft.Column([
                                        ft.Text("Profile", color="white", weight=ft.FontWeight.BOLD, size=16),
                                        # ft.Divider(height=10, color="transparent"),
                                        self.modal_candidate_name,
                                        self.modal_candidate_birthdate,
                                        self.modal_candidate_address,
                                        self.modal_candidate_phone
                                    ], scroll=ft.ScrollMode.ADAPTIVE),
                                    bgcolor="#1e1e2f", border_radius=10, padding=15
                                ),
                                # Skills column
                                ft.Container(
                                    expand=True, 
                                    content=ft.Column([
                                        ft.Text("Skills", color="white", weight=ft.FontWeight.BOLD, size=16),
                                        # ft.Divider(height=10, color="transparent"),
                                        ft.Container(
                                            content=self.modal_skills_list,
                                            expand=True
                                        )
                                    ], scroll=ft.ScrollMode.ADAPTIVE),
                                    bgcolor="#1e1e2f", border_radius=10, padding=15
                                )
                            ],
                            spacing=20,
                            expand=2, 
                            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                        ),
                        # Job History container
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Job History", color="white", weight=ft.FontWeight.BOLD),
                                self.modal_job_history_list
                            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=10),
                            expand=2, bgcolor="#1e1e2f", border_radius=10, padding=15
                        ),
                        # Education container
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Education", color="white", weight=ft.FontWeight.BOLD),
                                self.modal_education_list
                            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=10),
                            expand=2, bgcolor="#1e1e2f", border_radius=10, padding=15
                        )
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH
                )
            )
        )

    # Left column
    def _build_left_column(self):
        # Search controls
        self.keywords_field = ft.TextField(
            hint_text="Enter keywords, separated by commas", 
            border_color="#4E4E6A", 
            height=50, 
            bgcolor="#E5E7EB", 
            border_radius=10, 
            content_padding=ft.padding.symmetric(horizontal=15),
            text_style=ft.TextStyle(color="black"),
            hint_style=ft.TextStyle(color="#888888") 
        )
        self.algorithm_toggle = ft.CupertinoSwitch(value=True, active_color="#ED6C35", inactive_track_color="#ED6C35")
        search_button = ft.Container(
            content=ft.Text("Search", color="white", weight=ft.FontWeight.BOLD),
            height=50, bgcolor="#ED6C35", border_radius=10,
            alignment=ft.alignment.center, on_click=self.search_click
        )

        # Search Panel 
        search_panel = ft.Container(
            content=ft.Column([
                ft.Text("10Internship0Job App", size=24, weight=ft.FontWeight.BOLD, color="white"),
                self.keywords_field,
                ft.Row(
                    controls=[
                        ft.Container(
                            expand=True,
                            bgcolor="#1e1e2f", 
                            border_radius=8,
                            padding=ft.padding.symmetric(vertical=10, horizontal=10),
                            content=ft.Row(
                                [
                                    ft.Text("KMP"),
                                    self.algorithm_toggle,
                                    ft.Text("BM"),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY
                            )
                        ),
                        ft.Container(
                            expand=True,
                            bgcolor="#1e1e2f", 
                            border_radius=8,
                            padding=ft.padding.symmetric(vertical=4),
                            content=ft.Row(
                                [
                                    ft.IconButton(ft.Icons.REMOVE, on_click=lambda e: self.change_top_matches(-1)),
                                    self.top_matches_input,
                                    ft.IconButton(ft.Icons.ADD, on_click=lambda e: self.change_top_matches(1)),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=0
                            )
                        ),
                    ], spacing=15, alignment=ft.MainAxisAlignment.CENTER
                ),
                search_button,
            ], spacing=20)
        )

        # Statistics Panel 
        info_panel = ft.Container(
            expand=True,
            content=ft.Column([
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(name=ft.Icons.FOLDER_OPEN, color="white", size=30),
                            ft.Column(
                                [
                                    self.total_cv_text,
                                    ft.Text("Total Dataset", color="white", size=12),
                                ],
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor="#9497AE", border_radius=10, padding=20
                ),
                ft.Row([
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(name=ft.Icons.SEARCH, color="#90EE90", size=24),
                                ft.Column([
                                    ft.Text("Exact Match", color="white", size=12), 
                                    ft.Text("99 ms", color="white", weight=ft.FontWeight.BOLD)
                                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.START)
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.START,
                            spacing=15
                        ),
                        expand=True, bgcolor="#9497AE", border_radius=10, padding=15
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(name=ft.Icons.WIFI_FIND, color="#FFD700", size=24),
                                ft.Column([
                                    ft.Text("Fuzzy Match", color="white", size=12), 
                                    ft.Text("105 ms", color="white", weight=ft.FontWeight.BOLD)
                                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.START)
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.START,
                            spacing=15
                        ),
                        expand=True, bgcolor="#9497AE", border_radius=10, padding=15
                    ),
                ], spacing=20),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name=ft.Icons.LIGHTBULB_OUTLINE, color="white"),
                        ft.Text("Tips", color="white", size=20, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                    expand=True, bgcolor="#9497AE", border_radius=10, padding=15, alignment=ft.alignment.center
                )
            ], spacing=20),
            bgcolor="#1e1e2f", border_radius=10, padding=25
        )

        return ft.Container(
            col=5,
            content=ft.Column([search_panel, info_panel], spacing=25),
            padding=ft.padding.only(right=25)
        )

    # Right column
    def _build_right_column(self):
        return ft.Container(
            col=7,
            content=ft.Column([
                ft.Text("Result", size=24, weight=ft.FontWeight.BOLD, color="white"),
                self.results_grid
            ], scroll=ft.ScrollMode.ADAPTIVE, expand=True),
            bgcolor="#1e1e2f", border_radius=10, padding=25
        )

    # Main build function
    def build(self):
        self.modal_layer = self._build_modal_layer()
        left_column = self._build_left_column()
        right_column = self._build_right_column()

        self.page.overlay.append(self.modal_layer)
        self.page.add(
            ft.Container(
                content=ft.ResponsiveRow(
                    [left_column, right_column],
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH
                ),
                expand=True 
            )
        )
        total_cvs = self.data_service.get_total_cvs()
        self.total_cv_text.value = f"{total_cvs} CV"
        self.page.update()