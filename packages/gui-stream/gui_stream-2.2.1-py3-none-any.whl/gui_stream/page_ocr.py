#!/usr/bin/env python3
#
from __future__ import annotations
from typing import List
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from gui_stream.app_ui import AbstractNotifyProvider
from gui_stream.controller_app import Controller
from gui_stream.app_ui.ui.ui_pages import UiPage
from gui_stream.app_ui.ui.widgets import (
    WidgetFiles, WidgetScrow, Orientation, ProgressBarAdapter
)
from gui_stream.app_ui.ui.ui_pages import TopBar
from convert_stream import (
    PageDocumentPdf,
    PdfStream,
    DocumentPdf,
    ImageObject,
    LibraryPDF,
)
from soup_files import File
from ocr_stream import RecognizeImage, RecognizePdf, BinaryTesseract


#========================================================#
# Reconhecer Texto em PDF
#========================================================#
class PageRecognizePDF(UiPage):
    def __init__(self, *, controller: Controller):
        super().__init__(controller=controller)
        self.controller: Controller = controller
        # Inscreverse no objeto notificador
        self.controller.controllerFiles.add_observer(self)
        self.PAGE_ROUTE = '/home/ocr'
        self.PAGE_NAME = 'OCR Documentos'
        self.GEOMETRY = "630x345"
        self.reconized_pages: set[PageDocumentPdf] = set()
        
        self.frameWidgets = ttk.Frame(self)
        self.frameWidgets.pack(expand=True, fill='both', padx=1, pady=1)
        # Frame para os botões de input
        self.frameInputFiles = ttk.Frame(
            self.frameWidgets,
            style=self.controller.appTheme.value,
        )
        self.frameInputFiles.pack(side=tk.LEFT, expand=True, fill='both', padx=2, pady=3)

        self.widget_input = WidgetFiles(
            self.frameInputFiles, controller=self.controller, orientation=Orientation.V,
        )
        self.widget_input.set_button_image()
        self.widget_input.set_button_pdf()
        self.widget_input.set_button_folder()
        self.widget_input.set_button_clear()

        # Frame a direita
        self.frame_r = ttk.Frame(self.frameWidgets, style=self.controller.appTheme.value)
        self.frame_r.pack(expand=True, padx=3, pady=2)

        # botões de ação
        self.frame_btns = ttk.Frame(self.frame_r)
        self.frame_btns.pack(expand=True, fill='both', padx=1, pady=1)
        # Botão exportar lote
        self.btn_export_multi = ttk.Button(
            self.frame_btns,
            text='Exportar lote PDF',
            command=self.recognize_to_pdfs,
            style=self.controller.buttonsTheme.value,
            width=16,
        )
        self.btn_export_multi.pack(side=tk.LEFT, padx=1, pady=1, expand=True)

        # Botão exportar único PDF.
        self.btn_export_uniq = ttk.Button(
            self.frame_btns,
            text='Exportar único PDF',
            command=self.recognize_to_uniq_pdf,
            style=self.controller.buttonsTheme.value,
            width=16,
        )
        self.btn_export_uniq.pack(padx=1, pady=1, expand=True)
        # Container Scrollbar
        self.frame_scrow = ttk.Frame(self.frame_r)
        self.frame_scrow.pack(expand=True, fill='both', padx=1, pady=1)
        self.scrow: WidgetScrow = WidgetScrow(self.frame_scrow, height=12)

        self.controller.windowButtons.append(self.btn_export_uniq)
        self.controller.windowButtons.append(self.btn_export_multi)
        self.controller.windowFrames.extend(
            [
                self.frameInputFiles,
                self.frame_btns,
            ]
        )

    @property
    def topBar(self) -> TopBar:
        return self.controller.topBar
    
    @property
    def pbar(self) -> ProgressBarAdapter:
        return self.controller.topBar.pbar

    def recognize_to_pdfs(self):
        if not self.get_binary_tess().exists():
            messagebox.showerror('Erro', 'Instale o tesseract para prosseguir!')
            return
        if self.is_running():
            messagebox.showwarning('Erro', 'Existe outra operação em andamento, aguarde!')
            return
        if (self.controller.controllerFiles.num_files_image < 1) and (self.controller.controllerFiles.num_files_pdf < 1):
            messagebox.showinfo('Selecione documentos', 'Selecione uma imagem ou PDF para prosseguir!')
            return
        self.thread_main_create(self._run_recognize_to_pdfs)
        
    def _run_recognize_to_pdfs(self):
        """
            Reconhecer os arquivos PDF e Imagens adicionadas e exportar para PDFs individuais.
        """
        self.pbar.start()
        files_image = self.controller.controllerFiles.get_files_image()
        max_images = len(files_image)
        # Reconhecer imagens.
        rec: RecognizeImage = RecognizeImage.create(
            binary_tess=self.controller.binary,
        )

        doc = DocumentPdf(progress_bar=self.pbar)
        for num, file in enumerate(files_image):
            output_path: File = self.controller.controllerFiles.save_dir.join_file(f'{file.name()}.pdf')
            prog = (num/max_images) * 100
            if output_path.path.exists():
                self.update_text_scrow(f'[PULANDO]: o arquivo já existe: {output_path.basename()}')
                continue

            self.pbar.update(
                prog, 
                f'Reconhecendo imagem: {num+1} de {max_images} {file.basename()}'
            )
            self.update_text_scrow(f'Reconhecendo imagem: {num+1} de {max_images} {file.basename()}')
            img = ImageObject.create_from_file(file)
            img.set_paisagem()
            bt: bytes = rec.image_recognize(img).bytes_recognized
            self.pbar.update(prog, f'Exportando: {output_path.basename()}')
            doc.add_page(PageDocumentPdf.create_from_page_bytes(bt, library=LibraryPDF.FITZ))
            doc.to_file_pdf(output_path)
            doc.clear()
            
        # Reconhecer os arquivos PDF
        files_pdf = self.controller.controllerFiles.get_files_pdf()
        max_pdf = len(files_pdf)
        pdf_stream = PdfStream(progress_bar=self.pbar)
        rec_pdf: RecognizePdf = RecognizePdf(rec)
        doc.clear()
        for n, file_pdf in enumerate(files_pdf):
            progress_files = ((n+1)/max_pdf) * 100
            self.pbar.update(
                progress_files, 
                f'Adicionando arquivo: {n+1} de {max_pdf} {file_pdf.basename()}'
            )
            self.update_text_scrow(f'Adicionando arquivo: {n+1} de {max_pdf} {file_pdf.basename()}')
            pdf_stream.add_file_pdf(file_pdf)
            
            # Converter as páginas em imagem e aplicar o OCR.
            for num_page, page in enumerate(pdf_stream.pages):
                output_path = self.controller.controllerFiles.save_dir.join_file(
                    f'{file_pdf.name()}-pag-{page.page_number}.pdf'
                )
                if output_path.path.exists():
                    self.update_text_scrow(f'PULANDO: o arquivo já existe: {output_path.basename()}')
                    # Pular
                    continue
                
                self.pbar.update(
                        progress_files, 
                        f'OCR página: [{page.page_number} de {pdf_stream.num_pages}] Documento {n+1} de {max_pdf}'
                    )
                self.update_text_scrow(
                        f'OCR página: [{page.page_number} de {pdf_stream.num_pages}] Documento {n+1} de {max_pdf}'
                    )
                
                doc.add_page(rec_pdf.recognize_page_pdf(page))
                self.pbar.update(progress_files, f'Exportando: {output_path.basename()}')
                doc.to_file_pdf(output_path)
                doc.clear()
            pdf_stream.clear()
        
        self.pbar.update(100, 'Operação finalizada!')
        self.pbar.stop()
        self.thread_main_stop()

    def recognize_to_uniq_pdf(self):
        if not self.get_binary_tess().exists():
            messagebox.showerror('Erro', 'Instale o tesseract para prosseguir!')
            return
        if self.is_running():
            messagebox.showwarning('Erro', 'Existe outra operação em andamento, aguarde!')
            return
        if (self.controller.controllerFiles.num_files_image < 1) and (self.controller.controllerFiles.num_files_pdf < 1):
            messagebox.showinfo('Selecione documentos', 'Selecione uma imagem ou PDF para prosseguir!')
            return
        self.thread_main_create(self._run_recognize_uniq_pdf)

    def _run_recognize_uniq_pdf(self):
        self.pbar.start()
        document = DocumentPdf(LibraryPDF.FITZ, progress_bar=self.pbar) 
        pdf_stream = PdfStream(library_pdf=LibraryPDF.FITZ, progress_bar=self.pbar)
        rec_pdf: RecognizePdf = RecognizePdf(self.get_recognize_image())

        # Reconhecer as imagens e converter em páginas PDF para adicionar ao documento
        files_image: list[File] = self.controller.controllerFiles.get_files_image()
        max_images: int = len(files_image)
        for num_image, file in enumerate(files_image):
            prog: float = ((num_image+1)/max_images) * 100
            self.pbar.update(prog, f'Reconhecendo imagem: {num_image+1} de {max_images}')
            self.update_text_scrow(f'Reconhecendo imagem: {num_image+1} de {max_images}')
            # Converter o arquivo em imagem e aplicar o OCR
            im = ImageObject.create_from_file(file)
            page = self.get_recognize_image().image_recognize(im).to_page_pdf()
            document.add_page(page)
        
        # Reconhecer PDF.
        files_pdf: list[File] = self.controller.controllerFiles.get_files_pdf()
        max_pdf: int = len(files_pdf)
        for num_pdf, file in enumerate(files_pdf):
            prog: float = (num_pdf/max_pdf) * 100
            self.pbar.update(prog, f'Reconhecendo PDF: {num_pdf} de {max_pdf}')
            pdf_stream.add_file_pdf(file)
            # Reconhecer cada página
            for page in pdf_stream.pages:
                self.pbar.update(
                    prog, 
                    f'Reconhecendo PDF: {num_pdf} de {max_pdf} [página {page.page_number} de {pdf_stream.num_pages}]'
                )
                self.update_text_scrow(
                    f'Reconhecendo PDF: {num_pdf} de {max_pdf} [página {page.page_number} de {pdf_stream.num_pages}]'
                )
                new_page = rec_pdf.recognize_page_pdf(page)
                document.add_page(new_page)
                pdf_stream.clear()
        # Salvar o documento
        output_path: File = self.controller.controllerFiles.save_dir.join_file('DocumentoOCR.pdf')
        if output_path.path.exists():
            # Renomear o arquivo repetido
            _count: int = 1
            while True:
                output_path = self.controller.controllerFiles.save_dir.join_file(f'DocumentoOCR-({_count}).pdf')
                if not output_path.path.exists():
                    break
                _count += 1
        self.pbar.update_text(f'Salvando: {output_path.basename()}')
        self.update_text_scrow(f'Salvando: {output_path.basename()}')
        document.to_file_pdf(output_path)
        self.pbar.update(100, 'Operação finalizada!')
        self.pbar.stop()
        self.thread_main_stop()
        
    def get_binary_tess(self) -> BinaryTesseract:
        return self.controller.binary

    def get_recognize_image(self) -> RecognizeImage:
        return RecognizeImage.create(binary_tess=self.get_binary_tess())

    def update_text_scrow(self, value: str):
        # Adicionar textos
        self.scrow.update_text(value)
        
    def update_current_scrow_values(self, values: List[str], include_info=None):
        self.scrow.update_texts(values, include_info)
            
    def clear_current_scrow_bar(self):
        self.scrow.clear()  # Limpa todos os itens
        
    def receiver_notify(self, notify_provide: AbstractNotifyProvider = None):
        pass
        
    def set_size_screen(self):
        self.controller.geometry(self.GEOMETRY)
        self.controller.title(self.PAGE_NAME)

    def update_state(self):
        pass
