#!/usr/bin/env python3
from __future__ import annotations
import os
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod
from typing import Tuple, List
from tkinter import filedialog

from soup_files import (
    File, Directory, InputFiles, UserAppDir, LibraryDocs, JsonData, JsonConvert
)

from gui_stream.app_ui.core.observer import (
    AbstractObserver, AbstractNotifyProvider, ControllerNotifyProvider,
)
from gui_stream.app_ui.core.themes import AppThemes


class PreferencesApp(ControllerNotifyProvider):
    """Preferencias do aplicativo."""
    _instance_preferences_app = None  # Singleton

    def __new__(cls, *args, **kwargs):
        if cls._instance_preferences_app is None:
            cls._instance_preferences_app = super(PreferencesApp, cls).__new__(cls)
        return cls._instance_preferences_app

    def __init__(self, app_dir: UserAppDir):
        super().__init__()
        self.appDir: UserAppDir = app_dir
        self.appTheme: AppThemes = AppThemes.DARK
        self.initialInputDir: Directory = self.appDir.userFileSystem.userDownloads
        self.initialOutputDir: Directory = self.appDir.workspaceDirApp
        self.saveDir: Directory = self.appDir.workspaceDirApp
        self.fileConfig: File = self.appDir.config_dir_app().join_file(f'{self.appDir.appname}.json')
        self._config: Dict[str, str] = {}

    @property
    def config(self) -> Dict[str, str]:
        return self._config

    @config.setter
    def config(self, new: Dict[str, str]):
        self._config = new

    def set_config(self, key: str, value: str):
        self._config[key] = value

    def to_json(self) -> JsonData:
        default: Dict[str, str] = {
            'app_theme': self.appTheme.value,
            'initial_input_dir': self.initialInputDir.absolute(),
            'initial_output_dir': self.initialOutputDir.absolute(),
            'save_dir': self.saveDir.absolute(),
        }

        for _key in default.keys():
            self._config[_key] = default[_key]
        d = JsonConvert.from_dict(default)
        return d.to_json_data()


class AppFileDialog(ABC):
    """Caixa de dialogo para seleção de vários tipos de arquivos."""

    _instance_file_dialog = None  # Singleton

    def __new__(cls, *args, **kwargs):
        if cls._instance_file_dialog is None:
            cls._instance_file_dialog = super(AppFileDialog, cls).__new__(cls)
        return cls._instance_file_dialog

    def __init__(self, app_prefs: PreferencesApp) -> None:
        self.prefs_app: PreferencesApp = app_prefs

    def open_filename(self, input_type: LibraryDocs = LibraryDocs.ALL) -> str | None:
        """
            Caixa de dialogo para selecionar um arquivo
        """

        _filesTypes = [("Todos os arquivos", "*"), ]
        _title = 'Selecione um arquivo'
        if input_type == LibraryDocs.SHEET:
            _filesTypes = [("Planilhas", "*.xlsx"), ("Arquivos CSV", "*.csv *.txt")]
            _title = 'Selecione uma planilha'
        elif input_type == LibraryDocs.EXCEL:
            _filesTypes = [("Arquivos Excel", "*.xlsx")]
            _title = 'Selecione uma planilha'
        elif input_type == LibraryDocs.IMAGE:
            _filesTypes = [("Arquivos de Imagem", "*.png *.jpg *.jpeg *.svg")]
            _title = 'Selecione Imagens'
        elif input_type == LibraryDocs.PDF:
            _filesTypes = [("Arquivos PDF", "*.pdf *.PDF"), ]
            _title = 'Selecione arquivos PDF'
        #
        filename: str = filedialog.askopenfilename(
            title=_title,
            initialdir=self.prefs_app.initialInputDir.absolute(),
            filetypes=_filesTypes,
        )

        if not filename:
            return None
        _dirname: str = os.path.dirname(filename)
        self.prefs_app.initialInputDir = Directory(_dirname)
        return filename

    def open_filesname(self, input_type: LibraryDocs = LibraryDocs.ALL) -> Tuple[str]:
        """
            Selecionar um ou mais arquivos
        """

        _filesTypes = [("Todos os arquivos", "*"), ]
        _title = 'Selecione um arquivo'
        if input_type == LibraryDocs.SHEET:
            _filesTypes = [("Planilas Excel CSV", "*.xlsx *.csv"), ("Arquivos CSV", "*.csv *.txt")]
            _title = 'Selecione uma planilha'
        elif input_type == LibraryDocs.EXCEL:
            _filesTypes = [("Arquivos Excel", "*.xlsx")]
            _title = 'Selecione uma planilha'
        elif input_type == LibraryDocs.IMAGE:
            _filesTypes = [("Arquivos de Imagem", "*.png *.jpg *.jpeg *.svg")]
            _title = 'Selecione Imagens'
        elif input_type == LibraryDocs.PDF:
            _filesTypes = [("Arquivos PDF", "*.pdf *.PDF"), ]
            _title = 'Selecione arquivos PDF'
        #
        files = filedialog.askopenfilenames(
            title=_title,
            initialdir=self.prefs_app.initialInputDir.absolute(),
            filetypes=_filesTypes,
        )

        if len(files) > 0:
            _dirname: str = os.path.abspath(os.path.dirname(files[0]))
            self.prefs_app.initialInputDir = Directory(_dirname)
        return files

    def open_file_sheet(self) -> str | None:
        """
            Caixa de dialogo para selecionar um arquivo CSV/TXT/XLSX
        """
        return self.open_filename(LibraryDocs.SHEET)

    def open_files_sheet(self) -> Tuple[str]:
        """
            Selecionar uma ou mais planilhas
        """
        return self.open_filesname(LibraryDocs.SHEET)

    def open_files_image(self) -> Tuple[str]:
        return self.open_filesname(LibraryDocs.IMAGE)

    def open_files_pdf(self) -> Tuple[str]:
        return self.open_filesname(LibraryDocs.PDF)

    def open_folder(self, action_input=True) -> str | None:
        """Selecionar uma pasta"""
        if action_input == True:
            _initial: str = self.prefs_app.initialInputDir.absolute()
        else:
            _initial: str = self.prefs_app.initialOutputDir.absolute()

        _select_dir: str = filedialog.askdirectory(
            initialdir=_initial,
            title="Selecione uma pasta",
        )

        if _select_dir is None:
            return None
        _dirname = os.path.abspath(_select_dir)
        if action_input == True:
            self.prefs_app.initialInputDir = Directory(_dirname)
        else:
            self.prefs_app.initialOutputDir = Directory(_dirname)
        return _select_dir

    def save_file(self, type_file: LibraryDocs = LibraryDocs.ALL_DOCUMENTS) -> str | None:
        """Abre uma caixa de dialogo para salvar arquivos."""
        if type_file == LibraryDocs.SHEET:
            _default = '.xlsx'
            _default_types = [("Arquivos Excel", "*.xlsx"), ("Arquivos CSV", "*.csv")]
        elif type_file == LibraryDocs.EXCEL:
            _default = '.xlsx'
            _default_types = [("Arquivos Excel", "*.xlsx")]
        elif type_file == LibraryDocs.CSV:
            _default = '.csv'
            _default_types = [("Arquivos CSV", "*.csv"), ("Arquivos de texto", "*.txt")]
        elif type_file == LibraryDocs.PDF:
            _default = '.pdf'
            _default_types = [("Arquivos PDF", "*.pdf")]
        else:
            _default = '.*'
            _default_types = [("Salvar Como", "*.*")]

        # Abre a caixa de diálogo "Salvar Como"
        dir_path = filedialog.asksaveasfilename(
            defaultextension=_default,  # Extensão padrão
            filetypes=_default_types,  # Tipos de arquivos suportados
            title="Salvar arquivo como",
            initialdir=self.prefs_app.initialOutputDir.absolute(),
        )

        if not dir_path:
            return None
        self.prefs_app.initialOutputDir = Directory(dir_path)
        return dir_path


class ControllerFiles(ControllerNotifyProvider):
    """
        Arquivos e documentos selecionados pelo usuário com os botões.
    Esta classe também pode ser usada por classes OBSERVER.

    use o método add_observer(self, object)
    object: precisa ter o método .notify_change_files()
    para receber as notificações quando um novo arquivo for adicionado a este item.
    """

    def __init__(
                self,
                file_dialog: AppFileDialog,
                *,
                max_files: int = 2000
        ):
        super().__init__()
        self.fileDialog: AppFileDialog = file_dialog
        self._files: List[File] = []
        self.maxFiles: int = max_files
        self.numFiles: int = 0

    @property
    def fileConfig(self) -> File:
        return self.fileDialog.prefs_app.fileConfig

    @fileConfig.setter
    def fileConfig(self, new: File):
        self.fileDialog.prefs_app.fileConfig = new
        self.send_notify_files()

    @property
    def num_files_image(self) -> int:
        return len([f for f in self.get_files_image()])

    @property
    def num_files_csv(self) -> int:
        return len([f for f in self.get_files_csv()])

    @property
    def num_files_excel(self) -> int:
        return len([f for f in self.get_files_excel()])

    @property
    def num_files_sheet(self) -> int:
        return len([f for f in self.get_files_sheets()])

    @property
    def num_files_pdf(self) -> int:
        return len([f for f in self.get_files_pdf()])

    @property
    def files(self) -> List[File]:
        return self._files

    @files.setter
    def files(self, new: List[File]):
        if not isinstance(list, new):
            return
        if len(new) > self.maxFiles:
            new = new[0: self.maxFiles]
        self._files = new
        self.numFiles = len(self._files)

    @property
    def save_dir(self) -> Directory:
        return self.fileDialog.prefs_app.saveDir

    @save_dir.setter
    def save_dir(self, new: Directory):
        self.fileDialog.prefs_app.saveDir = new

    def select_file(self, type_file: LibraryDocs = LibraryDocs.ALL_DOCUMENTS):
        f: str = self.fileDialog.open_filename(type_file)
        if (f is None) or (f == ''):
            return
        fp = File(f)
        self.fileDialog.prefs_app.initialInputDir = Directory(fp.absolute()).parent()
        self.add_file(fp)
        self.send_notify_files()

    def select_files(self, type_file: LibraryDocs = LibraryDocs.ALL_DOCUMENTS):
        files: Tuple[str] = self.fileDialog.open_filesname(type_file)
        if len(files) < 1:
            return
        files_path = [File(f) for f in files]
        self.fileDialog.prefs_app.initialOutputDir = Directory(files_path[0].absolute()).parent()
        for fp in files_path:
            self.add_file(fp)
        self.send_notify_files()

    def select_dir(self, type_file: LibraryDocs = LibraryDocs.ALL_DOCUMENTS):
        d: str = self.fileDialog.open_folder(True)
        if (d is None) or (d == ""):
            return
        self.fileDialog.prefs_app.initialInputDir = Directory(d)
        input_files = InputFiles(self.fileDialog.prefs_app.initialInputDir, maxFiles=self.maxFiles)
        files: List[File] = input_files.get_files(file_type=type_file)
        self.add_files(files)

    def save_file(self, type_file: LibraryDocs = LibraryDocs.ALL) -> File:
        f: str = self.fileDialog.save_file(type_file)
        return File(f)

    def select_output_dir(self):
        """Setar um diretório para salvar arquivos."""
        d: str = self.fileDialog.open_folder(False)
        if (d is None) or (d == ""):
            print(f'{__class__.__name__} diretório vazio')
            return
        print(f'Alterando o SaveDir: {d}')
        self.fileDialog.prefs_app.saveDir = Directory(d)

    def add_file(self, file: File) -> None:
        if self.numFiles >= self.maxFiles:
            print(f'{__class__.__name__} o número máximo de arquivos já foi atingido: {self.maxFiles} !')
            return
        self._files.append(file)
        self.numFiles += 1
        print(f'Arquivo adicionado: [{self.numFiles}] {file.basename()}')
        self.send_notify()

    def add_files(self, files: List[File]):
        if self.numFiles >= self.maxFiles:
            print(f'{__class__.__name__} o número máximo de arquivos já foi atingido: {self.maxFiles} !')
            return

        for f in files:
            self._files.append(f)
            self.numFiles += 1
            if self.numFiles >= self.maxFiles:
                print(f'{__class__.__name__} o número máximo de arquivos já foi atingido: {self.maxFiles} !')
                break
        self.send_notify()

    def add_dir(self, d: Directory, *, file_type: LibraryDocs = LibraryDocs.ALL_DOCUMENTS):
        input_files: InputFiles = InputFiles(d, maxFiles=self.maxFiles)
        files = input_files.get_files(file_type=file_type)
        _files = [File(f.absolute()) for f in files]
        self.add_files(_files)

    def clear(self) -> None:
        """Limpar a lista de arquivos selecionados."""
        self._files.clear()
        self.numFiles = 0
        self.send_notify()

    def is_null(self) -> bool:
        return self.numFiles == 0

    def get_files_sheets(self) -> List[File]:
        files = []
        for f in self.files:
            if f.is_sheet():
                files.append(f)
        return files

    def get_files_csv(self) -> List[File]:
        return [f for f in self.files if f.is_csv()]

    def get_files_excel(self) -> List[File]:
        return [f for f in self.files if f.is_excel()]

    def get_files_pdf(self) -> List[File]:
        """Retorna uma lista de arquivos PDF"""
        return [f for f in self.files if f.is_pdf()]

    def get_files_image(self) -> List[File]:
        return [f for f in self.files if f.is_image()]


