#!/usr/bin/env python3
from soup_files import File, LibraryDocs
from pandas import DataFrame
from gui_stream.app_ui.core import (
    ControllerApp,
    MenuBar,
)


class UIMenuBar(MenuBar):

    def __init__(self, *, controller: ControllerApp, version='-'):
        super().__init__(controller=controller, version=version)
        
        self.menu_file.insert_command(
            0, 
            label='Voltar',
            command=lambda: self.controller.navigator.pop(), 
            background='yellow'
        )
        
    def update_menu_bar(self):
        super().update_menu_bar()
        
