import flet as ft
import fitz 
from dotenv import load_dotenv  # Add this import
import os
import base64
from db.controller.data_service import DataService
from ui.components import create_candidate_card
from db.models import init_database, test_connection

# Load environment variables from .env file
load_dotenv()

# APPLICATION CLASS
class CVApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.data_service = DataService()
        init_database() 
        self.keywords_field = None
        self.algorithm_toggle = None
        self.tips_modal_layer = None

        # Modal controls
        self.modal_candidate_name = ft.Text(weight=ft.FontWeight.BOLD, color="white", size=22)
        self.modal_candidate_birthdate = ft.Text(color="#d3d3d3", size=12)
        self.modal_candidate_address = ft.Text(color="#d3d3d3", size=12)
        self.modal_candidate_phone = ft.Text(color="#d3d3d3", size=12)
        self.modal_skills_list = ft.Row(wrap=True, spacing=8)
        self.modal_summary_text = ft.Column(spacing=8)
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
            text_align=ft.TextAlign.CENTER,
            text_style=ft.TextStyle(color="white"),
        )
        self.total_cv_text = ft.Text("0 CV", color="white", size=24, weight=ft.FontWeight.BOLD)
        self.exact_time = 0
        self.fuzzy_time = 0
        self.exact_time_text = ft.Text(f"{self.exact_time} ms", color="white", weight=ft.FontWeight.BOLD)
        self.fuzzy_time_text = ft.Text(f"{self.fuzzy_time} ms", color="white", weight=ft.FontWeight.BOLD)

        # view CV modal
        self.pdf_modal_layer = None
        self.pdf_images_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
        self.pdf_modal_title = ft.Text("", weight=ft.FontWeight.BOLD, size=20, color="black")
        self.pdf_loading_indicator = ft.ProgressRing(width=50, height=50, stroke_width=4)
        self.pdf_error_text = ft.Text("", color="red", size=16)

    # Modal layer
    def open_summary_modal(self, e, candidate_data):
        # print(f"Opening summary for: {candidate_data['name']}") # debug

        # Profile
        self.modal_candidate_name.value = candidate_data['first_name'] + " " + candidate_data['last_name']
        self.modal_candidate_birthdate.value = f"Birthdate: {candidate_data['birthdate'].strftime('%d-%m-%Y')}"
        self.modal_candidate_address.value = f"Address: {candidate_data['address']}"
        self.modal_candidate_phone.value = f"Phone: {candidate_data['phone']}"
        
        # Skills
        self.modal_skills_list.controls.clear()
        skills = self.data_service.get_skills_by_application_id(candidate_data["application_id"])
        for skill in skills:
            self.modal_skills_list.controls.append(
                ft.Container(
                    content=ft.Text(skill, color="white", size=12),
                    bgcolor="#4E4E6A",
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=15
                )
            )

        # Summary
        self.modal_summary_text.controls.clear()
        summaries = self.data_service.get_summary_by_application_id(candidate_data["application_id"])
        for summary in summaries:
            self.modal_summary_text.controls.append(
                ft.Column(
                    [ft.Text(summary['text'], color="white", size=14, weight=ft.FontWeight.NORMAL)],
                    spacing=5
                )
            )
            

        # Job History
        self.modal_job_history_list.controls.clear()
        jobs = self.data_service.get_job_history_by_application_id(candidate_data["application_id"])
        for job in jobs:
             self.modal_job_history_list.controls.append(
                ft.Column([
                    ft.Text(job['position'], color="white", weight=ft.FontWeight.BOLD),
                    ft.Text(f"{job['company']} ({job['period']})", color="#d3d3d3", size=12),
                ])
             )

        # Education
        self.modal_education_list.controls.clear()
        educations = self.data_service.get_education_by_application_id(candidate_data["application_id"])
        for edu in educations:
            self.modal_education_list.controls.append(
                ft.Column([
                    ft.Text(edu['degree'], color="white", weight=ft.FontWeight.BOLD),
                    ft.Text(f"{edu['institution']} ({edu['period']})", color="#d3d3d3", size=12),
                ])
            )
            
        self.modal_layer.visible = True
        self.page.update()

    def open_view_cv_modal(self, e, candidate_data, pdf_path):
        """Open modal to view CV PDF as images"""
        try:
            # Clear previous content
            self.pdf_images_column.controls.clear()
            self.pdf_error_text.value = ""
            
            # Set modal title
            candidate_name = f"{candidate_data['first_name']} {candidate_data['last_name']}"
            self.pdf_modal_title.value = f"CV - {candidate_name}"
            
            # Show loading indicator
            self.pdf_images_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        self.pdf_loading_indicator,
                        ft.Text("Loading PDF...", color="white", size=16)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    height=200
                )
            )
            
            # Show modal
            self.pdf_modal_layer.visible = True
            self.page.update()

            
            if pdf_path and os.path.exists(pdf_path):
                self.convert_and_display_pdf(pdf_path)
            else:
                self.show_pdf_error("PDF file not found")
                
        except Exception as e:
            self.show_pdf_error(f"Error opening CV: {str(e)}")

    def convert_and_display_pdf(self, pdf_path):
        """Convert PDF to images and display them"""
        try:
            # Clear loading indicator
            self.pdf_images_column.controls.clear()
            
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(pdf_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                
                # Convert page to image with high quality
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                
                # Convert pixmap to bytes
                img_data = pix.tobytes("png")
                
                # Convert to base64 for display in Flet
                img_base64 = base64.b64encode(img_data).decode()
                
                # Create image container
                image_container = ft.Container(
                    content=ft.Image(
                        src_base64=img_base64,
                        width=700,
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=5
                    ),
                    bgcolor="white",
                    border_radius=5,
                    padding=10,
                    margin=ft.margin.only(bottom=10)
                )
                
                # Add page number label
                page_label = ft.Container(
                    content=ft.Text(
                        f"Page {page_num + 1} of {len(pdf_document)}", 
                        color="white", 
                        size=12,
                        weight=ft.FontWeight.BOLD
                    ),
                    bgcolor="#4E4E6A",
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=5,
                    margin=ft.margin.only(bottom=5)
                )
                
                self.pdf_images_column.controls.append(page_label)
                self.pdf_images_column.controls.append(image_container)
            
            pdf_document.close()
            self.page.update()
            
        except Exception as e:
            self.show_pdf_error(f"Error converting PDF: {str(e)}")

    def show_pdf_error(self, error_message):
        """Show error message in PDF modal"""
        self.pdf_images_column.controls.clear()
        self.pdf_error_text.value = error_message
        
        error_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color="red", size=50),
                self.pdf_error_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            height=200
        )
        
        self.pdf_images_column.controls.append(error_container)
        self.page.update()

    def close_pdf_modal(self, e):
        """Close PDF modal"""
        self.pdf_modal_layer.visible = False
        self.page.update()

    def _build_pdf_modal_layer(self):
        """Build PDF viewer modal layer"""
        return ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.8, "black"),
            visible=False,
            on_click=self.close_pdf_modal,
            content=ft.Container(
                width=800,
                height=600,
                bgcolor="#f1f1f1",
                border_radius=10,
                padding=ft.padding.symmetric(vertical=15, horizontal=25),
                on_click=lambda e: None,  # Prevent modal from closing when clicking inside
                content=ft.Column(
                    [
                        # Header
                        ft.Row(
                            [
                                self.pdf_modal_title,
                                ft.IconButton(
                                    ft.Icons.CLOSE, 
                                    on_click=self.close_pdf_modal, 
                                    icon_color="black"
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        # PDF Content
                        ft.Container(
                            content=self.pdf_images_column,
                            bgcolor="#1e1e2f",
                            border_radius=10,
                            padding=15,
                            expand=True
                        )
                    ],
                    spacing=15,
                    expand=True
                )
            )
        )

    def close_modal(self, e):
        self.modal_layer.visible = False
        self.page.update()

    def open_tips_modal(self, e):
        self.tips_modal_layer.visible = True
        self.page.update()

    def close_tips_modal(self, e):
        self.tips_modal_layer.visible = False
        self.page.update()

    # Search function
    def search_click(self, e):
        raw_text = self.keywords_field.value
        keywords = [k.strip() for k in raw_text.split(',') if k.strip()]

        try:
            top_n = int(self.top_matches_input.value)
        except (ValueError, TypeError):
            top_n = 5

        selected_algorithm = self.algorithm_toggle.value
        
        top_candidates, self.exact_time, self.fuzzy_time = self.data_service.search_candidates(
            keywords=keywords,
            top_n=top_n,
            algorithm=selected_algorithm
        )
        self.exact_time = int(1000 * self.exact_time)  # Convert to milliseconds
        self.fuzzy_time = int(1000 * self.fuzzy_time)
        self.exact_time_text.value = f"{self.exact_time} ms"
        self.fuzzy_time_text.value = f"{self.fuzzy_time} ms"

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
                    on_summary_click_callback=self.open_summary_modal,
                    on_view_cv_click_callback=self.open_view_cv_modal
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
                        # Summary container
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Summary", color="white", weight=ft.FontWeight.BOLD, size=16),
                                self.modal_summary_text
                            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=10),
                            expand=2, bgcolor="#1e1e2f", border_radius=10, padding=15
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
        
    def _build_tips_modal_layer(self):
        def create_algorithm_card(name, description_list):
            def _on_hover(e):
                is_hovering = e.data == "true"
                card_content.visible = not is_hovering
                card_description.visible = is_hovering
                card_container.bgcolor = "#3a3a50" if is_hovering else "#f1f1f1"
                card_container.shadow = ft.BoxShadow(
                    spread_radius=2, blur_radius=10, color=ft.Colors.with_opacity(0.3, "black"),
                ) if is_hovering else None
                # card_container.scale = ft.Transform.Scale(1.03) if is_hovering else ft.Transform.Scale(1)
                card_container.update()

            card_content = ft.Container(
                content=ft.Text(name, color="black", size=16, weight=ft.FontWeight.BOLD),
                alignment=ft.alignment.center,
                expand=True
            )

            def create_bullet(text):
                return ft.Row([
                    ft.Text("•", color="white", size=12),
                    ft.Text(text, color="white", size=12, expand=True)
                ], spacing=5)

            card_description = ft.Container(
                padding=10,
                content=ft.Column([create_bullet(desc) for desc in description_list], spacing=5),
                visible=False,
                alignment=ft.alignment.top_left,
                expand=True,
            )
            
            card_container = ft.Container(
                content=ft.Stack([card_content, card_description]),
                width=230,
                height=230,
                bgcolor="#f1f1f1",
                border_radius=10,
                padding=15,
                on_hover=_on_hover,
                expand=True,
            )
            return card_container

        def create_bullet_point(text_content, is_bold=False):
            return ft.Row(
                controls=[
                    ft.Text("•", color="white", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        text_content, color="white", size=13,
                        weight=ft.FontWeight.BOLD if is_bold else ft.FontWeight.NORMAL,
                    ),
                ],
                spacing=10
            )

        kmp_desc = ["Cara Kerja: Memanfaatkan kegagalan untuk menghindari perbandingan yang tidak perlu.", "Kelebihan: Sangat efisien, tidak pernah menggeser pointer teks ke belakang.", "Penggunaan: Pilihan stabil dan andal untuk penggunaan umum."]
        bm_desc = ["Cara Kerja: Mencocokkan pattern dari belakang ke depan, melakukan lompatan besar.", "Kelebihan: Umumnya algoritma tercepat, terutama untuk pattern panjang.", "Penggunaan: Pilihan terbaik untuk pattern panjang dalam teks besar."]
        ac_desc = ["Cara Kerja: Mencari semua keyword sekaligus dalam sekali jalan.", "Kelebihan: Sangat cepat untuk pencarian multi-pattern.", "Penggunaan: Ideal saat mencari banyak kata kunci secara bersamaan. (Fitur Bonus)"]

        return ft.Container(
            expand=True, alignment=ft.alignment.center, bgcolor=ft.Colors.with_opacity(0.8, "black"),
            visible=False, on_click=self.close_tips_modal,
            content=ft.Container(
                width=800, height=600, bgcolor="#f1f1f1", border_radius=10,
                padding=ft.padding.symmetric(vertical=15, horizontal=25), on_click=lambda e: None,
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Text("Tips", weight=ft.FontWeight.BOLD, size=20, color="black"),
                            ft.IconButton(ft.Icons.CLOSE, on_click=self.close_tips_modal, icon_color="black")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("How to Use", color="white", weight=ft.FontWeight.BOLD, size=16),
                                create_bullet_point("Masukkan Kata Kunci (Keywords): Tulis skill, posisi, atau kriteria lain. Pisahkan dengan koma."),
                                create_bullet_point("Pilih Algoritma yang diinginkan: Pilih antara KMP, BM, atau AC."),
                                create_bullet_point("Tentukan Top Matches: Atur jumlah CV teratas yang ingin ditampilkan."),
                                create_bullet_point("Fuzzy Matching: Jika pencarian exact tidak ada, sistem otomatis mencari kata yang mirip."),
                            ], scroll=ft.ScrollMode.ADAPTIVE, spacing=8),
                            expand=2, bgcolor="#1e1e2f", border_radius=10, padding=15
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Perbedaan Algoritma", color="white", weight=ft.FontWeight.BOLD, size=16),
                                ft.Row(
                                    controls=[
                                        create_algorithm_card("Knuth-Morris-Pratt", kmp_desc),
                                        create_algorithm_card("Boyer-Moore", bm_desc),
                                        create_algorithm_card("Aho-Corasick", ac_desc),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                                )
                            ], spacing=10),
                            expand=3, bgcolor="#1e1e2f", border_radius=10, padding=15
                        ),
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
        
        self.algorithm_toggle = ft.RadioGroup(
            value="BM",  # Default algorithm
            content=ft.Row(
                [
                    ft.Radio(value="KMP", label="KMP", label_style=ft.TextStyle(color="white"), active_color="#ED6C35"),
                    ft.Radio(value="BM", label="BM", label_style=ft.TextStyle(color="white"), active_color="#ED6C35"),
                    ft.Radio(value="AC", label="AC", label_style=ft.TextStyle(color="white"), active_color="#ED6C35"),
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY
            )
        )

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
                            padding=ft.padding.symmetric(vertical=12, horizontal=10),
                            content=self.algorithm_toggle
                        ),
                        ft.Container(
                            expand=True,
                            bgcolor="#1e1e2f", 
                            border_radius=8,
                            padding=ft.padding.symmetric(vertical=4),
                            content=ft.Row(
                                [
                                    ft.IconButton(ft.Icons.REMOVE, on_click=lambda e: self.change_top_matches(-1), icon_color="white"),
                                    self.top_matches_input,
                                    ft.IconButton(ft.Icons.ADD, on_click=lambda e: self.change_top_matches(1), icon_color="white"),
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
                                    self.exact_time_text
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
                                    self.fuzzy_time_text
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
                    expand=True, bgcolor="#9497AE", border_radius=10, padding=15, alignment=ft.alignment.center, on_click=self.open_tips_modal, ink=True
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
        self.tips_modal_layer = self._build_tips_modal_layer()
        self.pdf_modal_layer = self._build_pdf_modal_layer()  # Add this line
        left_column = self._build_left_column()
        right_column = self._build_right_column()

        self.page.overlay.append(self.modal_layer)
        self.page.overlay.append(self.tips_modal_layer)
        self.page.overlay.append(self.pdf_modal_layer)  # Add this line
        
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