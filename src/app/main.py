import flet as ft
from db.controller.data_service import DataService
from ui.components import create_candidate_card
from ui.pages import setup_page
from app import CVApp

def main(page: ft.Page):
    setup_page(page)
    app = CVApp(page)
    app.build()

if __name__ == "__main__":
    ft.app(target=main)