#!/usr/bin/env python3
#


import pandas as pd
import os
from abc import ABC, abstractmethod
from typing import Optional

from sheetlib.models.m_progress import ABCProgressBar
from sheetlib.progress_bar import ProgressBarAdapter, ProgressBarSimple
from sheetlib.utils import File

class ABCSheetWriter(ABC):
    def __init__(self, path: File, *, progress: ABCProgressBar = ProgressBarSimple()):
        self.file_path:File = path
        self.progress = ProgressBarAdapter(progress)
        self._running:bool = False
        
    def is_running(self) -> bool:
        return self._running

    @abstractmethod
    def save(self, df: pd.DataFrame, *, index:bool=False):
        pass


class CSVSave(ABCSheetWriter):
    
    def __init__(self, path:File, *, progress = ProgressBarSimple()):
        super().__init__(path, progress=progress)
    
    def save(self, df: pd.DataFrame, *, index:bool=False):
        if df is None or df.empty:
            print("DataFrame inválido.")
            return

        self._running = True
        total_rows = len(df)
        self.progress.start()
        self.progress.update_progress("0%", "Iniciando gravação do CSV")

        with open(self.file_path.absolute(), mode="w", encoding="utf-8", newline='') as f:
            for i, chunk in enumerate(range(0, total_rows, 1000)):
                df.iloc[chunk:chunk + 1000].to_csv(f, index=index, header=(chunk == 0), mode='a')
                percent = ((chunk + 1000) / total_rows) * 100
                self.progress.update_progress(f"{percent:.1f}%", f"Gravando CSV ({int(percent)}%)")

        self.progress.update_progress("100%", "Gravação concluída")
        self.progress.stop()
        self._running = False


class ExcelSave(ABCSheetWriter):
    def __init__(self, path:File, progress = ProgressBarSimple()):
        super().__init__(path, progress=progress)
        
    def save(self, df: pd.DataFrame, *, index:bool=False):
        if df is None or df.empty:
            print("DataFrame inválido.")
            return

        self._running = True
        self.progress.start()
        self.progress.update_progress("0%", "Iniciando gravação do Excel")

        df.to_excel(self.file_path.absolute(), index=index)

        self.progress.update_progress("100%", "Gravação concluída")
        self.progress.stop()
        self._running = False


class SheetOutputStream(object):
    def __init__(self, file_path: File, *, progress: ABCProgressBar):
        self.file_path = file_path
        self.sheet_writer:ABCSheetWriter = self._create_writer(file_path, progress)

    def _create_writer(self, path: File, progress: ABCProgressBar) -> ABCSheetWriter:
        #ext = os.path.splitext(path)[1].lower()
        if path.is_csv():
            return CSVSave(path, progress=progress)
        elif path.is_excel():
            return ExcelSave(path, progress=progress)
        else:
            print(f"Formato de arquivo não suportado: {path.basename()}")
            return None

    def write(self, df: pd.DataFrame, *, index=False):
        if self.sheet_writer is None:
            print(f"Formato de arquivo não suportado: {self.file_path.basename()}")
            return None
        self.sheet_writer.save(df, index=index)
