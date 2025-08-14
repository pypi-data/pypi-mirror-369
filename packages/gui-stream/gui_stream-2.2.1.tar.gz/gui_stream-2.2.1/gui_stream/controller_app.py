#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from soup_files import File
from gui_stream.app_ui.core.page import ThreadApp
from gui_stream.app_ui.core.select_files import PreferencesApp, AppFileDialog, ControllerFiles
from gui_stream.app_ui.ui.ui_pages import UiController
from gui_stream.app_ui.ui.ui_menu_bar import UIMenuBar
from gui_stream.app_ui.run_app import load_conf_user
from ocr_stream import BinaryTesseract

__version__ = '2.2'


def create_controller(prefs_app: PreferencesApp) -> Controller:
    """
        Gera uma controller personalizada, priorizando
    as preferências do usuário em detrimento das informações padrão.
    """
    prefs_app = load_conf_user(prefs_app)
    # Definir controller para arquivos
    file_dialog: AppFileDialog = AppFileDialog(prefs_app)
    controller_files: ControllerFiles = ControllerFiles(file_dialog)
    
    # Definir controller do App.
    controller: UiController = Controller(
        controller_files=controller_files, pages=[]
    )
    return controller 
    
    
class Controller(UiController):
    def __init__(self, *, thread_app=ThreadApp(), controller_files, pages):
        super().__init__(thread_app=thread_app, controller_files=controller_files, pages=pages)
        self.binary: BinaryTesseract = BinaryTesseract()
        
    def __get_path_tesseract_system(self) -> File | None:
        return self.binary.path_tesseract if self.binary.exists() else None
            
    def __get_path_tesseract_config(self) -> File | None:
        """
            Retorna o caminho do tesseract salvo nas preferências
        do usuário.
        """
        for k in self.appPrefs.config:
            if k == 'path_tesseract':
                self.binary.path_tesseract = File(self.appPrefs.config['path_tesseract'])
                break
        return self.binary.path_tesseract if self.binary.exists() else None
    
    def get_path_tesseract(self) -> File | None:
        if self.__get_path_tesseract_config() is not None:
            return self.__get_path_tesseract_config()
        return self.__get_path_tesseract_system()
        
 
class AppMenuBar(UIMenuBar):
    
    def __init__(self, *, controller: Controller, version='-'):
        super().__init__(controller=controller, version=version)
        self.controller: Controller = controller
        
        # Executável tesseract
        out = self.controller.get_path_tesseract()
        tess = '-' if out is None else out.absolute()
        text_tooltip = 'indisponível' if out is None else 'disponível'
        
        self.index_file_webdriver: int = self.add_item_menu(
            tooltip=tess,
            name=f'Tesseract: ',
            cmd=self.change_file_tesseract,
            submenu=self.menu_config,
        )

    def change_file_tesseract(self):
        f = self.controller.controllerFiles.fileDialog.open_filename()
        if f is None:
            return
        self.controller.appPrefs.set_config('path_tesseract', f)
        self.menu_config.entryconfig(
            self.index_file_webdriver,
            label=f'Tesseract: {f}'
        )
        self.controller.send_notify_files()

    def update_menu_bar(self):
        super().update_menu_bar()
        # Atualizar o webdriver
        f_tess: File = File(self.controller.appPrefs.config['path_tesseract'])
        self.menu_config.entryconfig(
            self.index_file_webdriver,
            label=f'Arquivo: {f_tess.absolute()}' if f_tess.exists() else 'Tesseract: indisponível',
        )
         
         
