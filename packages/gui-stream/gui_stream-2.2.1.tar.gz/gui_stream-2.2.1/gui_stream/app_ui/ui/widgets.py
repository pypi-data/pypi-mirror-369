#!/usr/bin/env python3
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict

from tkinter import ttk
import tkinter as tk
from soup_files import LibraryDocs
from gui_stream.app_ui.core.themes import AppThemes
from gui_stream.app_ui.core.page import ControllerApp
from gui_stream.app_ui.core.progress import (
    ProgressBarTkIndeterminate,
    ProgressBarTkDeterminate,
    ProgressBarAdapter,
)

class Orientation(Enum):
    H = 'horizontal'
    V = 'vertical'


class LibProgress(Enum):
    INDETERMINATE = 'indeterminate'
    DETERMINATE = 'determinate'
   

class WidgetApp(ABC):
    def __init__(self, frame: ttk.Frame, theme: AppThemes = AppThemes.DARK):
        #self.frame: ttk.Frame = ttk.Frame(frame, style=theme.value)
        self.frame = frame
        self.frame.pack(expand=True, fill='both', padx=1, pady=1)
        self.button = None
        self.label = None
        self.buttonsKeys: Dict[str, ttk.Button] = {}

    @abstractmethod
    def add_button(self, name: str, cmd: callable, *, theme: AppThemes = AppThemes.BUTTON_GREEN):
        pass

    @abstractmethod
    def add_label(self, text: str):
        pass


class WidgetColumn(WidgetApp):
    def __init__(self, frame):
        super().__init__(frame)

    def add_button(self, name: str, cmd: callable, *, theme: AppThemes = AppThemes.BUTTON_GREEN):
        if self.button is not None:
            return
        self.button = ttk.Button(
            self.frame,
            text=name,
            command=cmd,
            style=theme.value
        )
        self.button.pack(expand=True, fill='both', padx=1, pady=1)

    def add_label(self, text: str):
        self.label = ttk.Label(self.frame, text=text)
        self.label.pack(expand=True, padx=1, pady=1)


class WidgetRow(WidgetApp):
    def __init__(self, frame):
        super().__init__(frame)

    def add_button(self, name: str, cmd: callable, *, theme: AppThemes = AppThemes.BUTTON_GREEN):
        if self.button is not None:
            return
        self.button = ttk.Button(
            self.frame,
            text=name,
            command=cmd,
            style=theme.value
        )
        self.button.pack(side=tk.LEFT, expand=True, fill='both', pady=1, padx=1)

    def add_label(self, text: str):
        if self.label is not None:
            pass
        self.label = ttk.Label(self.frame, text=text)
        self.label.pack(side=tk.LEFT, expand=True, fill='both', pady=1, padx=1)


class WidgetFiles(object):
    def __init__(self, frame: ttk.Frame, *, orientation: Orientation = Orientation.V, controller: ControllerApp):
        self.controller: ControllerApp = controller
        self.orientation: Orientation = orientation
        self.frame: ttk.Frame = ttk.Frame(frame)
        self.frame.pack(expand=True, fill='x')
        self._PADDING = (6, 8)
        self._WIDTH = 14
        
        self.frame_buttons: ttk.Frame = ttk.Frame(
            self.frame,
            style=controller.appTheme.value,
        )
        self.frame_labels: ttk.Frame = ttk.Frame(
            self.frame,
            style=AppThemes.LIGHT_PURPLE.value,
        )
        
        #-----------------------------------------------------------#
        # Botão para selecionar a pasta de saída.
        #-----------------------------------------------------------#
        self.btn_export = ttk.Button(
            self.frame_buttons,
            style=self.controller.buttonsTheme.value,
            command=self.select_ouput_folder,
            text='Destino',
            padding=self._PADDING,
            width=self._WIDTH,
        )
        self.lb_outdir = ttk.Label(
            self.frame_labels,
            text=f'Salvar em: {self.controller.controllerFiles.save_dir.basename()} '
        )
        if self.orientation == Orientation.V:
            self.frame_buttons.pack(expand=True, fill='both', padx=1, pady=1)
            self.frame_labels.pack(expand=True, fill='both', padx=1, pady=1)
            
            self.btn_export.pack(expand=True, fill='both', padx=1, pady=1)
            self.lb_outdir.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            self.frame_buttons.pack(expand=True, fill='both', padx=1, pady=1)
            self.frame_labels.pack(expand=True, fill='both', padx=1, pady=1)
            
            self.btn_export.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
            self.lb_outdir.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)

        #-----------------------------------------------------------#
        # Botões de imagem
        #-----------------------------------------------------------#
        self.btn_img = ttk.Button(
            self.frame_buttons,
            style=self.controller.buttonsTheme.value,
            text='Adicionar Imagens',
            command=self.add_files_image,
            padding=self._PADDING,
            width=self._WIDTH,
        )
        self.lb_img: ttk.Label = ttk.Label(
            self.frame_labels,
            text=f'Imagens: {self.controller.controllerFiles.num_files_image}'
        )

        # -----------------------------------------------------------#
        # Botões PDF
        # -----------------------------------------------------------#
        self.btn_pdf = ttk.Button(
            self.frame_buttons,
            style=self.controller.buttonsTheme.value,
            text='Adicionar PDFs',
            command=self.add_files_pdf,
            padding=self._PADDING,
            width=self._WIDTH,
        )
        self.lb_pdf: ttk.Label = ttk.Label(
            self.frame_labels,
            text=f'PDFs: {self.controller.controllerFiles.num_files_pdf}'
        )
        self.controller.windowFrames.append(self.frame_buttons)
        self.controller.windowFrames.append(self.frame_labels)
        
        # -----------------------------------------------------------#
        # Botões Planilhas
        # -----------------------------------------------------------#
        self.btn_sheets = ttk.Button(
            self.frame_buttons,
            style=self.controller.buttonsTheme.value,
            text='Adicionar Planilhas',
            command=self.add_files_sheets,
            padding=self._PADDING,
            width=self._WIDTH,
        )
        self.lb_sheets: ttk.Label = ttk.Label(
            self.frame_labels,
            text=f'Planilhas: {self.controller.controllerFiles.num_files_sheet}'
        )
        
        # -----------------------------------------------------------#
        # Botão para importar pastas
        # -----------------------------------------------------------#
        self.btn_input_dir = ttk.Button(
            self.frame_buttons,
            style=self.controller.buttonsTheme.value,
            text='Importar Pasta',
            command=self.add_folder,
            padding=self._PADDING,
            width=self._WIDTH,
        )
        
        # -----------------------------------------------------------#
        # Botão para limpar
        # -----------------------------------------------------------#
        self.btn_clear_files = ttk.Button(
            self.frame_buttons,
            style=self.controller.buttonsTheme.value,
            text='Limpar',
            command=self.clear_files,
            padding=self._PADDING,
            width=self._WIDTH,
        )

        self.controller.windowFrames.extend(
            [self.frame_labels, self.frame_buttons],
        )
        self.controller.windowButtons.extend(
            [
                self.btn_export, self.btn_img, self.btn_pdf,
                self.btn_clear_files, self.btn_sheets, self.btn_input_dir,
            ]
        )

    def set_button_image(self):
        if self.orientation == Orientation.V:
            self.btn_img.pack(expand=True, fill='both', padx=1, pady=1)
            self.lb_img.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            self.btn_img.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
            self.lb_img.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)

    def set_button_pdf(self):
        if self.orientation == Orientation.V:
            self.btn_pdf.pack(expand=True, fill='both', padx=1, pady=1)
            self.lb_pdf.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            self.btn_pdf.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
            self.lb_pdf.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
        
    def set_button_sheets(self):
        if self.orientation == Orientation.V:
            self.btn_sheets.pack(expand=True, fill='both', padx=1, pady=1)
            self.lb_sheets.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            self.btn_sheets.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
            self.lb_sheets.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
            
    def set_button_folder(self):
        if self.orientation == Orientation.V:
            self.btn_input_dir.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            self.btn_input_dir.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
            
    def set_button_clear(self):
        if self.orientation == Orientation.V:
            self.btn_clear_files.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            self.btn_clear_files.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)

    def add_files_pdf(self):
        self.controller.controllerFiles.select_files(LibraryDocs.PDF)
        self.lb_pdf.config(
            text=f'PDFs: {self.controller.controllerFiles.num_files_pdf}'
        )
        
    def add_files_sheets(self):
        self.controller.controllerFiles.select_files(LibraryDocs.SHEET)
        self.lb_pdf.config(
            text=f'Planilhas: {self.controller.controllerFiles.num_files_sheet}'
        )

    def add_files_image(self):
        self.controller.controllerFiles.select_files(LibraryDocs.IMAGE)
        self.lb_img.config(
            text=f' Images: {self.controller.controllerFiles.num_files_image}'
        )

    def add_folder(self):
        self.controller.controllerFiles.select_dir(LibraryDocs.ALL_DOCUMENTS)
        self.lb_pdf.config(
            text=f'PDFs: {self.controller.controllerFiles.num_files_pdf}'
        )
        self.lb_img.config(
            text=f' Images: {self.controller.controllerFiles.num_files_image}'
        )
        self.lb_sheets.config(
            text=f'Planilhas: {self.controller.controllerFiles.num_files_sheet}'
        )

    def select_ouput_folder(self):
        self.controller.controllerFiles.select_output_dir()
        self.lb_outdir.config(
            text=f'Salvar em: {self.controller.controllerFiles.save_dir.basename()}'
        )

    def clear_files(self):
        """Limpar a lista de arquivos selecionados"""
        self.controller.controllerFiles.clear()

        self.lb_pdf.config(
            text=f'PDFs: {self.controller.controllerFiles.num_files_pdf}'
        )
        self.lb_img.config(
            text=f'Imagens: {self.controller.controllerFiles.num_files_image}'
        )
        self.lb_sheets.config(
            text=f'Planilhas: {self.controller.controllerFiles.num_files_sheet}'
        )



class WidgetExportFiles(object):
    def __init__(self, frame: ttk.Frame, *, orientation: Orientation = Orientation.V, controller: ControllerApp):
        self.controller: ControllerApp = controller
        self.orientation: Orientation = orientation
        self.frame: ttk.Frame = ttk.Frame(frame)
        self.frame.pack(expand=True, fill='x')
        self._PADDING = (6, 8)
        self._WIDTH = 14
        self.buttonsKey: Dict[str, ttk.Button] = {}
        
        self.frameButtons: ttk.Frame = ttk.Frame(
            self.frame,
            style=controller.appTheme.value,
        )
        self.frameLabels: ttk.Frame = ttk.Frame(
            self.frame,
            style=AppThemes.LIGHT_PURPLE.value,
        )
        
        if self.orientation == Orientation.V:
            self.frameButtons.pack(expand=True, fill='both', padx=1, pady=1)
            self.frameLabels.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            self.frameButtons.pack(expand=True, fill='both', padx=1, pady=1)
            self.frameLabels.pack(expand=True, fill='both', padx=1, pady=1)
            
        #-----------------------------------------------------------#
        # Botão para exportar imagens
        #-----------------------------------------------------------#
        self.btn_img = ttk.Button(
            self.frameButtons,
            style=self.controller.buttonsTheme.value,
            text='Exportar Imagens',
            padding=self._PADDING,
            width=self._WIDTH,
        )
        
        # -----------------------------------------------------------#
        # Botões para exportar PDFs
        # -----------------------------------------------------------#
        self.btn_pdf = ttk.Button(
            self.frameButtons,
            style=self.controller.buttonsTheme.value,
            text='Exportar PDFs',
            padding=self._PADDING,
            width=self._WIDTH,
        )
        
        # -----------------------------------------------------------#
        # Botões Planilhas
        # -----------------------------------------------------------#
        self.btn_sheets = ttk.Button(
            self.frameButtons,
            style=self.controller.buttonsTheme.value,
            text='Exportar Planilha',
            padding=self._PADDING,
            width=self._WIDTH,
        )
        
        # -----------------------------------------------------------#
        # Botões para exportar PDF
        # -----------------------------------------------------------#
        self.btn_uniq_pdf = ttk.Button(
            self.frameButtons,
            style=self.controller.buttonsTheme.value,
            text='Exportar PDF',
            padding=self._PADDING,
            width=self._WIDTH,
        )
        self.controller.windowFrames.extend(
            [
                self.frameButtons, 
                self.frameLabels,
            ]
        )
        self.controller.windowButtons.extend(
            [
                self.btn_sheets,
                self.btn_img,
                self.btn_pdf,
                self.btn_uniq_pdf,
            ]
        )

    def set_button_key(self, text: str, cmd: callable):
        for k in self.buttonsKey.keys():
            if k == text:
                break # Não alterar botões já existentes
            
        btn = ttk.Button(
            self.frameButtons, 
            text=text, 
            command=cmd,
            style=self.controller.buttonsTheme.value,
            padding=self._PADDING,
            width=self._WIDTH,
        )
        self.buttonsKey[text] = btn
        self.controller.windowButtons.append(self.buttonsKey[text])
        if self.orientation == Orientation.V:
            btn.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            btn.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)

    def set_button_image(self, on_click: callable):
        if self.orientation == Orientation.V:
            self.btn_img.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            self.btn_img.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
        self.btn_img.config(command=on_click)

    def set_button_pdf(self, on_click: callable):
        if self.orientation == Orientation.V:
            self.btn_pdf.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            self.btn_pdf.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
        self.btn_pdf.config(command=on_click)
        
    def set_button_uniq_pdf(self, on_click: callable):
        if self.orientation == Orientation.V:
            self.btn_uniq_pdf.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            self.btn_uniq_pdf.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
        self.btn_uniq_pdf.config(command=on_click)
        
    def set_button_sheets(self, on_click: callable):
        if self.orientation == Orientation.V:
            self.btn_sheets.pack(expand=True, fill='both', padx=1, pady=1)
        else:
            self.btn_sheets.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
        self.btn_sheets.config(command=on_click)
            
   

class WidgetScrow(object):
    def __init__(self, frame: ttk.Frame, *, width:int = 48, height: int = 8):
        self.frame: ttk.Frame = frame 
        
        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=1, pady=1)
        
        # Listbox
        self.listbox: tk.Listbox = tk.Listbox(
            self.frame, 
            yscrollcommand=self.scrollbar.set, 
            width=width, 
            height=height,
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Conectar a scrollbar à listbox
        self.scrollbar.config(command=self.listbox.yview)
        
    def update_text(self, value: str):
        """Inserir novo texto na scrowbar"""
        # Adicionar textos
        self.listbox.insert(tk.END, value)
        
    def update_texts(self, values: List[str], include_info:str=None):
        """Adiciona uma lista de textos na scrowbar"""
        for value in values:
            if include_info is None:
                self.listbox.insert(tk.END, value)
            else:
                self.listbox.insert(tk.END, f"{include_info} {value}")
            
    def clear(self):
        """Limpar o texto da scrowbar"""
        self.listbox.delete(0, tk.END)  # Limpa todos os itens
        
    
class WidgetProgressBar(object):
    """
        Criar uma barra de progresso padrão.
    """
    def __init__(
                    self, 
                    frame:ttk.Frame, 
                    *, 
                    mode: LibProgress = LibProgress.INDETERMINATE, 
                    orientation:str='horizontal', 
                    default_text:str='0%',
                    theme: AppThemes = AppThemes.PBAR_GREEN,
                ):
        """Barra de progresso."""
        self.mode: LibProgress = mode
        self.container_labels: ttk.Frame = ttk.Frame(
            frame,
            style=AppThemes.LIGHT_PURPLE.value,
        )
        self.container_labels.pack(expand=True, fill='x', padx=1, pady=1)
        self.container_pbar: ttk.Frame = ttk.Frame(
            frame,
            style=AppThemes.LIGHT_PURPLE.value,
        )
        self.container_pbar.pack(expand=True, fill='x', padx=1, pady=1)
        
        self._label_text: ttk.Label = ttk.Label(self.container_labels, text='-')
        self._label_text.pack(expand=True, padx=1, pady=1)
        self._label_progress: ttk.Label = ttk.Label(self.container_labels, text=default_text)
        self._label_progress.pack(expand=True, padx=1, pady=1)
        
        self._pbar: ttk.Progressbar = ttk.Progressbar(
            self.container_pbar, 
            orient=orientation,
            style=theme.value,
        )
        self._pbar.pack(expand=True, fill='x', padx=1, pady=1)
        
        if self.mode == LibProgress.INDETERMINATE:
            self.implement_pbar:ProgressBarTkIndeterminate =  ProgressBarTkIndeterminate(
                label_text=self._label_text,
                label_progress=self._label_progress,
                progress_bar=self._pbar,
            )
        elif self.mode == LibProgress.DETERMINATE:
            self.implement_pbar:ProgressBarTkDeterminate =  ProgressBarTkDeterminate(
                label_text=self._label_text,
                label_progress=self._label_progress,
                progress_bar=self._pbar,
            )
        else:
            raise ValueError(f'{__class__.__name__} Use: determinate OU indeterminate')
        self.progress_adapter:ProgressBarAdapter = ProgressBarAdapter(self.implement_pbar)
        
    def update(self, prog:float, text:str):
        self.progress_adapter.update(prog, text)
        
    def update_text(self, text:str):
        self.progress_adapter.update_text(text)
        
    def update_percent(self, prog: float):
        self.progress_adapter.update_percent(prog)
        
    def get_progress(self) -> int:
        return self.progress_adapter.get_current_percent()
    
    def start(self):
        self.progress_adapter.start()
        
    def stop(self):
        self.progress_adapter.stop()
  
  
        