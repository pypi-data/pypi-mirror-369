#!/usr/bin/env python3

from soup_files import LibraryDocs, File
import tkinter as tk
from gui_stream.app_ui.core.observer import AbstractNotifyProvider, ObserverController
from gui_stream.app_ui.core.themes import AppThemes
from gui_stream.app_ui.core.page import ControllerApp


class MenuBar(ObserverController):

    def __init__(self, *, controller: ControllerApp, version='-'):
        super().__init__()
        self.controller: ControllerApp = controller
        self.version = version

        #-------------------------------------------------------------#
        # Criar a barra superior
        #-------------------------------------------------------------#
        # Iniciar a barra com tema dark
        bg_color = "gray15"
        fg_color = "white"
        active_bg_color = "gray30"
        active_fg_color = "white"

        self.menu_bar: tk.Menu = tk.Menu(self.controller)
        self.menu_bar.config(
            bg=bg_color,
            fg=fg_color,
            activebackground=active_bg_color,
            activeforeground=active_fg_color
        )
        self.controller.config(menu=self.menu_bar)

        # -------------------------------------------------------------#
        # Criar o menu Arquivo
        # -------------------------------------------------------------#
        self.menu_file: tk.Menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Arquivo", menu=self.menu_file)
        self.index_menu_exit = self.add_item_menu(
            name='Sair',
            tooltip='Sair do programa',
            cmd=self.controller.exit_app,
            submenu=self.menu_file,
        )
        self.menu_file.config(background='red')

        # -------------------------------------------------------------#
        # Menu Configurações
        # -------------------------------------------------------------#
        self.menu_config: tk.Menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Configurações", menu=self.menu_config)
        # Arquivo de configurações
        file_conf = self.controller.controllerFiles.fileConfig
        self.index_config_file = self.add_item_menu(
            tooltip=file_conf.absolute(),
            name='Arquivo de configuração: ',
            cmd=(),
            submenu=self.menu_config,
        )
        # Pasta de trabalho
        self.index_work_dir: int = self.add_item_menu(
            tooltip=self.controller.controllerFiles.save_dir.absolute(),
            name='Pasta de trabalho: ',
            cmd=lambda: self.change_work_dir(),
            submenu=self.menu_config,
        )
        
        # -------------------------------------------------------------#
        # Menu Estilo
        # -------------------------------------------------------------#
        self.style_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tema", menu=self.style_menu)
        self.init_menu_style()

        # -------------------------------------------------------------#
        # Menu sobre
        # -------------------------------------------------------------#
        self.menu_about_bar: tk.Menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Sobre", menu=self.menu_about_bar)
        self.menu_about_bar.add_command(label=f'Versão: {self.version}')

        self.indexAutor = self.add_item_menu(
            cmd=(),
            submenu=self.menu_about_bar,
            tooltip='autor',
            name='Autor'
        )

    def add_item_menu(self, *, name: str, tooltip: str, cmd: callable, submenu: tk.Menu) -> int:
        """
            Adiciona um item ao menu com um tooltip.

            :param name: Nome do item no menu.
            :param tooltip: Texto do tooltip exibido no menu.
            :param cmd: Função a ser chamada ao clicar no item.
            :param submenu: Um item do menu, Arquivo, Sobre, etc.
            :return: Índice do item adicionado no menu.
        """
        submenu.add_command(label=f"{name} ({tooltip})", command=cmd)
        return submenu.index(tk.END)

    def init_menu_style(self):
        # Submenu para temas da barra
        self.bar_theme_menu: tk.Menu = tk.Menu(self.style_menu, tearoff=0)

        self.bar_theme_menu.add_command(
            label="Tema Claro",
            command=lambda: self.set_theme_menu_bar(AppThemes.LIGHT)
        )
        self.bar_theme_menu.add_command(
            label="Tema Escuro",
            command=lambda: self.set_theme_menu_bar(AppThemes.DARK)
        )
        self.bar_theme_menu.add_command(
            label="Tema Roxo Claro",
            command=lambda: self.set_theme_menu_bar(AppThemes.LIGHT_PURPLE)
        )

        # Submenu para temas do app
        self.bar_theme_app = tk.Menu(self.style_menu, tearoff=0)
        self.bar_theme_app.add_command(
            label="Tema Claro",
            command=lambda: self.set_theme_app(AppThemes.LIGHT),
        )
        self.bar_theme_app.add_command(
            label="Tema Escuro",
            command=lambda: self.set_theme_app(AppThemes.DARK),
        )
        self.bar_theme_app.add_command(
            label="Roxo Escuro",
            command=lambda: self.set_theme_app(AppThemes.DARK_PURPLE),
        )
        self.bar_theme_app.add_command(
            label="Roxo Claro",
            command=lambda: self.set_theme_app(AppThemes.LIGHT_PURPLE),
        )

        # Submenu para temas dos botões
        self.bar_theme_buttons = tk.Menu(self.style_menu, tearoff=0)
        self.bar_theme_buttons.add_command(
            label="Botões verdes",
            command=lambda: self.set_theme_buttons(AppThemes.BUTTON_GREEN),
        )
        self.bar_theme_buttons.add_command(
            label="Botões Roxo claro",
            command=lambda: self.set_theme_buttons(AppThemes.BUTTON_PURPLE_LIGHT),
        )

        # Adicionar os submenus à barra de menu principal
        self.style_menu.add_cascade(label="Tema do App", menu=self.bar_theme_app)
        self.style_menu.add_cascade(label="Tema da barra", menu=self.bar_theme_menu)
        self.style_menu.add_cascade(label="Tema dos botões", menu=self.bar_theme_buttons)

    def set_theme_menu_bar(self, new: AppThemes):
        bg_color = "gray15"
        fg_color = "white"
        active_bg_color = "gray30"
        active_fg_color = "white"
        
        if new == AppThemes.LIGHT:
            bg_color = "white"
            fg_color = "black"
            active_bg_color = "lightgray"
            active_fg_color = "black"
        elif new == AppThemes.LIGHT_PURPLE:
            # barra com tema roxo claro
            bg_color = "#B388EB"  # Roxo claro (tom pastel)
            fg_color = "white"  # Texto branco para contraste
            active_bg_color = "#a070d6"  # Roxo um pouco mais escuro para hover
            active_fg_color = "white"  # Texto branco também no hover

        self.menu_bar.config(
            bg=bg_color,
            fg=fg_color,
            activebackground=active_bg_color,
            activeforeground=active_fg_color
        )

    def set_theme_app(self, new: AppThemes):
        self.controller.appTheme = new

    def set_theme_buttons(self, new: AppThemes):
        self.controller.buttonsTheme = new

    def change_work_dir(self):
        self.controller.controllerFiles.select_output_dir()
        self.menu_config.entryconfig(
            self.index_work_dir,
            label=f'Pasta de trabalho: {self.controller.controllerFiles.save_dir.absolute()}'
        )

    def update_menu_bar(self):
        """Atualizar as opções do Menu"""
        self.menu_config.entryconfig(
            self.index_menu_exit,
            label=f'Arquivo: {self.controller.controllerFiles.fileConfig.absolute()}'
        )

    def update_state(self):
        self.update_menu_bar()

    def receiver_notify(self, notify_provider: AbstractNotifyProvider = None):
        """
            Receber notificações quando as preferências
            do app_ui forem atualizadas.
        """
        self.update_state()
