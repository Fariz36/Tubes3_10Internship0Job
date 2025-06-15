import flet as ft
import threading
import time
from app import CVApp
from db.controller.data_service import DataService
from ui.pages import setup_page
from ui.loading_page import create_loading_view

def main(page: ft.Page):
    setup_page(page)

    app_context = {"data_service": None}

    def initialize_data():
        service = DataService()
        app_context["data_service"] = service

    def build_main_app():
        page.clean()
        app = CVApp(page, data_service=app_context["data_service"])
        app.build()
        page.update()

    def animate_and_switch():
        loader_thread = threading.Thread(target=initialize_data, daemon=True)
        loader_thread.start()

        while loader_thread.is_alive():
            status_text.value = next(text_iterator)
            page.update()
            time.sleep(2)  

        build_main_app()

    loading_view, status_text, text_iterator = create_loading_view()
    page.add(loading_view)

    threading.Thread(target=animate_and_switch, daemon=True).start()

if __name__ == "__main__":
    ft.app(target=main)