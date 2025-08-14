#!/usr/bin/env python3
#
from convert_stream import ImageObject, LibraryImage
from soup_files import File
from gui_stream.app_ui.ui.ui_pages import UiPage, UiController, TopBar
from gui_stream.app_ui.ui.widgets import (
    WidgetFiles,
    WidgetScrow,
    WidgetExportFiles,
    Orientation,
)

from tkinter import ttk
from tkinter import messagebox
import tkinter as tk


class PageEditImages(UiPage):
    def __init__(self, *, controller):
        super().__init__(controller=controller)
        self.controller: UiController = controller
        self.PAGE_ROUTE = '/home/images'
        self.PAGE_NAME = 'Editar Imagens'
        self.GEOMETRY = '580x320'

        # Inscrever a página atual no objeto notificador de arquivos.
        self.controller.controllerFiles.add_observer(self)
        self.processed_images: set[ImageObject] = set()
        self._processed_paisagem: bool = False
        self._processed_gray: bool = False

        self.frameWidgets = ttk.Frame(self)
        self.frameWidgets.pack(expand=True, fill='both')

        # Frame com botões para importar arquivos.
        self.frameInput = ttk.Frame(self.frameWidgets)
        self.frameInput.pack(expand=True, fill='both', padx=1, pady=1)
        # Botões para importar arquivos.
        self.w_row_input = WidgetFiles(
            self.frameInput, controller=self.controller, orientation=Orientation.H,
        )
        self.w_row_input.set_button_image()
        self.w_row_input.set_button_folder()
        self.w_row_input.set_button_clear()

        # Frame para os widgets inferiores
        self.frameDow = ttk.Frame(self.frameWidgets)
        self.frameDow.pack(side=tk.LEFT, expand=True, fill='both', padx=1, pady=1)

        # Frame para scrow e botões de exportação
        self.frameScrowBar = ttk.Frame(self.frameDow)
        self.frameScrowBar.pack(side=tk.LEFT, expand=True, fill='both', padx=1, pady=1)
        # Scrow
        self.scrow = WidgetScrow(self.frameScrowBar, width=40, height=5)

        # Frame para botões de exportação de arquivos.
        self.frameButtons = ttk.Frame(self.frameDow)
        self.frameButtons.pack(expand=True, fill='both', padx=1, pady=1)

        self.export: WidgetExportFiles = WidgetExportFiles(
            self.frameButtons,
            orientation=Orientation.V,
            controller=self.controller
        )
        self.export.set_button_image(self.images_export)
        # botão para melhorar o texto embutido
        self.export.set_button_key('Melhorar o texto embutido', self.images_set_gray)
        self.export.set_button_key('Rotacionar como paisagem', self.images_set_paisagem)

        # Frame para rotarionar imagens
        self.frameRotate = ttk.Frame(self.frameButtons)
        self.frameRotate.pack(expand=True, fill='x', padx=1, pady=1)

        self.btn_rotate = ttk.Button(
            self.frameRotate,
            text='Rotacionar',
            command=self.images_set_rotation,
            style=self.controller.buttonsTheme.value,
        )
        self.btn_rotate.pack(side=tk.LEFT, padx=1, pady=1)

        # Combobox
        self.combo_opt_image = ttk.Combobox(
            self.frameRotate,
            values=[
                LibraryImage.ROTATION_90.value,
                LibraryImage.ROTATION_180.value,
                LibraryImage.ROTATION_270.value,
            ]
        )
        self.combo_opt_image.pack(side=tk.LEFT, padx=1, pady=1)
        self.combo_opt_image.set(LibraryImage.ROTATION_90.value)

    @property
    def topBar(self) -> TopBar:
        return self.controller.topBar

    def images_set_rotation(self):
        """
            Definir todas as imagens como paisagem
        """
        if not self.check_running():
            return
        if self.controller.controllerFiles.num_files_image < 1:
            messagebox.showwarning('Aviso', 'Adicione imagens para prosseguir!')
            return
        if self._processed_paisagem:
            messagebox.showinfo('OK', 'As imagens já foram definidas como paisagem!')
            return
        self.thread_main_create(self._run_set_rotation)

    def _run_set_rotation(self):
        self.topBar.pbar.start()
        if len(self.processed_images) == 0:
            files: list[File] = self.controller.controllerFiles.get_files_image()
            max_images = len(files)
            for num, file in enumerate(files):
                prog = (num / max_images) * 100
                self.topBar.set_text('Rotacionando imagens')
                self.topBar.pbar.update(prog, f'Rotacionando imagem: {num + 1} de {max_images}')
                self.scrow.update_text(f'Rotacionando imagem: {num + 1} de {max_images}')
                image: ImageObject = ImageObject.create_from_file(file)
                if self.combo_opt_image.get() == '90':
                    image.set_rotation(LibraryImage.ROTATION_90)
                elif self.combo_opt_image.get() == '180':
                    image.set_rotation(LibraryImage.ROTATION_180)
                elif self.combo_opt_image.get() == '270':
                    image.set_rotation(LibraryImage.ROTATION_270)
                self.processed_images.add(image)
        else:
            max_images = len(self.processed_images)
            for n, image in enumerate(self.processed_images):
                prog = (n / max_images) * 100
                self.topBar.pbar.update(prog, f'Rotacionando imagem: {n + 1} de {max_images}')
                self.scrow.update_text(f'Rotacionando imagem: {n + 1} de {max_images}')
                if self.combo_opt_image.get() == '90':
                    image.set_rotation(LibraryImage.ROTATION_90)
                elif self.combo_opt_image.get() == '180':
                    image.set_rotation(LibraryImage.ROTATION_180)
                elif self.combo_opt_image.get() == '270':
                    image.set_rotation(LibraryImage.ROTATION_270)

        self.topBar.pbar.update(100, 'Operação finalizada!')
        self.topBar.set_text('Rotacionando imagens OK')
        self.topBar.pbar.stop()
        self.thread_main_stop()

    def images_set_paisagem(self):
        """
            Definir todas as imagens como paisagem
        """
        if not self.check_running():
            return
        if self.controller.controllerFiles.num_files_image < 1:
            messagebox.showwarning('Aviso', 'Adicione imagens para prosseguir!')
            return
        if self._processed_paisagem:
            messagebox.showinfo('OK', 'As imagens já foram definidas como paisagem!')
            return
        self.thread_main_create(self._run_set_paisagem)

    def _run_set_paisagem(self):
        self.topBar.pbar.start()
        if len(self.processed_images) == 0:
            files: list[File] = self.controller.controllerFiles.get_files_image()
            max_images = len(files)
            for num, file in enumerate(files):
                prog = (num / max_images) * 100
                self.topBar.pbar.update(prog, f'Processando imagem: {num + 1} de {max_images}')
                self.scrow.update_text(f'Processando imagem: {num + 1} de {max_images}')
                img: ImageObject = ImageObject.create_from_file(file)
                img.set_paisagem()
                self.processed_images.add(img)
        else:
            max_images = len(self.processed_images)
            for n, image in enumerate(self.processed_images):
                prog = (n / max_images) * 100
                self.topBar.pbar.update(prog, f'Processando imagem: {n + 1} de {max_images}')
                self.scrow.update_text(f'Processando imagem: {n + 1} de {max_images}')
                image.set_paisagem()

        self.topBar.pbar.update(100, 'Operação finalizada!')
        self._processed_paisagem = True
        self.topBar.pbar.stop()
        self.thread_main_stop()

    def images_set_gray(self):
        """
            Escurecer imagens com o tom cinza.
        """
        if not self.check_running():
            return
        if self.controller.controllerFiles.num_files_image < 1:
            messagebox.showwarning('Aviso', 'Adicione imagens para prosseguir!')
            return
        if self._processed_gray:
            messagebox.showinfo('OK', 'As imagens já foram definidas como Cinza escuro!')
            return
        self.thread_main_create(self._run_image_gray)

    def _run_image_gray(self):
        self.topBar.pbar.start()
        if len(self.processed_images) == 0:
            files: list[File] = self.controller.controllerFiles.get_files_image()
            max_images = len(files)
            for num, file in enumerate(files):
                prog = (num / max_images) * 100
                self.topBar.pbar.update(prog, f'Processando imagem: {num + 1} de {max_images}')
                self.scrow.update_text(f'Processando imagem: {num + 1} de {max_images}')
                img: ImageObject = ImageObject.create_from_file(file)
                img.set_background_gray()
                self.processed_images.add(img)
        else:
            max_images = len(self.processed_images)
            for n, image in enumerate(self.processed_images):
                prog = (n / max_images) * 100
                self.topBar.pbar.update(prog, f'Processando imagem: {n + 1} de {max_images}')
                self.scrow.update_text(f'Processando imagem: {n + 1} de {max_images}')
                image.set_background_gray()

        self.topBar.pbar.update(100, 'Operação finalizada!')
        self.topBar.set_text('Operação finalizada!')
        self._processed_gray = True
        self.topBar.pbar.stop()
        self.thread_main_stop()

    def images_export(self):
        """
            Exportar todas as imagens para arquivos de imagem no disco.
        """
        if not self.check_running():
            return
        if self.controller.controllerFiles.num_files_image < 1:
            messagebox.showwarning('Aviso', 'Adicione imagens para prosseguir!')
            return
        if len(self.processed_images) < 1:
            messagebox.showinfo('OK', 'Nenhuma imagem foi processada!')
            return
        self.thread_main_create(self._run_export)

    def _run_export(self):
        self.topBar.pbar.start()
        ignored: int = 0  # Arquivos repetidos.
        exported: int = 0
        out = self.controller.controllerFiles.save_dir.concat('Imagens Processadas', create=True)
        max_images = len(self.processed_images)
        for num, img in enumerate(self.processed_images):
            output_path: File = out.join_file(f'imagem-{num + 1}.png')
            if output_path.path.exists():
                self.scrow.update_text(f'PULANDO: o arquivo já existe: {output_path.basename()}')
                ignored += 1
                continue

            prog = (num / max_images) * 100
            self.topBar.pbar.update(prog, f'Exportando: {num + 1} de {max_images}')
            self.scrow.update_text(f'Exportando: {num + 1} de {max_images}')
            img.to_file(output_path)
            exported += 1

        self.topBar.pbar.update(100, f'Arquivos exportados {exported} | ignorados/repetidos {ignored}')
        self.topBar.pbar.stop()
        self.thread_main_stop()

    def receiver_notify(self, notify_provide=None):
        """
            Recebe atualização de estado do objetos notificadores
        """
        # Verifica se atualização de estado foi a limpeza dos arquivos 
        # selecionados pelo usuário, se sim, limpar a propriedade .processed_images: set
        if self.controller.controllerFiles.numFiles == 0:
            self.processed_images.clear()
            self._processed_paisagem = False
            self._processed_gray = False

    def set_size_screen(self):
        self.controller.geometry(self.GEOMETRY)
        self.controller.title('Editar Imagens')
