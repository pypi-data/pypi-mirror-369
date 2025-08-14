#!/usr/bin/env python3

from soup_files import UserAppDir, File, Directory, JsonConvert, JsonData, KERNEL_TYPE
from gui_stream.app_ui.core.select_files import ControllerFiles, AppFileDialog, PreferencesApp
from gui_stream.app_ui.core.themes import AppThemes
from gui_stream.app_ui.ui.ui_menu_bar import UIMenuBar
from gui_stream.app_ui.ui.ui_pages import UiPage, UiController


def load_conf_user(prefs_app: PreferencesApp) -> PreferencesApp:
    # Verificar e ler o arquivo de configuração local, se existir.
    if not prefs_app.fileConfig.exists():
        return prefs_app
    
    try:
        initial_conf: dict = JsonConvert.from_file(prefs_app.fileConfig).to_json_data().to_dict()
    except Exception as e:
        print(e)
    else:
        for key in initial_conf.keys():
            if key == 'save_dir':
                prefs_app.saveDir = Directory(initial_conf['save_dir'])
            elif key == 'initial_input_dir':
                prefs_app.initialInputDir = Directory(initial_conf['initial_input_dir'])
            elif key == 'initial_output_dir':
                prefs_app.initialOutputDir = Directory(initial_conf['initial_output_dir'])
            elif key == 'app_theme':
                if initial_conf['app_theme'] == 'Black.TFrame':
                    prefs_app.appTheme = AppThemes.DARK
                elif initial_conf['app_theme'] == 'LightFrame.TFrame':
                    prefs_app.appTheme = AppThemes.LIGHT
                elif initial_conf['app_theme'] == 'DarkPurple.TFrame':
                    prefs_app.appTheme = AppThemes.DARK_PURPLE
                elif initial_conf['app_theme'] == 'LightPurple.TFrame':
                    prefs_app.appTheme = AppThemes.LIGHT_PURPLE
                elif initial_conf['app_theme'] == 'CinzaFrame.TFrame':
                    prefs_app.appTheme = AppThemes.GRAY
                else:
                    prefs_app.appTheme = AppThemes.DARK
    return prefs_app


class MyApp(object):
    def __init__(self, controller: UiController):
        # Definir appdir
        #self.app_dir: UserAppDir = controller.appPrefs.appDir
        # Definir controller do App.
        self.controller_app: UiController = controller
        # Criar as páginas
        pages = [
            UiPage,
        ]

        # Adicionar páginas ao controller
        for page in pages:
            p = page(controller=self.controller_app)
            self.controller_app.add_page(p)
        self.controller_app.go_home_page()
        
    def set_menu_bar(self):
        # Barra superior
        self.app_bar: UIMenuBar = UIMenuBar(controller=self.controller_app)

    def initUI(self):
        self.controller_app.mainloop()
        
   
