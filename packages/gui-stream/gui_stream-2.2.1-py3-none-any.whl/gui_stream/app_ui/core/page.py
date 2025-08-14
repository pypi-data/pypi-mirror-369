#!/usr/bin/env python3

from __future__ import annotations
import threading
from typing import Tuple, List, Dict
from tkinter import (ttk, Tk, Menu, filedialog, messagebox)
from soup_files import LibraryDocs, File, Directory, UserAppDir

from gui_stream.app_ui.core.observer import (
    ControllerNotifyProvider, AbstractNotifyProvider, ObserverController
)
from gui_stream.app_ui.core.themes import AppStyles, AppThemes
from gui_stream.app_ui.core.select_files import ControllerFiles, PreferencesApp


class ThreadApp(object):
    _instance = None  # Singleton

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ThreadApp, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.threadMain = None
        self.threadStopEvent = threading.Event()
        self.threadRunning = False
        self._running = False

    def is_running(self) -> bool:
        return self.threadRunning and self._running

    def thread_main_create(self, cmd: callable) -> None:
        """Cria e inicia a thread principal da operação."""
        if self.threadRunning:
            print(f'{self.__class__.__name__}: Já existe uma operação em andamento.')
            return

        if self.threadMain is not None:
            print(f'{self.__class__.__name__}: Thread principal já foi criada.')
            return

        self.threadStopEvent.clear()
        self._running = True
        self.threadRunning = True

        def wrapper():
            print(f'{self.__class__.__name__}: Iniciando execução da thread...')
            try:
                cmd()

            except Exception as e:
                print(f'{self.__class__.__name__}: Erro na thread: {e}')
            finally:
                self._running = False
                self.threadRunning = False
                self.threadMain = None
                print(f'{self.__class__.__name__}: Thread finalizada.')

        self.threadMain = threading.Thread(target=wrapper, daemon=True)
        self.threadMain.start()
        print(f'{self.__class__.__name__}: Thread principal criada.')

    def thread_main_stop(self):
        """Sinaliza para a thread parar e aguarda sua finalização."""
        if self.threadMain and self.threadMain.is_alive():
            print(f'{self.__class__.__name__}: Parando a Thread principal com Event.set()')
            self.threadStopEvent.set()
            self.threadMain.join(timeout=3)

            if self.threadMain.is_alive():
                print(f'{self.__class__.__name__}: Atenção: Thread ainda viva após timeout 3.')
            else:
                print(f'{self.__class__.__name__}: Thread parada com sucesso.')

        self.threadMain = None
        self._running = False
        self.threadRunning = False


class AppWindow(Tk):
    _instance_window = None

    def __new__(cls, *args, **kwargs):
        if cls._instance_window is None:
            cls._instance_window = super(AppWindow, cls).__new__(cls)
        return cls._instance_window

    def __init__(self, *, thread_app: ThreadApp = ThreadApp()):
        super().__init__()
        self.threadApp: ThreadApp = thread_app
        self.appStyles: AppStyles = AppStyles(self)
        # Container superior (Head)
        self.containerHead: ttk.Frame = ttk.Frame(self, height=30)
        self.containerHead.pack(padx=1, pady=1, fill='x')
        # Container inferior Body
        self.containerBody: ttk.Frame = ttk.Frame(self)
        self.containerBody.pack(expand=True, fill='both', padx=2, pady=2)
        # Lista de Containers
        self.windowFrames: List[ttk.Frame] = []
        self.windowFrames.append(self.containerHead)
        self.windowFrames.append(self.containerBody)
        # Lista de barras de progresso
        self.windowProgressBar: List[ttk.Progressbar] = []
        # Lista de botões
        self.windowButtons: List[ttk.Button] = []
        
    def alert(self, text: str):
        messagebox.showinfo('Alerta', text)

    def exit_app(self):
        """Encerrar threads em execução e sair do programa"""
        self.threadApp.thread_main_stop()
        if self.threadApp.threadMain is not None:
            print("Aguardando thread finalizar...")
            self.threadApp.threadMain.join(timeout=5)
        print("Thread finalizada. Encerrando GUI.")
        self.quit()


class ControllerApp(AppWindow, ControllerNotifyProvider):
    """
        Controlador de páginas
    """
    _instance_controller = None

    def __new__(cls, *args, **kwargs):
        if cls._instance_controller is None:
            cls._instance_controller = super(ControllerApp, cls).__new__(cls)
        return cls._instance_controller

    def __init__(
            self,
            *,
            thread_app: ThreadApp = ThreadApp(),
            controller_files: ControllerFiles,
            pages: List[AppPage],
            ):
        super().__init__(thread_app=thread_app)
        ControllerNotifyProvider.__init__(self)
        self.controllerFiles: ControllerFiles = controller_files
        self.containerBody.config(style=self.controllerFiles.fileDialog.prefs_app.appTheme.value)
        self.containerHead.config(style=self.controllerFiles.fileDialog.prefs_app.appTheme.value)
        self._buttonsTheme: AppThemes = AppThemes.BUTTON_GREEN

        self.pages_collection: Dict[str, AppPage] = {}
        self.navigator: Navigator = Navigator(pages=self.pages_collection)
        for p in pages:
            self.pages_collection[p.PAGE_ROUTE] = p
        self.navigator: Navigator = Navigator(pages=self.pages_collection)

    @property
    def appPrefs(self) -> PreferencesApp:
        return self.controllerFiles.fileDialog.prefs_app

    @property
    def appDir(self) -> UserAppDir:
        return self.controllerFiles.fileDialog.prefs_app.appDir

    @property
    def fileConfig(self) -> File:
        return self.controllerFiles.fileDialog.prefs_app.fileConfig

    @fileConfig.setter
    def fileConfig(self, new: File):
        self.controllerFiles.fileDialog.prefs_app.fileConfig = new

    @property
    def saveDir(self) -> Directory:
        return self.controllerFiles.fileDialog.prefs_app.saveDir

    @saveDir.setter
    def saveDir(self, new: Directory):
        self.controllerFiles.fileDialog.prefs_app.saveDir = new

    @property
    def appTheme(self) -> AppThemes:
        return self.controllerFiles.fileDialog.prefs_app.appTheme

    @appTheme.setter
    def appTheme(self, new: AppThemes):
        if new == self.controllerFiles.fileDialog.prefs_app.appTheme:
            return
        self.controllerFiles.fileDialog.prefs_app.appTheme = new
        self.update_theme_window()
        self.send_notify_theme()

    @property
    def buttonsTheme(self) -> AppThemes:
        return self._buttonsTheme

    @buttonsTheme.setter
    def buttonsTheme(self, new: AppThemes):
        if new == self._buttonsTheme:
            return # Tema repetido
        self._buttonsTheme = new
        self.update_theme_buttons()
        self.send_notify_theme()

    def add_page(self, page: AppPage):
        if isinstance(page, AppPage):
            self.navigator.add_page(page)

    def add_pages(self, pages: List[AppPage]):
        for p in pages:
            self.add_page(p)
            
    def update_theme_buttons(self):
        for btn in self.windowButtons:
            btn.config(style=self.buttonsTheme.value)

    def update_theme_window(self):
        """
            Alterar o tema dos frames da janela, não inclui itens das páginas, nem botões.
        """
        for _frame in self.windowFrames:
            _frame.config(style=self.appTheme.value)
            
        for _bar in self.windowProgressBar:
            if self.appTheme == AppThemes.DARK_PURPLE:
                _bar.config(style=AppThemes.PBAR_PURPLE.value)
            elif self.appTheme == AppThemes.LIGHT_PURPLE:
                _bar.config(style=AppThemes.PBAR_PURPLE_LIGHT.value)
            else:
                _bar.config(style=AppThemes.PBAR_GREEN.value)
        print(f'Controller: Tema Alterado')

    def go_home_page(self):
        for _key in self.navigator.pages.keys():
            if _key == '/home':
                self.navigator.push('/home')
                break

    def save_config(self):
        """Salvar as configurações atuais em um arquivo .JSON"""

        try:
            print(f'Salvando configurações em: {self.fileConfig.absolute()}')
            self.appPrefs.to_json().to_file(self.fileConfig)
        except Exception as e:
            print(e)

    def set_local_user_prefs(self):
        """
            Ler as configurações de um arquivo JSON local se existir
        """
        pass

    def exit_app(self):
        self.save_config()
        super().exit_app()


class AppPage(ttk.Frame, ObserverController):

    def __init__(self, *, controller: ControllerApp):
        super().__init__(controller.containerBody)
        ObserverController.__init__(self)
        self.controller: ControllerApp = controller
        self.controller.add_observer(self)
        self.PAGE_ROUTE: str = '/home'
        self.PAGE_NAME: str = 'HOME'
        self.GEOMETRY: str = "400x250"

        self.pageListFrames: List[ttk.Frame] = []
        self.pageListButtons: List[ttk.Button] = []
        self.set_size_screen()

    def initUI(self):
        pass

    def receiver_notify(self, notify_provide: AbstractNotifyProvider = None):
        """
            Receber notificações externas de outros objetos.
        """
        pass

    def receiver_notify_theme(self, notify: ControllerNotifyProvider):
        # Alterar o tema dos frames
        for _frame in self.pageListFrames:
            _frame.config(style=self.controller.appTheme.value)

        # Alterar o tema dos botões
        for _btn in self.pageListButtons:
            _btn.config(style=self.controller.buttonsTheme.value)

    def is_running(self):
        return self.controller.threadApp.is_running()

    def check_running(self) -> bool:
        """
            Verifica se já existe outra operação em andamento.
        """
        if self.is_running():
            messagebox.showwarning("Aviso", "Existe outra operação em andamento, aguarde!")
            return False
        return True

    def thread_main_create(self, cmd: callable) -> None:
        self.controller.threadApp.thread_main_create(cmd)

    def thread_main_stop(self):
        self.controller.threadApp.thread_main_stop()

    def command_stop_button(self):
        """
            Esse método pode ser conectado a um botão para parar a Thread principal.
        Podendo ser conectado diretamente ou indiretamente.
        """
        self.controller.threadApp.thread_main_stop()

    def go_back_page(self):
        self.thread_main_stop()
        self.controller.navigator.pop()

    def set_size_screen(self):
        self.controller.geometry(self.GEOMETRY)
        self.controller.title(self.PAGE_NAME)

    def update_page_state(self):
        pass


class Navigator(object):
    def __init__(self, *, pages: Dict[str, AppPage]):
        self.pages: Dict[str, AppPage] = pages
        self.current_page = None  # Página atualmente exibida
        self.historyPages: List[str] = []  # Pilha para armazenar o histórico de navegação

    def add_page(self, page: AppPage):
        self.pages[page.PAGE_ROUTE] = page
        print(f'Página adicionada: {page.PAGE_ROUTE}')

    def push(self, page_name: str):
        """
        Exibe a página especificada.

        :param page_name: Nome da página a ser exibida.
        """
        print(f'Navegando para {page_name}')
        if page_name not in self.pages:
            messagebox.showwarning("Aviso", f'Página não encontrada!\n{page_name}')
            return

        # Esconde a página atual, se houver
        if self.current_page is not None:
            self.historyPages.append(self.current_page.PAGE_ROUTE)  # Salvar no histórico
            self.current_page.pack_forget()

        # Mostra a nova página
        self.current_page: AppPage = self.pages[page_name]
        self.current_page.set_size_screen()
        self.current_page.update_page_state()
        self.current_page.pack(expand=True, fill='both', padx=2, pady=2)
        print(f'Página atual: {self.current_page.PAGE_ROUTE}')

    def pop(self):
        """
        Retorna à página anterior no histórico de navegação.
        """
        if not self.historyPages:
            messagebox.showwarning("Aviso", "Não há páginas anteriores no histórico para retornar.")
            return

        # Esconde a página atual
        if self.current_page is not None:
            self.current_page.pack_forget()

        # Recupera a página anterior do histórico
        previous_page_name = self.historyPages.pop()
        self.current_page: AppPage = self.pages[previous_page_name]
        self.current_page.set_size_screen()
        self.current_page.update_page_state()
        self.current_page.pack(expand=True, fill='both', padx=2, pady=2)
        print(f'Retornado para anterior: {previous_page_name}')
