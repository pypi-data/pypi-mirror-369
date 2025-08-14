#!/usr/bin/env python3
from __future__ import annotations
from typing import List
from tkinter import ttk,messagebox
import tkinter as tk
from soup_files import File, KERNEL_TYPE
from gui_stream.app_ui.core.themes import AppThemes
from gui_stream.app_ui.core.select_files import ControllerFiles
from gui_stream.app_ui.core.page import ControllerApp, AppPage, AppThemes, ThreadApp
from gui_stream.app_ui.core.progress import ProgressBarAdapter, ProgressBarTkIndeterminate
from gui_stream.app_ui.ui.widgets import (
    WidgetFiles, Orientation, WidgetColumn, WidgetRow, WidgetProgressBar
)


class UiController(ControllerApp):

    def __init__(
                self, *, thread_app: ThreadApp = ThreadApp(),
                controller_files: ControllerFiles,
                pages: List[AppPage]
            ):
        super().__init__(
            thread_app=thread_app,
            controller_files=controller_files,
            pages=pages
        )
        self._top_bar: TopBar = None
        
    @property
    def topBar(self) -> TopBar:
        if self._top_bar is None:
            self._top_bar = TopBar(self)
        return self._top_bar

    def set_topbar(self):
        if self._top_bar is None:
            self._top_bar = TopBar(self)


class UiPage(AppPage):

    def __init__(self, *, controller: UiController):
        super().__init__(controller=controller)
        self.GEOMETRY = '460x400'
        self.initUI()

    def initUI(self):
        pass
    
    def alert(self, text:str):
        messagebox.showinfo('Alerta', text)

    def set_app_theme(self, new: AppThemes):
        self.controller.appTheme = new


class TopBar(object):
    def __init__(self, controller: UiController):
        self.controller: UiController = controller
        self.frameMain = ttk.Frame(
            self.controller.containerHead,
            style=self.controller.appTheme.value,
        )
        self.frameMain.pack(expand=True, fill='x', padx=1, pady=1)
        
        # Label Texto
        self.lbText = ttk.Label(
            self.frameMain,
            text='-'
        )
        self.lbText.pack(expand=True, fill='x', padx=1, pady=1)
        
        #===========================================================#
        # Barra de progresso
        #===========================================================#
        # Container para Labels da barra de progresso
        self.frameLabels = ttk.Frame(self.frameMain, style=self.controller.appTheme.value)
        self.frameLabels.pack(expand=True, fill='x')
        
        self.lbProgress = ttk.Label(self.frameLabels, text='0%')
        self.lbProgress.pack(side=tk.LEFT, padx=1, pady=1)
        
        self.lbPbarText = ttk.Label(self.frameLabels, text='-')
        self.lbPbarText.pack(side=tk.LEFT, padx=1, pady=1, expand=True, fill='x')
        
        self.tk_pbar = ttk.Progressbar(
            self.frameMain, 
            mode='indeterminate',
            style=AppThemes.PBAR_GREEN.value
        )
        self.tk_pbar.pack(expand=True, fill='x', padx=1, pady=1)
        self.pbar: ProgressBarAdapter = ProgressBarAdapter(
            ProgressBarTkIndeterminate(
                label_text=self.lbPbarText,
                label_progress=self.lbProgress,
                progress_bar=self.tk_pbar,
            )
        )
        
        # Inscrever o Frame() na controller para alterar o tema 
        # dinamicamente quando o usuário selecionar determinado 
        # tema na barra de ferramentas
        self.controller.windowProgressBar.append(self.tk_pbar)
        
    def set_text(self, text:str):
        self.lbText.config(text=text)