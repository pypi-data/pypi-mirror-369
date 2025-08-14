#!/usr/bin/env python3
import os.path
import pandas as pd
import shutil
import threading
from typing import List
import tkinter as tk
from tkinter import ttk, messagebox

from gui_stream.app_ui import ControllerNotifyProvider
from gui_stream.app_ui.core.progress import ProgressBarAdapter
from gui_stream.app_ui.ui.ui_pages import UiPage, TopBar, AppThemes
from gui_stream.app_ui.ui.widgets import (
    WidgetRow, WidgetFiles, Orientation, WidgetScrow,
)
from gui_stream.controller_app import Controller
from gui_stream.sheets.load import SheetInputStream
from soup_files import File, Directory, LibraryDocs


class SheetName(str):

    def __init__(self):
        super().__init__()


class FileName(str):

    def __init__(self):
        super().__init__()


class PageConvertSheet(UiPage):
    """
        Fitrar texto em planilhas
    """
    def __init__(self, *, controller: Controller):
        super().__init__(controller=controller)
        self.controller: Controller = controller
        self.controller.add_observer(self)
        self.controller.controllerFiles.add_observer(self)
        self.PAGE_NAME = 'Planilhas'
        self.PAGE_ROUTE = '/home/sheets'
        self.GEOMETRY = '630x520'
        self.frame_main = ttk.Frame(self)
        self.frame_main.pack(expand=True, fill='both', padx=1, pady=1)
        #
        #                  {basename(): {sheet_name: DataFrame()}}
        self.filesnames_data_frame: dict[FileName, dict[SheetName, pd.DataFrame]] = {}
        #                  {basename(): File()}
        self.filenames_paths: dict[FileName, File] = {}
        self.files_loaded: set[str] = set()
        self.data: pd.DataFrame = None
        self.file_sheet_filter: File = None
        self.initUI()
        # Inscrever-se no notificador de arquivos
        # e notificador de tema/estilo
        self.controller.controllerFiles.add_observer(self)
        self.controller.appPrefs.add_observer(self) # Preferências do usuário.
        self.controller.appPrefs.send_notify()
        #===========================================================#
        # Frames
        # ===========================================================#
        self.frame_widgets = ttk.Frame(self.frame_main)
        self.frame_widgets.pack(expand=True, fill='both', padx=1, pady=1)
        # Frame com botões para importar arquivos
        self.frame_input = ttk.Frame(self.frame_widgets, style=self.controller.appTheme.value)
        self.frame_input.pack(expand=True, fill='both', padx=2, pady=1)
        
        # Frame para edição de dados
        self.frame_edit_sheet = ttk.Frame(self.frame_widgets)
        self.frame_edit_sheet.pack(expand=True, fill='both', padx=2, pady=1)

        # Frame para botões centrais
        self.frame_buttons = ttk.Frame(self.frame_edit_sheet, style=self.controller.appTheme.value)
        self.frame_buttons.pack(expand=True, fill='both', padx=2, pady=1)
        
        # Frame com widgets, lebels e botões para o filtro de dados
        self.frame_filter = ttk.Frame(self.frame_edit_sheet)
        self.frame_filter.pack(expand=True, fill='both', padx=2, pady=2)
        
        # Frame com botão e 3 labels para concatenar
        self.frame_concat = ttk.Frame(self.frame_edit_sheet, style=self.controller.appTheme.value)
        self.frame_concat.pack(expand=True, fill='both', padx=2, pady=2)
        
        # Frame combobox contendo as abas dos arquivos
        self.frame_info_sheets = ttk.Frame(self.frame_widgets)
        self.frame_info_sheets.pack(side=tk.LEFT, expand=True, fill='both', padx=2, pady=1)
        
        # Frame para srow bar.
        self.frame_scrow = ttk.Frame(self.frame_widgets, style=self.controller.appTheme.value)
        self.frame_scrow.pack(expand=True, fill='both', padx=2, pady=2)

        # Frame para opções de exportação dos dados.
        self.frame_export = ttk.Frame(self.frame_widgets, style=self.controller.appTheme.value)
        self.frame_export.pack(expand=True, fill='both', padx=1, pady=1)

        # Frame para barra de progresso.
        self.frame_pbar = ttk.Frame(self.frame_main)
        self.frame_pbar.pack(expand=True, fill='both', padx=2, pady=1)
        
        #-----------------------------------------------------#
        # Container superior para importar planilhas
        #-----------------------------------------------------#
        # Input Files
        self.w_row_files: WidgetFiles = WidgetFiles(
            self.frame_input, 
            controller=self.controller,
            orientation=Orientation.H,
        )
        self.w_row_files.set_button_sheets()
        self.w_row_files.set_button_clear()

        # Frame com labels para mostrar os arquivos
        self.frame_combo_files = ttk.Frame(self.frame_info_sheets, style=self.controller.appTheme.value)
        self.frame_combo_files.pack(expand=True, fill='both', padx=1, pady=1)
        
        self.lb_info_sheets = ttk.Label(self.frame_combo_files, text='Arquivos e Abas')
        self.lb_info_sheets.pack(expand=True, fill='both', padx=1, pady=1)
        self.lb_files_names = ttk.Label(self.frame_combo_files, text='Arquivo: ')
        self.lb_files_names.pack(padx=1, pady=1, expand=True, fill='both')
        
        self.combobox_files_names: ttk.Combobox = ttk.Combobox(self.frame_combo_files, values=['-'])
        self.combobox_files_names.pack(padx=1, pady=1, expand=True, fill='both')
        self.combobox_files_names.set('-')
        
        # Combobox para mostrar as abas do arquivo.
        self.frame_combo_sheet_names = ttk.Frame(
            self.frame_info_sheets,
            style=self.controller.appTheme.value,
        )
        self.frame_combo_sheet_names.pack(expand=True, fill='both', padx=1, pady=1)

        self.lb_sheet_names = ttk.Label(self.frame_combo_sheet_names, text=' Aba: ')
        self.lb_sheet_names.pack(padx=1, pady=1, expand=True, fill='both')
        self.combobox_sheet_names = ttk.Combobox(self.frame_combo_sheet_names, values=['-'])
        self.combobox_sheet_names.set('-')
        self.combobox_sheet_names.pack(padx=1, pady=1, expand=True, fill='both')
        self.combobox_files_names.bind("<<ComboboxSelected>>", self.update_combobox_sheet_names)
        
        # Combobox para mostar as colunas da aba selecionada
        self.frame_combo_columns = ttk.Frame(self.frame_info_sheets, style=self.controller.appTheme.value)
        self.frame_combo_columns.pack(expand=True, fill='both', padx=1, pady=1)

        self.lb_columns = ttk.Label(self.frame_combo_columns, text='Coluna: ')
        self.lb_columns.pack(padx=1, pady=1, expand=True, fill='both')
        self.combobox_columns = ttk.Combobox(self.frame_combo_columns, values=['-'])
        self.combobox_columns.set('-')
        self.combobox_columns.pack(padx=1, pady=1, expand=True, fill='both')
        self.combobox_columns.bind("<<ComboboxSelected>>", self.update_scrow_col)
        
        # Frame para o botão carregar
        self.frame_buttons_read = ttk.Frame(self.frame_info_sheets)
        self.frame_buttons_read.pack(expand=True, fill='both', padx=1, pady=1)
        self.btn_load_data = ttk.Button(
            self.frame_buttons_read,
            text='Carregar dados',
            command=self.set_current_data_frame,
            style=self.controller.buttonsTheme.value,
        )
        self.btn_load_data.pack(expand=True, fill='both', padx=1, pady=1)
        #-----------------------------------------------------#
        # Container central
        #-----------------------------------------------------#
        # Botões de ação.
        self.frame_lb_info = ttk.Frame(self.frame_buttons)
        self.frame_lb_info.pack(expand=True, fill='both', padx=1, pady=1)

        self.lb_info_actions = ttk.Label(self.frame_lb_info, text='Edição e filtro de dados')
        self.lb_info_actions.pack()
        # Botão para apagar linhas vazias
        self.btn_delet_lines = ttk.Button(
            self.frame_buttons,
            text='Apagar Linhas vazias',
            command=self.action_delet_null_lines,
            style=self.controller.buttonsTheme.value,
            width=18,
        )
        self.btn_delet_lines.pack(side=tk.LEFT, padx=1, pady=1)

        # Botão para filtrar texto
        self.btn_filter_text = ttk.Button(
            self.frame_buttons,
            text='Filtrar Texto',
            command=self.action_filter_text,
            style=self.controller.buttonsTheme.value,
        )
        self.btn_filter_text.pack(side=tk.LEFT, padx=1, pady=1)

        # Botão para apagar a coluna selecionada
        self.btn_delet_column = ttk.Button(
            self.frame_buttons,
            text='Apagar Coluna selecionada',
            width=24,
            command=self.action_delet_current_column,
            style=self.controller.buttonsTheme.value,
        )
        self.btn_delet_column.pack(side=tk.LEFT, padx=1, pady=1)

        # Botão para filtrar texto com arquivo
        self.btn_filter_with_file = ttk.Button(
            self.frame_buttons,
            text='Filtrar Arquivo',
            command=self.action_filter_with_file,
            style=self.controller.buttonsTheme.value,
        )
        self.btn_filter_with_file.pack()
        
        #-----------------------------------------------------#
        # Container filtro de dados
        #-----------------------------------------------------#
        # Frame para o texto a ser filtrado
        self.frame_filter_main = ttk.Frame(self.frame_filter)
        self.frame_filter_main.pack(expand=True, fill='both', padx=2, pady=1)
        self.lb_info_filter = ttk.Label(self.frame_filter_main, text='Filtrar texto ou arquivo')
        self.lb_info_filter.pack()
        
        self.frame_filter_text = ttk.Frame(self.frame_filter, style=self.controller.appTheme.value)
        self.frame_filter_text.pack(side=tk.LEFT, expand=True, fill='both', padx=1, pady=1)
        self.lb_text_filter = ttk.Label(self.frame_filter_text, text='Filtrar texto: ')
        self.lb_text_filter.pack(side=tk.LEFT, expand=True, fill='both', padx=1, pady=1)
        self.text_entry: ttk.Entry = ttk.Entry(self.frame_filter_text)
        self.text_entry.pack(side=tk.LEFT, expand=True, fill='both', padx=1, pady=1)
        
        self.frame_filter_file = ttk.Frame(self.frame_filter, style=self.controller.appTheme.value)
        self.frame_filter_file.pack(side=tk.LEFT, expand=True, fill='both', padx=1, pady=1)
        self.btn_select_sheet_filter = ttk.Button(
                self.frame_filter_file, 
                text='Planilha filtro', 
                command=self.open_file_filter,
            )
        self.btn_select_sheet_filter.pack(side=tk.LEFT, expand=True, fill='both', padx=1, pady=1)
        self.lb_filter_file = ttk.Label(self.frame_filter_file, text='Nenhum arquivo selecionado')
        self.lb_filter_file.pack(side=tk.LEFT, expand=True, fill='both', padx=1, pady=1)
        
        # Concatenar
        self.btn_concat: ttk.Button = ttk.Button(
                self.frame_concat, 
                text='Concatenar', 
                command=self.action_concat_columns,
            )
        self.btn_concat.pack(side=tk.LEFT)
        # combo com 3 colunas
        self.combo_conc_1 = ttk.Combobox(self.frame_concat, values=[''])
        self.combo_conc_1.set('-')
        self.combo_conc_1.pack(side=tk.LEFT)
        
        self.combo_conc_2 = ttk.Combobox(self.frame_concat, values=[''])
        self.combo_conc_2.set('-')
        self.combo_conc_2.pack(side=tk.LEFT)
        
        self.combo_conc_3 = ttk.Combobox(self.frame_concat, values=[''])
        self.combo_conc_3.set('-')
        self.combo_conc_3.pack(side=tk.LEFT)
        
        # Scrow bar
        self.lb_info_scrow = ttk.Label(self.frame_scrow, text='Texto das coluna(s)')
        self.lb_info_scrow.pack(expand=True, fill='both', padx=2, pady=2)
        self.scrow = WidgetScrow(self.frame_scrow, height=5)
        
        # Exportar dados.
        self.frame_lb_export = ttk.Frame(self.frame_export)
        self.frame_lb_export.pack(expand=True, fill='both', padx=1, pady=1)
        self.lb_info_export = ttk.Label(self.frame_lb_export, text='Exportação de dados')
        self.lb_info_export.pack()
        
        self.frame_buttons_export = ttk.Frame(self.frame_export)
        self.frame_buttons_export.pack(expand=True, fill='both', padx=1, pady=1)
        self.checkbox_var = tk.IntVar()
        self.checkbox = ttk.Checkbutton(
                                self.frame_buttons_export,
                                text="Exportar arquivos filtrando itens da coluna atual",
                                variable=self.checkbox_var,
                                command=()
                            )
        self.checkbox.pack()
        self.w_row_export = WidgetRow(self.frame_buttons_export)
        self.w_row_export.add_button('Exportar Dado', self.action_export_current_data)
        self.w_row_export.add_button('Exportar Coluna', self.action_export_current_column)

        self.controller.windowFrames.extend(
            [
                self.frame_export,
                self.frame_scrow,
                self.frame_buttons,
                self.frame_widgets,
            ]
        )
        
    @property
    def topBar(self) -> TopBar:
        return self.controller.topBar

    @property
    def pbar(self) -> ProgressBarAdapter:
        return self.controller.topBar.pbar
        
    def update_theme(self):
        pass
            
    def action_delet_null_lines(self):
        """
            Apaga linhas vazias da coluna selecionada.
        """
        if self.is_running():
            return
        self.thread_main_create(self._run_delet_null_lines)
    
    def _run_delet_null_lines(self):
        if not self.combobox_columns.get() in self.data.columns.tolist():
            messagebox.showerror(
                'Coluna não encontrada',
                f'A coluna {self.combobox_columns.get()} não existe no dado atual!'
            )
            return
        
        self.pbar.start()
        self.pbar.update(0, f'Apagando linhas vazias: {self.combobox_columns.get()}')
        col = self.combobox_columns.get()
        self.data = self.data.dropna(subset=[self.combobox_columns.get()])
        self.data = self.data[self.data[col] != "nan"]
        self.data = self.data[self.data[col] != "None"]
        self.data = self.data[self.data[col] != ""]
        self.pbar.update(100, f'Linhas vazias apagadas: {self.combobox_columns.get()}')
        self.thread_main_stop()
    
    def action_delet_current_column(self):
        self.thread_main_create(self._run_delet_current_column)
    
    def _run_delet_current_column(self):
        current_column = self.combobox_columns.get()
        self.pbar.update(0, f'Apagando coluna {current_column}')
        if not current_column in self.data.columns.tolist():
            messagebox.showerror('Coluna não encontrada', f'A coluna {current_column} não existe no dado atual!')
            return
        self.data = self.data.drop([current_column], axis=1)
        self.update_combobox_columns()
        self.pbar.update(100, f'Coluna apagada: {current_column}')
    
    def action_concat_columns(self):
        self.thread_main_create(self._run_action_concat)
    
    def _run_action_concat(self):
        col1 = self.combo_conc_1.get()
        col2 = self.combo_conc_2.get()
        col3 = self.combo_conc_3.get()
        if not col1 in self.data.columns.tolist():
            messagebox.showwarning('Coluna inválida', f'Verifique a coluna {col1}')
            return
        if not col2 in self.data.columns.tolist():
            messagebox.showwarning('Coluna inválida', f'Verifique a coluna {col2}')
            return
        if not col3 in self.data.columns.tolist():
            messagebox.showwarning('Coluna inválida', f'Verifique a coluna {col3}')
            return
        self.pbar.start()
        self.pbar.update(0, 'Concatenando colunas')
        # Concatena as colunas 'coluna1', 'coluna2' e 'coluna3'
        new_col = f'{col1}_{col2}_{col3}'
        #self.current_data[new_col] = self.current_data[col1] + self.current_data[col2] + self.current_data[col3]
        # Concatena as colunas com um separador (por exemplo, "-")
        self.data[new_col] = self.data[col1].str.cat([self.data[col2], self.data[col3]], sep='_')

        self.update_combobox_columns()
        self.pbar.update(100, 'Colunas concatenadas com sucesso!')
        self.pbar.stop()
        self.thread_main_stop()
    
    def action_export_current_data(self):
        if (self.data is None) or (self.data.empty):
            messagebox.showerror('Dados vazios', 'Clique no botão carregar dados!')
            return
        if not self.combobox_columns.get() in self.data.columns.tolist():
            messagebox.showerror(
                'Coluna inválida', f'A coluna {self.combobox_columns.get()} não existe!'
            )
            return
        
        if self.checkbox_var.get() == 1:
            self.thread_main_create(self._run_export_current_data_multi)
        else:
            self.thread_main_create(self._run_export_current_data)
        
    def _run_export_current_data_multi(self):
        col = self.combobox_columns.get()
        values = self.data[col].drop_duplicates().values.tolist()
        out_dir: Directory = self.controller.controllerFiles.save_dir.concat('Exportado', create=True)
        max_values = len(values)
        self.pbar.start()
        self.scrow.clear()
        for num, item in enumerate(values):
            output_file: File = out_dir.join_file(f'{item}.xlsx')
            prog = (num+1)/(max_values) * (100)
            self.pbar.update(prog, f'Exportando:[{num+1} de {max_values}] {output_file.basename()}')
            self.scrow.update_text(f'Exportando:[{num+1} de {max_values}] {output_file.basename()}')
            try:
                df = self.data[self.data[col] == item]
            except Exception as e:
                print(e)
            else:
                df.to_excel(output_file.absolute(), index=False)
        self.pbar.update(100, 'Operação finalizada!') 
        self.pbar.stop()       
        self.thread_main_stop()
    
    def _run_export_current_data(self):
        output_file: File = self.controller.controllerFiles.save_dir.join_file('output_data.xlsx')
        self.pbar.start()
        self.pbar.update(0, f'Exportando arquivo: {output_file.basename()}')
        self.data.to_excel(output_file.absolute(), index=False)
        self.pbar.update(100, 'OK')
        self.pbar.stop()
        self.thread_main_stop()
    
    def action_export_current_column(self):
        self.thread_main_create(self._run_action_export_current_column)
    
    def _run_action_export_current_column(self):
        current_column = self.combobox_columns.get()
        if not current_column in self.data.columns.tolist():
            messagebox.showerror('Coluna não encontrada', f'A coluna {current_column} não existe no dado atual!')
            return
        output_path: File = self.controller.controllerFiles.save_dir.join_file(f'output-{current_column}.xlsx')
        self.pbar.update(0, f'Exportando coluna {current_column}')
        df = self.data[[current_column]]
        df = df.drop_duplicates()
        df.to_excel(output_path.absolute(), index=False)
        self.pbar.update(100, f'Coluna exportada! {current_column}')
        self.pbar.stop()
        self.thread_main_stop()
        
    def action_filter_text(self):
        self.thread_main_create(self._run_action_filter_text)
    
    def _run_action_filter_text(self):
        current_text: str = self.text_entry.get()
        current_column: str = self.combobox_columns.get()
        if (current_text is None) or (current_text == ""):
            messagebox.showerror('Texto Vazio', 'Adicione textos na caixa de texto!')
            return
        self.pbar.start()
        self.pbar.update(0, f'Filtrando texto: {current_text} na coluna: {current_column}')
        # df = self.data[self.data[col].str.contains(text, case=False, na=False)]
        self.data = self.data[self.data[current_column] == current_text]
        self.pbar.update(100, f'Texto filtrado: {current_text}')
        self.pbar.stop()
        self.thread_main_stop()
    
    def action_filter_with_file(self):
        self.thread_main_create(self._run_action_filter_with_file)

    def _run_action_filter_with_file(self):
        current_col: str = self.combobox_columns.get()
        if not current_col in self.data.columns.tolist():
            messagebox.showerror('Coluna inválida', f'A coluna {current_col} não existe no Dado atual!')
            return
        if (self.file_sheet_filter is None) or (not self.file_sheet_filter.path.exists()):
            messagebox.showinfo('Aviso', 'Planilha de filtros, inválida!')
            return
        
        # Obter a coluna a ser filtrada no arquivo de filtro
        stream = SheetInputStream(self.file_sheet_filter, progress=self.pbar)
        df = stream.read().drop_duplicates()
        if not self.combobox_columns.get() in df.columns.tolist():
            messagebox.showerror('Erro', f'A coluna {self.combobox_columns.get()} não existe na planilha de filtro!')
            return
        values: list[str] = df.astype('str')[self.combobox_columns.get()].values.tolist()
        df_filter = self.data[self.data[self.combobox_columns.get()].isin(values)]
        self.data = df_filter.astype('str')
        
    def open_file_filter(self):
        file: str = self.controller.controllerFiles.fileDialog.open_file_sheet()
        if (file is None) or (file == ''):
            return
        self.file_sheet_filter = File(file)
        self.lb_filter_file.config(text=f'Planilha para filtro: {self.file_sheet_filter.basename()}')
        
    def update_combobox_sheet_names(self, event=None):
        current_file_name: str = self.combobox_files_names.get()
        current_file_dict: dict[FileName, pd.DataFrame] = self.filesnames_data_frame[current_file_name]
        sheet_values: list = list(current_file_dict.keys())
        self.combobox_sheet_names['values'] = sheet_values
        self.combobox_sheet_names.set(sheet_values[0] or '-')
        
    def update_combobox_columns(self):
        if self.data is None:
            current_file = self.combobox_files_names.get()
            if not current_file in self.filenames_paths:
                return
            
            current_file_path: File = self.filenames_paths[current_file]
            current_sheet = self.combobox_sheet_names.get()
            stream = SheetInputStream(
                current_file_path, sheet_name=current_sheet, progress=self.pbar
            )
            self.data = stream.read().astype('str')
            self.filesnames_data_frame[current_file][current_sheet] = self.data
            
        columns = self.data.columns.tolist()        
        self.combobox_columns['values'] = columns
        self.combobox_columns.set(columns[0] or '-')
        self.combo_conc_1['values'] = columns
        self.combo_conc_2['values'] = columns
        self.combo_conc_3['values'] = columns
        
    def update_scrow_col(self, event=None):
        col = self.combobox_columns.get()
        if not col in self.data.columns.tolist():
            return
        values = self.data[col].values.tolist()
        self.scrow.clear()
        for num, item in enumerate(values):
            self.scrow.update_text(f'Coluna {col} index {num} => {item}')
            if num >= 10:
                break
        
    def set_current_data_frame(self):
        """
            Alterar a propriedade que contém o DataFrame atual
        com base no arquivo selecionado na combobox.
        """
        if self.controller.controllerFiles.num_files_sheet == 0:
            messagebox.showinfo('Aviso', 'Adicione planilhas para prosseguir!')
            return
        self.thread_main_create(self._run_set_current_data_frame)
    
    def _run_set_current_data_frame(self):
        current_file_name: str = self.combobox_files_names.get()
        selected_sheet_name: SheetName = self.combobox_sheet_names.get()
        if not current_file_name in self.filenames_paths:
            file_path: File = self.controller.controllerFiles.get_files_sheets()[0]
            selected_sheet_name = None
        else:
            file_path: File = self.filenames_paths[current_file_name]
            
        if len(self.filesnames_data_frame) == 0:
            # Dicionário vazio, necessário carregar do arquivo
            stream = SheetInputStream(
                file_path,
                sheet_name=selected_sheet_name,
                progress=self.pbar
            )
            # Salvar os dados no dicionário, incluíndo o nome do arquivo fonte
            # e a ABA da planilha selecionada pelo usuário.
            self.data = stream.read()
            self.filesnames_data_frame[file_path.basename()][selected_sheet_name] = self.data
            self.filenames_paths[file_path.basename()] = file_path
        elif self.filesnames_data_frame[current_file_name][selected_sheet_name].empty:
            # DataFrame vazio, necessário carregar do arquivo
            file_path: File = self.filenames_paths[current_file_name]
            stream = SheetInputStream(
                file_path,
                sheet_name=selected_sheet_name,
                progress=self.pbar
            )
            self.data = stream.read().astype('str')
            self.filesnames_data_frame[current_file_name][selected_sheet_name] = self.data
        else:
            # o arquivo já foi carregado anteriormente, apenas alterar a propriedade.
            self.data = self.filesnames_data_frame[current_file_name][selected_sheet_name]
        self.update_combobox_columns()
        self.thread_main_stop()
        
    def update_files_sheet_names(self):
        """
            Atualizar os nomes das abas de cada planilha selecionada pelo usuário.
        """
        if self.is_running():
            messagebox.showerror(
                'Atualização de arquivos',
                'Existe outra operação em andamento, aguarde...'
            )
            return
        self.thread_main_create(self._run_update_sheet_names)
    
    def _run_update_sheet_names(self):
        self.pbar.start()
        self.pbar.update(0, f'Atualizando aguarde.')
        files = self.controller.controllerFiles.get_files_sheets()
        maxnum: int = len(files)
        for num, file in enumerate(files):
            self.pbar.update(
                ((num+1)/maxnum) * 100,
                f'Lendo: {file.basename()}'
            )
            
            if not file.basename() in self.filenames_paths:
                # Ler as abas do arquivo atual, e atualizar o combo.
                stream = SheetInputStream(
                    file, progress=self.pbar
                )
                current_sheet_names = stream.get_sheet_names()
                self.filenames_paths[file.basename()] = file
                current_file_values: dict[str, pd.DataFrame] = {}
                for sheet_name in current_sheet_names:
                    # Inicializar um DataFrame vazio para cada aba da planilha.
                    # os valores reais serão carregados apenas quando necessário o uso.
                    current_file_values[sheet_name] = pd.DataFrame()
                self.filesnames_data_frame[file.basename()] = current_file_values
        # Atualizar os combos com nome de arquivo, abas e colunas.
        files_list = list(self.filesnames_data_frame.keys())
        self.combobox_files_names['values'] = files_list
        self.combobox_files_names.set(files_list[0] or '-')
        self.update_combobox_sheet_names()
        self.update_combobox_columns()
        self.pbar.update(100, 'OK')
        self.pbar.stop()
        self.thread_main_stop()

    def receiver_notify_files(self, notify: ControllerNotifyProvider):
        """
            Sempre que esse método for chamado, significa que o usuário
        alterou a seleção de arquivos, limpar ou adicionar. Sendo necessário
        atualizar as propriedades de DataFrame e arquivos.
        """
        if self.controller.controllerFiles.numFiles == 0:
            # O usuário limpou os arquivos
            self.filesnames_data_frame.clear()
            self.filenames_paths.clear()
            self.combobox_columns['values'] = ['-']
            self.combobox_columns.set('-')
            self.combobox_files_names['values'] = ['-']
            self.combobox_files_names.set('-')
            self.combobox_sheet_names['values'] = ['-']
            self.combobox_sheet_names.set('-')
            print('Combos atualizados!')
            return
        self.update_files_sheet_names()
        
    def set_size_screen(self):
        """Redimensionar o tamanho da janela quando esta página for aberta."""
        self.controller.title("Filtra texto em planilhas")
        self.controller.geometry(self.GEOMETRY)

    def update_state(self):
        """
            Carregar algumas informações enquanto a janela é exibida.
        """
        pass


# ========================================================#
# Planilhar Pasta
# ========================================================#
class PageFilesToExcel(UiPage):
    """
        Página para planilhar pasta.
    """

    def __init__(self, *, controller: Controller):
        super().__init__(controller=controller)
        self.controller: Controller = controller
        self.PAGE_ROUTE = '/home/folder_to_excel'
        self.PAGE_NAME = 'Arquivos Para Excel'
        self.GEOMETRY = "300x410"
        self.initUI()
        self.frameWidgets = ttk.Frame(self)
        self.frameWidgets.pack(expand=True, fill='both', padx=1, pady=1)

        self.w_files = WidgetFiles(self.frameWidgets, controller=self.controller, orientation=Orientation.V)
        self.w_files.set_button_image()
        self.w_files.set_button_pdf()
        self.w_files.set_button_sheets()
        self.w_files.set_button_folder()
        self.w_files.set_button_clear()

        self.btn_export = ttk.Button(
            self.frameWidgets,
            text='Exportar Excel',
            command=self.convert_folder_to_excel,
            style=AppThemes.BUTTON_PURPLE_LIGHT.value,
        )
        self.btn_export.pack(padx=1, pady=2)

    @property
    def topBar(self) -> TopBar:
        return self.controller.topBar

    @property
    def pbar(self) -> ProgressBarAdapter:
        return self.topBar.pbar

    def initUI(self):
        pass

    def convert_folder_to_excel(self):
        """
            Planilhar os arquivos selecionados.
        """
        if self.is_running():
            return
        self.thread_main_create(self._operation_convet_folder_to_excel)

    def _operation_convet_folder_to_excel(self):
        """
            -
        """
        self.pbar.start()
        self.pbar.update_text('Exporando planilha!')
        data: pd.DataFrame = self.__get_info_files()
        data.to_excel(self.controller.controllerFiles.save_dir.join_file('Arquivos.xlsx').absolute(), index=False)
        self.topBar.set_text('Planilha exportada!')
        self.pbar.update(100, 'OK')
        self.pbar.stop()
        self.thread_main_stop()

    def __get_info_files(self) -> pd.DataFrame:
        """
            Obter uma lista de com os nomes dos arquivos selecionados pelo usuário.
        """
        files: List[File] = self.controller.controllerFiles.files
        files.sort(key=lambda file: file.absolute().lower())
        self.topBar.pbar.update_text('Obtendo dados')
        data = {
            'NOME': [],
            'ARQUIVO': [],
            'PASTA': [],
            'TIPO': [],
        }
        for f in files:
            data['NOME'].append(f.name())
            data['ARQUIVO'].append(f.absolute())
            data['PASTA'].append(f.dirname()),
            data['TIPO'].append(f.extension())
        return pd.DataFrame.from_dict(data)

    def set_size_screen(self):
        self.controller.geometry(self.GEOMETRY)
        self.controller.title(f"Planilhar Pasta")

    def update_state(self):
        pass


# ========================================================#
# Mover arquivos
# ========================================================#
class PageMoveFiles(UiPage):

    def __init__(self, *, controller: Controller):
        super().__init__(controller=controller)
        self.controller: Controller = controller
        self.controller.controllerFiles.add_observer(self)
        self.PAGE_ROUTE = '/home/page_mv_files'
        self.PAGE_NAME = 'Mover Arquivos'
        self.GEOMETRY = "500x200"
        self.initUI()
        self.frameWidgets = ttk.Frame(self)
        self.frameWidgets.pack(expand=True, fill='both')
        # Frame mover
        self.frameLabels = ttk.Frame(self.frameWidgets)
        self.frameLabels.pack(padx=2, pady=2)
        # Frame botões
        self.frameButtons = ttk.Frame(self.frameWidgets)
        self.frameButtons.pack(padx=1, pady=1)

        #====================================================================#
        # Combo para selecionar a coluna excel que contém os arquivos fonte
        # ====================================================================#
        self.frameColumnFiles = ttk.Frame(self.frameLabels)
        self.frameColumnFiles.pack(side=tk.LEFT)
        # Label
        self.lbColumnFiles = ttk.Label(self.frameColumnFiles, text='Coluna arquivos')
        self.lbColumnFiles.pack()
        # Combo
        self.combo_column_files = ttk.Combobox(
            self.frameColumnFiles,
            values=['-']
        )
        self.combo_column_files.pack(padx=2, pady=2, side=tk.LEFT)
        self.combo_column_files.set('-')

        # ====================================================================#
        # Combo para selecionar a coluna excel com a pasta destino.
        # ====================================================================#
        self.frameColumnDir = ttk.Frame(self.frameLabels)
        self.frameColumnDir.pack()
        # Label
        self.lbColumnDir = ttk.Label(self.frameColumnDir, text='Coluna Pasta de Destino')
        self.lbColumnDir.pack()
        # Combo
        self.combo_column_dir = ttk.Combobox(
            self.frameColumnDir,
            values=['-']
        )
        self.combo_column_dir.pack(padx=2, pady=2, side=tk.LEFT)
        self.combo_column_dir.set('-')

        # ====================================================================#
        # Botão para adicionar planilha.
        # ====================================================================#
        self.btn_add_sheet = ttk.Button(
            self.frameButtons,
            text='Adicionar planilha',
            command=lambda: self.controller.controllerFiles.select_file(LibraryDocs.EXCEL),
            style=AppThemes.BUTTON_GREEN.value,
            width=20,
        )
        self.btn_add_sheet.pack(side=tk.LEFT, padx=1, pady=2)

        # Botão mover
        self.btn_move = ttk.Button(
            self.frameButtons,
            text='Mover',
            command=self.action_move_files,
            style=AppThemes.BUTTON_PURPLE_LIGHT.value,
            width=20,
        )
        self.btn_move.pack(padx=1, pady=2)

        self._main_data: pd.DataFrame = None

    @property
    def mainData(self) -> pd.DataFrame:
        return self._main_data

    @property
    def topBar(self) -> TopBar:
        return self.controller.topBar

    def receiver_notify_files(self, notify: ControllerNotifyProvider):
        th = threading.Thread(target=self._run_update_files)
        th.start()

    def _run_update_files(self):
        self.topBar.set_text('Atualizando DataFrame')
        files = self.controller.controllerFiles.get_files_excel()
        maxnum = len(files)
        if maxnum == 0:
            return
        # Atualizar o label informativo
        file: File = files[0]
        try:
            self._main_data = pd.read_excel(file.absolute())
        except Exception as e:
            print(e)
            messagebox.showwarning('Erro', e)
            return

        self.combo_column_files['values'] = self.mainData.columns.tolist()
        self.combo_column_dir['values'] = self.mainData.columns.tolist()

    def action_move_files(self):
        if self.is_running():
            return
        if self.mainData is None:
            messagebox.showwarning('Erro', 'Selecione uma planilha para prosseguir!')
            return
        if not self.combo_column_files.get() in self.mainData.columns.tolist():
            messagebox.showwarning('Erro', f'Selecione uma coluna válida para os arquivos')
            return
        if not self.combo_column_dir.get() in self.mainData.columns.tolist():
            messagebox.showwarning('Erro', f'Selecione uma coluna válida para o diretório destino')
            return
        self.thread_main_create(self.__execute_move_files)

    def __execute_move_files(self):

        idxs_sheet: List[int] = self.mainData.index.tolist()
        maxnum: int = len(idxs_sheet)
        for n, i in enumerate(idxs_sheet):
            self.topBar.pbar.update(
                ((n+1)/maxnum) * 100,
                f'Movendo: [{n+1} de {maxnum}]'
            )
            item = self.mainData.loc[i]
            f = item[self.combo_column_files.get()]
            out_dir = item[self.combo_column_dir.get()]
            if not os.path.exists(f):
                continue
            # Concatenar o diretório destino com o nome do arquivo atual
            dest: str = os.path.join(out_dir, os.path.basename(f))
            self.move_files(f, dest)

    def move_files(self, src: str, dest: str):
        try:
            shutil.move(src, dest)
        except Exception as e:
            print(e)

    def get_data_move_files(self) -> pd.DataFrame | None:
        """
            Usar o DataFrame da planilha de dados para gerar uma coluna com o nome dos
        arquivos a serem movidos/renomeados
        """
        pass

    def set_size_screen(self):
        self.controller.geometry(self.GEOMETRY)
        self.controller.title(f"Mover arquivos")

    def update_state(self):
        pass
