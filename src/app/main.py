import flet as ft

def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.bgcolor = "#14141E"
    
    # Keywords input
    keywords_field = ft.TextField(
        label="Keywords",
        border_color="#4E4E6A",
        height=50,
        bgcolor="#E5E7EB",
        border_radius=10,
        content_padding=ft.padding.symmetric(horizontal=15),
        text_style=ft.TextStyle(color="black"),
        label_style=ft.TextStyle(color="#d3d3d3")
    )

    algorithm_toggle = ft.CupertinoSwitch(
        value=True,
        active_color="#FF8A65",
        inactive_track_color="#FF8A65",
        on_change=lambda e: print("Switch changed"),
    )
    
    # Top matches dropdown
    top_matches_input = ft.TextField(
        value="1",
        border_color="#4E4E6A",
        border_radius=10,
        width=70,
        height=50,
        text_align=ft.TextAlign.CENTER
    )

    def change_top_matches(value):
        current_value = int(top_matches_input.value)
        new_value = max(1, current_value + value) 
        top_matches_input.value = str(new_value)
        page.update()

    # Tombol Search
    search_button = ft.Container(
        content=ft.Text("Search", color="white", weight=ft.FontWeight.BOLD),
        width=300, 
        height=50,
        bgcolor="#FF8A65",
        border_radius=10,
        alignment=ft.alignment.center,
        on_click=lambda e: search_click(e) 
    )
    
    # Results container
    results_grid = ft.GridView(
        expand=1,
        runs_count=3,  
        child_aspect_ratio=1, 
        spacing=20,
        run_spacing=20,
    )
    
    # Search function
    def search_click(e):
        results_grid.controls.clear()
        
        candidates = [
            {"name": "Adha", "matches": 4, "keywords": ["React: 4 occurences", "C++: 7 occurences", "Java: 1 occurence"]},
            {"name": "Budi", "matches": 3, "keywords": ["Python: 5 occurences", "SQL: 2 occurences"]},
            {"name": "Caca", "matches": 2, "keywords": ["HTML: 3 occurences", "CSS: 1 occurence"]},
            {"name": "Deni", "matches": 2, "keywords": ["Flet: 8 occurences", "Python: 1 occurence"]},
            {"name": "Euis", "matches": 1, "keywords": ["JavaScript: 2 occurences"]},
        ]
        
        for candidate in candidates:
            keyword_controls = [
                ft.Text(f"{i}. {kw}", color="#444444", size=12) 
                for i, kw in enumerate(candidate["keywords"], 1)
            ]
            
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(candidate["name"], weight=ft.FontWeight.BOLD, color="black", size=18),
                        ft.Container(
                            content=ft.Text(f"{candidate['matches']} Matched", color="#1e1e2f", size=10, weight=ft.FontWeight.BOLD),
                            bgcolor="#B7E5B4",
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=5
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text("Matched keywords:", color="#444444", size=12, weight=ft.FontWeight.BOLD),
                    ft.Column(keyword_controls, spacing=2),
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton("Summary", bgcolor="#4E4E6A", color="white"),
                        ft.ElevatedButton("View CV", bgcolor="#4E4E6A", color="white")
                    ], spacing=10, alignment=ft.MainAxisAlignment.END)
                ], spacing=8),
                bgcolor="#ffffff",
                border_radius=10,
                padding=20,
            )
            results_grid.controls.append(card)
        page.update()

    # Left Column
    left_column = ft.Container(
        col = 5,
        content=ft.Column([
            # Input Section 
            ft.Container(
                content=ft.Column([
                    ft.Text("10Internship0Job App", size=20, weight=ft.FontWeight.BOLD, color="white"),
                    keywords_field,
                    ft.Row([
                        ft.Text("KMP", color="white"),
                        algorithm_toggle,
                        ft.Text("BM", color="white"),
                        ft.Container(width=20),
                        ft.IconButton(ft.Icons.REMOVE, icon_color="white", on_click=lambda e: change_top_matches(-1)),
                        top_matches_input,
                        ft.IconButton(ft.Icons.ADD, icon_color="white", on_click=lambda e: change_top_matches(1)),
                    ], alignment=ft.MainAxisAlignment.START, spacing=10),
                    search_button,
                ], spacing=20),
                bgcolor="#2A2A3D",
                border_radius=10,
                padding=25
            ),
            
            # Statistics Section
            ft.Container(
                content=ft.Column([
                    # Total Dataset
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(name=ft.Icons.FOLDER_OPEN, color="white"),
                            ft.Text("Total Dataset", color="white", size=12),
                            ft.Text("666 CV", color="white", size=24, weight=ft.FontWeight.BOLD)
                        ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor="#9497AE",
                        border_radius=10,
                        padding=20,
                        alignment=ft.alignment.center
                    ),
                    # Scan Times
                    ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(name=ft.Icons.SPEED, color="#FF8A65"),
                                ft.Column([
                                    ft.Text("Exact Match", color="white", size=12),
                                    ft.Text("99 ms", color="white", weight=ft.FontWeight.BOLD)
                                ])
                            ]),
                            expand=True, bgcolor="#9497AE", border_radius=10, padding=15
                        ),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(name=ft.Icons.RULE, color="#FF8A65"),
                                ft.Column([
                                    ft.Text("Fuzzy Match", color="white", size=12),
                                    ft.Text("105 ms", color="white", weight=ft.FontWeight.BOLD)
                                ])
                            ]),
                            expand=True, bgcolor="#9497AE", border_radius=10, padding=15
                        ),
                    ], spacing=20),
                    # Tips
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(name=ft.Icons.LIGHTBULB_OUTLINE, color="white"),
                            ft.Text("Tips", color="white")
                        ]),
                        expand=True, bgcolor="#9497AE", border_radius=10, padding=15
                    )
                ], spacing=20),
                bgcolor="#2A2A3D",
                border_radius=10,
                padding=25
            )
        ], spacing=25),
        width=400,
        padding=ft.padding.only(right=25)
    )

    # Right Column
    right_column = ft.Container(
        col=7,
        content=ft.Column(
            [
                ft.Text("Result", size=24, weight=ft.FontWeight.BOLD, color="white"),
                results_grid
            ],
            scroll=ft.ScrollMode.ADAPTIVE, 
            expand=True 
        ),
        bgcolor="#2A2A3D",
        border_radius=10,
        padding=25
    )
    
    # Main layout
    page.add(
        ft.ResponsiveRow(
            [
                left_column,
                right_column
            ],
            vertical_alignment=ft.CrossAxisAlignment.START
        )
    )

ft.app(main)