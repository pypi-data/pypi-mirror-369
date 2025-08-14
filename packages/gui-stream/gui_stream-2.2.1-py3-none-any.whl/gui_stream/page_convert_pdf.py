#!/usr/bin/env python3

from typing import List
import tkinter as tk
from tkinter import ttk
from gui_stream.app_ui.ui.ui_pages import UiPage, TopBar
from gui_stream.app_ui.ui.widgets import (
    ProgressBarAdapter, WidgetFiles, Orientation, WidgetScrow, WidgetExportFiles
)
from gui_stream.controller_app import Controller
from soup_files import File
from convert_stream import (
    DocumentPdf, PdfStream, ImageObject,
    LibraryPDF, LibraryImage, LibImageToPDF, CreatePbar
)


class LocalPdfStream(PdfStream):

    def __init__(
            self, *,
            library_pdf: LibraryPDF = LibraryPDF.FITZ,
            library_image: LibraryImage = LibraryImage.OPENCV,
            lib_image_to_pdf: LibImageToPDF = LibImageToPDF.PILPDF,
            progress_bar: ProgressBarAdapter = CreatePbar().get(),
            maximum_pages: int = 3500
            ):
        #
        super().__init__(
            library_pdf=library_pdf,
            library_image=library_image,
            lib_image_to_pdf=lib_image_to_pdf,
            progress_bar=progress_bar,
            maximum_pages=maximum_pages
        )

    def add_files_images(self, images: List[File]):
        self.progress_bar.start()
        maxnum: int = len(images)
        for n, file in enumerate(images):
            self.progress_bar.update(
                ((n+1)/maxnum) * 100,
                f'Adicionando imagem: [{n+1} de {maxnum}] {file.basename()}'
            )
            self.add_image(ImageObject.create_from_file(file))
        self.progress_bar.stop()

    def rotate(self, r: int):
        self.progress_bar.start()
        for n, page in enumerate(self.document.get_pages()):
            self.progress_bar.update(
                ((n+1)/self.document.get_num_pages()) * 100,
                f'Rotacionando páginas: [{n+1} de {self.document.get_pages()}]'
            )
            page.rotate(r)
        self.progress_bar.stop()


class PageConvertPdf(UiPage):
    
    def __init__(self, *, controller: Controller):
        super().__init__(controller=controller)
        self.controller: Controller = controller
        self.PAGE_ROUTE = '/home/pdf'
        self.PAGE_NAME = 'Conversão de PDF'
        self.GEOMETRY = '730x310'
        # 
        self.frameMain = ttk.Frame(self)
        self.frameMain.pack(expand=True, fill='both', padx=1, pady=1)
        
        # Frames 
        self.frameWidgets = ttk.Frame(self.frameMain)
        self.frameWidgets.pack(expand=True, fill='both')
        # Frame Scrow
        self.frameScrow = ttk.Frame(self.frameWidgets)
        self.frameScrow.pack(expand=True, fill='both', padx=1, pady=1, side=tk.LEFT)
        # Frame Export
        self.frameExport = ttk.Frame(self.frameMain)
        self.frameExport.pack(expand=True, fill='both', padx=1, pady=1)
        #
        self.w_file = WidgetFiles(
            self.frameScrow, 
            orientation=Orientation.H, 
            controller=self.controller    
        )
        self.w_file.set_button_pdf()
        self.w_file.set_button_image()
        self.w_file.set_button_folder()
        self.w_file.set_button_clear()
        #
        self.scrow: WidgetScrow = WidgetScrow(self.frameScrow, width=42, height=6)
        
        # Botão rotacionar
        self.frameRotate = ttk.Frame(self.frameScrow)
        self.frameRotate.pack(padx=1, pady=1)
        self.btn_rotate = ttk.Button(
            self.frameRotate,
            text='Rotacionar',
            command=self.execute_rotation,
            style=self.controller.buttonsTheme.value,
        )
        self.btn_rotate.pack(padx=1, pady=1, expand=True, fill='both')
        # Combo rotacionar
        self.combo_rotate = ttk.Combobox(
            self.frameRotate, 
            values=[
                    '90',
                    '180',
                    '270',
                    '-90',
                ],
        )
        self.combo_rotate.set('90')
        self.combo_rotate.pack(padx=1, pady=1)
        
        self.widgetExport: WidgetExportFiles = WidgetExportFiles(
            self.frameExport,
            controller=self.controller,
            orientation=Orientation.H,
        )
        self.widgetExport.set_button_uniq_pdf(self.export_uniq_pdf)
        self.widgetExport.set_button_image(self.export_images)
        self.widgetExport.set_button_pdf(self.export_multi_pdf)
        self.widgetExport.set_button_sheets(self.export_sheet)

        #self.__pdf_stream: LocalPdfStream = LocalPdfStream(progress_bar=self.controller.topBar.pbar)
        self.__pdf_stream: LocalPdfStream = None
        
    @property
    def streamPdf(self) -> LocalPdfStream:
        return self.__pdf_stream
    
    @streamPdf.setter
    def streamPdf(self, new: LocalPdfStream):
        self.__pdf_stream = new
        
    @property
    def topBar(self) -> TopBar:
        return self.controller.topBar
    
    def _create_stream_pdf(self) -> None:
        self.topBar.pbar.start()
        stream = LocalPdfStream(
            library_pdf=LibraryPDF.FITZ, 
            progress_bar=self.topBar.pbar,
        )
        # Adicionar arquivos PDF.
        stream.add_files_pdf(self.controller.controllerFiles.get_files_pdf())  
        # Adicionar arquivos de Imagem.
        stream.add_files_images(self.controller.controllerFiles.get_files_image()) 
        self.streamPdf = stream
        self.topBar.set_text(f'-')
        self.topBar.pbar.stop()
    
    def export_uniq_pdf(self):
        if self.is_running():
            return
        self.thread_main_create(self._run_export_uniq_pdf)
    
    def _run_export_uniq_pdf(self):
        if self.streamPdf is None:
            self._create_stream_pdf()
        self.topBar.pbar.start()
        self.topBar.set_text(f'Exportando PDF')
        output: File = self.controller.saveDir.concat('PDF', create=True).join_file('Documento.pdf')
        self.streamPdf.to_file_pdf(output)
        self.topBar.set_text(f'Arquivo exportado em: {output.basename()}')
        self.topBar.pbar.stop()

    def export_images(self):
        if self.is_running():
            return
        self.thread_main_create(self._run_export_images)
    
    def _run_export_images(self):
        if self.streamPdf is None:
            self._create_stream_pdf()
        self.topBar.pbar.start()
        
        self.topBar.set_text(f'Exportando Imagens')
        output_dir = self.controller.saveDir.concat('PDF', create=True).concat('PDF Para Imagens', create=True)
        self.streamPdf.to_files_image(output_dir)
        self.topBar.set_text(f'Imagens exportadas em: {output_dir.basename()}')
        self.topBar.pbar.stop()
    
    def export_multi_pdf(self):
        if self.is_running():
            return
        self.thread_main_create(self._run_export_multi_pdf)
    
    def _run_export_multi_pdf(self):
        if self.streamPdf is None:
            self._create_stream_pdf()
        self.topBar.pbar.start()
        
        self.topBar.set_text(f'Exportando arquivos em PDF')
        output_dir = self.controller.saveDir.concat('PDF', create=True).concat('PDF Dividido', create=True)
        self.streamPdf.to_files_pdf(output_dir)
        self.topBar.set_text(f'Arquivos exportado em: {output_dir.basename()}')
        self.topBar.pbar.stop()
        
    def execute_rotation(self):
        if self.is_running():
            return
        self.thread_main_create(self._run_execute_rotation)
    
    def _run_execute_rotation(self):
        if self.streamPdf is None:
            self._create_stream_pdf()
        self.topBar.pbar.start()
        self.topBar.set_text(f'Rotacionando páginas, aguarde!')
        self.streamPdf.rotate(int(self.combo_rotate.get()))
        self.topBar.pbar.stop()
    
    def export_sheet(self):
        if self.is_running():
            return
        self.thread_main_create(self._run_export_sheet)
    
    def _run_export_sheet(self):
        self.topBar.pbar.start()
        doc = DocumentPdf(progress_bar=self.topBar.pbar)
        doc.add_files_pdf(self.controller.controllerFiles.get_files_pdf())
        self.topBar.set_text(f'Exportando Planilha Excel, aguarde!')
        output = self.controller.saveDir.concat('Planilhas', create=True).join_file('Documentos.xlsx')
        doc.to_excel(output)
        self.topBar.set_text(f'Planilha exportada em: {output.basename()}')
        self.topBar.pbar.stop()
        
        