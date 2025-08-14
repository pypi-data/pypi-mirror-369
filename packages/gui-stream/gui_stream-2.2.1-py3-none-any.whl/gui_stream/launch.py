#!/usr/bin/env python3
from soup_files import UserAppDir
from gui_stream.app_ui.core.select_files import PreferencesApp
from gui_stream.controller_app import Controller, AppMenuBar, create_controller, __version__
from gui_stream.app_ui.run_app import MyApp
from gui_stream.home_page import HomePageApp
from gui_stream.page_convert_pdf import PageConvertPdf
from gui_stream.page_sheets import PageConvertSheet, PageMoveFiles, PageFilesToExcel
from gui_stream.page_images import PageEditImages
from gui_stream.page_ocr import PageRecognizePDF


class MyApplication(MyApp):
    def __init__(self, controller: Controller):
        super().__init__(controller)
        self.controller_app: Controller = controller
        # Páginas de navegação do ‘app’.
        pages = [
            HomePageApp(controller=self.controller_app),
            PageConvertPdf(controller=self.controller_app),
            PageConvertSheet(controller=self.controller_app),
            PageEditImages(controller=self.controller_app),
            PageMoveFiles(controller=self.controller_app),
            PageFilesToExcel(controller=self.controller_app),
            PageRecognizePDF(controller=self.controller_app),
        ]

        self.controller_app.navigator.pages.clear()
        # Adicionar páginas ao navegador.
        for page in pages:
            self.controller_app.add_page(page)
        self.controller_app.go_home_page()
        self.controller_app.set_topbar()

    def set_menu_bar(self):
        """Exibir a barra de ferramentas no topo do app"""
        self.app_bar: AppMenuBar = AppMenuBar(controller=self.controller_app, version=__version__)


def run_app(appname='gui_stream') -> None:
    user_appdir: UserAppDir = UserAppDir(appname)
    prefs_app = PreferencesApp(user_appdir)
    controller = create_controller(prefs_app)
    app = MyApplication(controller)
    app.set_menu_bar()
    app.initUI()
