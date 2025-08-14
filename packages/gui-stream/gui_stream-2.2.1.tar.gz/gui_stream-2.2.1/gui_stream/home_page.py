#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from gui_stream.app_ui.ui.ui_pages import UiPage
from gui_stream.app_ui.ui.widgets import (
    WidgetRow, ProgressBarAdapter, ProgressBarTkDeterminate, ProgressBarTkIndeterminate
)
from gui_stream.controller_app import Controller


class HomePageApp(UiPage):
    
    def __init__(self, *, controller: Controller):
        super().__init__(controller=controller)
        self.PAGE_NAME = 'HOME PAGE'
        self.PAGE_ROUTE = '/home'
        self.GEOMETRY = '545x170'
        self.frameMain: ttk.Frame = ttk.Frame(self, style=self.controller.appTheme.value)
        self.frameMain.pack(padx=1, pady=1, expand=True, fill='both')
        self.frame1 = ttk.Frame(self.frameMain)
        self.frame1.pack(expand=True, fill='x')
        self.frame2 = ttk.Frame(self.frameMain)
        self.frame2.pack(expand=True, fill='x')
        self.controller.windowFrames.extend(
            [self.frame1, self.frame2, self.frameMain]
        )
        self.PADDING_BTN = (8, 9)
        self.WIDTH = 16
        
        #----------------------------------------------------------#
        # Primeira Linha
        #----------------------------------------------------------#
        self.btn_convert_pdf = ttk.Button(
            self.frame1,
            text='Conversão de PDF',
            command=lambda: self.controller.navigator.push('/home/pdf'),
            style=self.controller.buttonsTheme.value,
            padding=self.PADDING_BTN,
            width=self.WIDTH
        )
        self.btn_convert_pdf.pack(side=tk.LEFT, expand=True, fill='x', padx=1, pady=1)
        
        self.btn_ocr = ttk.Button(
            self.frame1,
            text='OCR Documentos',
            command=lambda: self.controller.navigator.push('/home/ocr'),
            style=self.controller.buttonsTheme.value,
            padding=self.PADDING_BTN,
            width=self.WIDTH
        )
        self.btn_ocr.pack(side=tk.LEFT, expand=True, fill='x', padx=1, pady=1)
        
        self.btn_convert_image = ttk.Button(
            self.frame1,
            text='Editar Imagens',
            command=lambda: self.controller.navigator.push('/home/images'),
            style=self.controller.buttonsTheme.value,
            padding=self.PADDING_BTN,
            width=self.WIDTH
        )
        self.btn_convert_image.pack(side=tk.LEFT, expand=True, fill='x', padx=1, pady=1)
        
        self.btn_outro = ttk.Button(
            self.frame1,
            text='Outro',
            command=(),
            style=self.controller.buttonsTheme.value,
            padding=self.PADDING_BTN,
            width=self.WIDTH
        )
        self.btn_outro.pack(side=tk.LEFT, expand=True, fill='x', padx=1, pady=1)
        
        #----------------------------------------------------------#
        # Segunda Linha
        #----------------------------------------------------------#
        self.btn_folder_to_sheet = ttk.Button(
            self.frame2,
            text='Planilhar Pasta',
            command=lambda: self.controller.navigator.push('/home/folder_to_excel'),
            style=self.controller.buttonsTheme.value,
            padding=self.PADDING_BTN,
            width=self.WIDTH
        )
        self.btn_folder_to_sheet.pack(side=tk.LEFT, expand=True, fill='x', padx=1, pady=1)
        
        self.btn_filter_sheets = ttk.Button(
            self.frame2,
            text='Filtrar Planilhas',
            command=lambda: self.controller.navigator.push('/home/sheets'),
            style=self.controller.buttonsTheme.value,
            padding=self.PADDING_BTN,
            width=self.WIDTH
        )
        self.btn_filter_sheets.pack(side=tk.LEFT, expand=True, fill='x', padx=1, pady=1)
        
        self.btn_move_files = ttk.Button(
            self.frame2,
            text='Mover Arquivos',
            command=lambda: self.controller.navigator.push('/home/page_mv_files'),
            style=self.controller.buttonsTheme.value,
            padding=self.PADDING_BTN,
            width=self.WIDTH
        )
        self.btn_move_files.pack(side=tk.LEFT, expand=True, fill='x', padx=1, pady=1)
        
        self.btn_special = ttk.Button(
            self.frame2,
            text='Especial',
            command=(),
            style=self.controller.buttonsTheme.value,
            padding=self.PADDING_BTN,
            width=self.WIDTH
        )
        self.btn_special.pack(side=tk.LEFT, expand=True, fill='x', padx=1, pady=1)
        
        self.pageListButtons.extend(
            [
                self.btn_convert_image, self.btn_convert_pdf,
                self.btn_filter_sheets, self.btn_folder_to_sheet,
                self.btn_ocr, self.btn_outro, self.btn_move_files,
                self.btn_special,
            ]
        )