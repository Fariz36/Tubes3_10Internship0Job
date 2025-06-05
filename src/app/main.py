import flet as ft

def main(page: ft.Page):
    page.title = "CV Analyzer App"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.bgcolor = "#FFFFFF"
    
    # Keywords input
    keywords_field = ft.TextField(
        value="React, Express, HTML",
        width=800,
        height=50,
        bgcolor="#E5E7EB",
        border_radius=5,
        content_padding=ft.padding.all(15)
    )
    
    # Search algorithm slider
    algorithm_slider = ft.Slider(
        min=0,
        max=1,
        divisions=1,
        value=0,
        width=200,
        active_color="#6B7280",
        thumb_color="#374151"
    )
    
    # Top matches dropdown
    matches_dropdown = ft.Dropdown(
        value="3",
        width=100,
        options=[
            ft.dropdown.Option("1"),
            ft.dropdown.Option("2"),
            ft.dropdown.Option("3"),
            ft.dropdown.Option("5"),
            ft.dropdown.Option("10"),
        ],
        bgcolor="#E5E7EB",
        border_radius=5
    )
    
    # Results container
    results_container = ft.Column(spacing=15)
    
    # Search function
    def search_click(e):
        # Clear previous results
        results_container.controls.clear()
        
        # Add results header
        results_container.controls.append(
            ft.Column([
                ft.Text("Results", size=32, weight=ft.FontWeight.BOLD, color="#000000"),
                ft.Text("100 CVs scanned in 100ms", size=14, color="#6B7280")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
        )
        
        # Sample results data
        candidates = [
            {"name": "Farhan", "matches": 4, "keywords": ["React: 1 occurrence", "Express: 2 occurrences", "HTML: 1 occurrence"]},
            {"name": "Aland", "matches": 1, "keywords": ["React: 1 occurrence"]},
            {"name": "Ariel", "matches": 1, "keywords": ["Express: 1 occurrence"]}
        ]
        
        # Create result cards
        result_cards = []
        for candidate in candidates:
            # Create keyword list
            keyword_controls = []
            for i, keyword in enumerate(candidate["keywords"], 1):
                keyword_controls.append(
                    ft.Text(f"{i}. {keyword}", size=12, color="#1F2937")
                )
            
            # Create buttons
            buttons_row = ft.Row([
                ft.ElevatedButton(
                    "Summary",
                    bgcolor="#9CA3AF",
                    color="#000000",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                ),
                ft.ElevatedButton(
                    "View CV",
                    bgcolor="#6B7280",
                    color="#FFFFFF",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                )
            ], spacing=10)
            
            # Create result card
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(candidate["name"], size=18, weight=ft.FontWeight.BOLD, color="#000000"),
                        ft.Text(f"{candidate['matches']} match{'es' if candidate['matches'] > 1 else ''}", 
                               size=12, color="#6B7280")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text("Matched keywords:", size=12, weight=ft.FontWeight.BOLD, color="#000000"),
                    ft.Column(keyword_controls, spacing=2),
                    ft.Container(height=10),
                    buttons_row
                ], spacing=8),
                bgcolor="#E5E7EB",
                border_radius=8,
                padding=15,
                width=280
            )
            result_cards.append(card)
        
        # Add result cards in a row
        results_container.controls.append(
            ft.Row(
                result_cards,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
                scroll=ft.ScrollMode.AUTO
            )
        )
        
        page.update()
    
    # Search button
    search_button = ft.ElevatedButton(
        "Search",
        on_click=search_click,
        width=800,
        height=50,
        bgcolor="#6B7280",
        color="#FFFFFF",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=25)
        )
    )
    
    # Main layout
    page.add(
        ft.Column([
            # Title
            ft.Container(
                ft.Text("CV Analyzer App", size=32, weight=ft.FontWeight.BOLD, color="#000000"),
                margin=ft.margin.only(bottom=30)
            ),
            
            # Keywords section
            ft.Column([
                ft.Text("Keywords :", size=16, weight=ft.FontWeight.BOLD, color="#000000"),
                keywords_field
            ], spacing=10),
            
            # Search algorithm section
            ft.Container(
                ft.Column([
                    ft.Text("Search Algorithm:", size=16, weight=ft.FontWeight.BOLD, color="#000000"),
                    ft.Row([
                        ft.Text("KMP", size=14, color="#000000"),
                        algorithm_slider,
                        ft.Text("BM", size=14, color="#000000")
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                ], spacing=10),
                margin=ft.margin.only(top=20, bottom=20)
            ),
            
            # Top matches section
            ft.Column([
                ft.Text("Top Matches:", size=16, weight=ft.FontWeight.BOLD, color="#000000"),
                matches_dropdown
            ], spacing=10),
            
            # Search button
            ft.Container(
                search_button,
                margin=ft.margin.only(top=30, bottom=30)
            ),
            
            # Results section
            results_container
            
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
    )

ft.app(main)