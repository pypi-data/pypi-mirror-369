#!/usr/bin/env python3
#
from __future__ import annotations
import re
from typing import (List, Dict)
from pandas import (DataFrame, Series)
from abc import ABC, abstractmethod
import numpy
import shutil

from sheetlib.utils import File, Directory


class ABCParseData(ABC):
    """
        Filtrar, editar e mainipular dados com DataFrame()
    """
    def __init__(self, df:DataFrame):
        if not isinstance(df, DataFrame):
            raise ValueError(f'{__class__.__name__} | data precisa ser do tipo DataFrame() não {type(df)}!')
        
    @abstractmethod
    def get_progress(self) -> float:
        pass

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def header(self) -> List[str]:
        """Retorna a coluna em forma de lista."""
        pass
    
    @abstractmethod
    def exists_column(self, col:str) -> bool:
        pass
    
    @abstractmethod
    def exists_columns(self, cols:List[str]) -> bool:
        pass

    @abstractmethod
    def index_items(self, *, col:str, text:str, iqual=True) -> List[int]:
        pass
        
    @abstractmethod
    def find_elements(self, *, col:str, text:str, iqual:bool=True) -> ImplementParseDataFrame:
        """
            Filtra texto em uma coluna, e retorna todos os elementos filtrados incluíndo
        colunas adjacentes.
        """
        pass
    
    @abstractmethod
    def find_column(self, *, col:str, text:str, iqual:bool=True) -> Series:
        pass
    
    @abstractmethod
    def select_columns(self, columns:List[str]) -> ImplementParseDataFrame | None:
        pass
    
    @abstractmethod
    def add_column(self, *, col:str, values:List[str]) -> None:
        pass

    @abstractmethod
    def uniq_column(self, col:str) -> Series:
        pass

    @abstractmethod    
    def remove_null(self, *, col:str) -> None:
        """
            Remove valores nulos de uma coluna
        """
        pass

    @abstractmethod
    def remove_lines(self, *, col:str, text:str, iqual:bool=True) -> None:
        pass
    
    @abstractmethod
    def delet_columns(self, columns:List[str]) -> None:
        pass
    
    @abstractmethod
    def concat_columns(self, *, columns:List[str], new_col:str=None, sep_cols:str='_') -> None:
        pass


class ImplementParseDataFrame(ABCParseData):
    """
        Filtrar, editar e mainipular dados com DataFrame()
    """
    def __init__(self, df):
        super().__init__(df)
        if df.empty:
            self._current_df = df
        else:
            self._current_df = df.astype('str')
        self.length = len(self._current_df)
        self._prog:float = 0
        self._text:str = '-'
        self.current_action:str = '-'

    @property
    def data(self) -> DataFrame:
        return self._current_df
    
    @data.setter
    def data(self, new):
        if not isinstance(new, DataFrame):
            return
        self._current_df = new.astype('str')
        self.length = len(self._current_df)
     
    def get_progress(self):
        return self._prog
    
    def get_text(self):
        return self._text

    def header(self) -> List[str]:
        """Retorna a coluna em forma de lista."""
        return self.data.columns.tolist()
    
    def exists_column(self, col:str) -> bool:
        return col in self.header()
    
    def exists_columns(self, cols:List[str]) -> bool:
        _status = True
        for c in cols:
            if not self.exists_column(c):
                _status = False
                break
        return _status

    def index_items(self, *, col:str, text:str, iqual=True) -> List[int]:
        if not self.exists_column(col):
            return []
        if iqual == False:
            return self.data[self.data[col].str.contains(text, case=False, na=False)].index.tolist()
        s: Series = self.data[col]
        return s[s == text].index.tolist()
        
    def find_elements(self, *, col:str, text:str, iqual:bool=True) -> ImplementParseDataFrame:
        """
            Filtra texto em uma coluna, e retorna todos os elementos filtrados incluíndo
        colunas adjacentes.
        """
        print(f'[FILTRANDO TEXTO] Coluna: {col} | Texto: {text}')
        if not self.exists_column(col):
            return ImplementParseDataFrame(DataFrame())
        #
        if iqual == True:
            df = self.data[self.data[col] == text]
        else:
            df = self.data[self.data[col].str.contains(text, case=False, na=False)]
        #
        if df.empty:
            return ImplementParseDataFrame(DataFrame())
        #
        #return ParseData(self.data.iloc[list_index])
        return ImplementParseDataFrame(df)
    
    def find_column(self, *, col:str, text:str, iqual:bool=True) -> Series:
        if not self.exists_column(col):
            return Series()
        #
        if iqual == True:
            df = self.data[self.data[col] == text]
        else:
            df = self.data[self.data[col].str.contains(text, case=False, na=False)]
        #
        if df.empty:
            return Series()
        return df[col]
    
    def select_columns(self, columns:List[str]) -> ImplementParseDataFrame | None:
        if not self.exists_columns(columns):
            return None
        return ImplementParseDataFrame(self.data[columns])
    
    def add_column(self, *, col:str, values:List[str]) -> None:
        if self.exists_column(col):
            print(f'{__class__.__name__} [FALHA] a coluna {col} já existe no DataFrame()!')
            return
        # Preenchendo com NaN para ajustar o tamanho
        num_values:int = len(values)
        num_data:int = self.length
        if num_values == num_data:
            new_column = values
        elif num_values < num_data:
            new_column = values + [numpy.nan] * (num_data - num_values)
        elif num_values > num_data:
            new_column = values[0:num_data]
        self.data[col] = new_column
        
    def uniq_column(self, col:str) -> Series:
        return self.data[col].drop_duplicates()
        
    def remove_null(self, *, col:str) -> None:
        """
            Remove valores nulos de uma coluna
        """
        print(f'[APAGANDO LINHAS VAZIAS] Coluna: {col}')
        if not self.exists_column(col):
            return
        self.data = self.data.dropna(subset=[col])
        self.data = self.data[self.data[col] != "nan"]
        self.data = self.data[self.data[col] != "None"]
        self.data = self.data[self.data[col] != ""]

    def remove_lines(self, *, col:str, text:str, iqual:bool=True) -> None:
        # _df = df[~df['coluna'].str.contains(pattern)]
        if not self.exists_column(col):
            return
        #
        if iqual == True:
            self.data = self.data[self.data[col] != text]
        else:
            pattern = re.compile(r'{}'.format(text))
            self.data = self.data[~self.data[col].str.contains(pattern)]
    
    def delet_columns(self, columns:List[str]) -> None:
        if not self.exists_columns(columns):
            return None
        self.data = self.data.drop(columns, axis=1)
        
    def concat_columns(self, *, columns:List[str], new_col:str=None, sep_cols:str = '_'):
        """Concatena colunas no DataFrame Original"""
        # df['nova_coluna'] = df['col1'].astype(str) + '_' + df['col2'].astype(str) + '_' + df['col3'].astype(str)

        if not self.exists_columns(columns):
            print(f'As colunas não existem: {columns}')
            return None
        
        # Criar uma lista vazia para armazenar os valores concatenados
        column_concat = []
        iter_rows = self.data.iterrows()
        for idx, row in iter_rows:
            # Concatenar os valores das colunas selecionadas
            value_concat = sep_cols.join([str(row[col]) for col in columns])
            column_concat.append(value_concat)
        # Adicionar a nova coluna ao DataFrame
        if new_col is None:
            new_col = sep_cols.join(columns)
        self.data[new_col] = column_concat

#
class ParseDF(object):
    """FACADE"""
    def __init__(self, df):
        self._parseDataFrame:ImplementParseDataFrame = ImplementParseDataFrame(df)
        
    @property
    def data(self) -> DataFrame:
        return self._parseDataFrame.data
    
    @data.setter
    def data(self, new:DataFrame):
        if not isinstance(new, DataFrame):
            return
        if new.empty:
            return
        self._parseDataFrame = ImplementParseDataFrame(new)
        
    def get_progress(self) -> float:
        return self._parseDataFrame.get_progress()

    def get_text(self) -> str:
        return self._parseDataFrame.get_text()

    def header(self) -> List[str]:
        return self._parseDataFrame.header()
    
    def exists_column(self, col:str) -> bool:
        return self._parseDataFrame.exists_column(col)
    
    def exists_columns(self, cols:List[str]) -> bool:
        return self._parseDataFrame.exists_columns(cols)

    def index_items(self, *, col:str, text:str, iqual=True) -> List[int]:
        return self._parseDataFrame.index_items(col=col, text=text, iqual=iqual)
        
    def find_elements(self, *, col:str, text:str, iqual:bool=True) -> ParseDF:
        return ParseDF(self._parseDataFrame.find_elements(col=col, text=text, iqual=iqual).data)
    
    def find_column(self, *, col:str, text:str, iqual:bool=True) -> Series:
        return self._parseDataFrame.find_column(col=col, text=text,iqual=iqual)
    
    def select_columns(self, columns:List[str]) -> ParseDF | None:
        _parse = self._parseDataFrame.select_columns(columns)
        return None if _parse is None else ParseDF(_parse.data)
    
    def add_column(self, *, col:str, values:List[str]) -> None:
        return self._parseDataFrame.add_column(col=col, values=values)

    def uniq_column(self, col:str) -> Series:
        return self._parseDataFrame.uniq_column(col)
    
    def remove_null(self, *, col:str) -> None:
        return self._parseDataFrame.remove_null(col=col)

    def remove_lines(self, *, col:str, text:str, iqual:bool=True) -> None:
        return self._parseDataFrame.remove_lines(col=col, text=text, iqual=iqual)
    
    def delet_columns(self, columns:List[str]) -> None:
        return self._parseDataFrame.delet_columns(columns)
    
    def concat_columns(self, *, columns, new_col = None, sep_cols = '_'):
        return self._parseDataFrame.concat_columns(columns=columns, new_col=new_col, sep_cols=sep_cols)



     
class DataString(object):
    def __init__(self, value:str):
        self.value = value
        
    def is_null(self) -> bool:
        if (self.value is None) or (self.value == ''):
            return True
        return False

    def to_utf8(self) -> DataString:
        items_for_remove = [
                        '\xa0T\x04',
                    ]
        try:
            for i in items_for_remove:
                REG = re.compile(i)
                self.value = REG.sub("_", self.value)
        except:
            return self
        else:
            self.value = self.value.encode("utf-8", errors="replace").decode("utf-8")
        return self
    
    def to_upper(self) -> DataString:
        self.value = self.value.upper()
        return self
    
    def to_list(self, separator:str=' ') -> List[str]:
        """
            Transforma uma string em uma lista de strings.
        """
        try:
            return self.value.split(separator)
        except Exception as e:
            print(e)
            return []

    def replace_all(self, char:str, new_char:str='_') -> DataString:
        """
            Usar expressão regular para substituir caracteres.
        """
        # re.sub(r'{}'.format(char), new_char, text)
        self.value = re.sub(re.escape(char), new_char, self.value)
        return self

    def replace_bad_chars(self, *, new_char='-') -> DataString:
        char_for_remove = [
                            ':', ',', ';', '$', '=', 
                            '!', '}', '{', '(', ')', 
                            '|', '\\', '‘', '*'
                            '¢', '“', '\'', '¢', '"', 
                            '#', '<', '?', '>', 
                            '»', '@', '+', '[', ']',
                            '%', '%', '~', '¥', '«',
                            '°', '¢', '”', '&'
                ]

        for char in char_for_remove:
            self.replace_all(char, new_char)
        format_chars = [
            '-_', '_-', '--', '__',
        ]
        for c in format_chars:
            self.replace_all(c)
        return self
    


class MoveFiles(object):
    """
        Mover arquivos a partir dos dados de um DataFrame()
    o DataFrame() base deve ter as seguintes colunas:
    
    ARQUIVO: Sendo o caminho absoluto do arquivo fonte(src) a ser movido
    NOVO_ARQUIVO: Sendo o nome relativo do novo arquivo ao mover (dest)
    
    """
    def __init__(self, df:DataFrame, *, col_src:str, col_new_name:str):
        #self.df:DataFrame = df
        self.col_src:str = col_src
        self.col_new_name:str = col_new_name
        self.sucess_num:int = 0
        self.error_num:int = 0
        self.max_num:int = 0
        if not isinstance(df, DataFrame):
            raise ValueError(f'{__class__.__name__}Erro use DataFrame(), não {type(df)}')
        
        self.parse:ParseDF = ParseDF(df)
        if not self.parse.exists_column(self.col_src):
            raise ValueError(f'{__class__.__name__}\n A coluna fonte não existe: {self.col_src}')
        if not self.parse.exists_column(self.col_new_name):
            raise ValueError(f'{__class__.__name__}\n A coluna arquivo destino não existe: {self.col_new_name}')
        self.parse.data = self.parse.data.drop_duplicates(subset=[self.col_new_name])
        
    def __get_formated_data(self) -> DataFrame | None:
        if not self.parse.exists_columns([self.col_new_name, self.col_src]):
            raise ValueError(f'{__class__.__name__} Colunas iválidas.')
        df = self.parse.select_columns([self.col_src, self.col_new_name]).data
        return None if (df is None) or (df.empty) else df
    
    def move_to(self, output_dir:Directory):
        if not isinstance(output_dir, Directory):
            raise ValueError(f'{__class__.__name__} User Directory, não {type(output_dir)}')
        output_dir.mkdir()
        current_df = self.__get_formated_data()
        if current_df is None:
            return
        listnum = current_df.index.tolist()
        self.max_num = len(listnum)
        for num_line in listnum:
            src_file:File = File(current_df[self.col_src].values.tolist()[num_line])
            print('=' * 80)
            print(src_file.absolute())
            if not src_file.path.exists():
                continue
            try:
                # Remover aqui os caracteres inválidos para nomes de arquivos.
                fmt:DataString = DataString(current_df[self.col_new_name].values.tolist()[num_line])
                fmt.replace_bad_chars().replace_all('/', '_')
                #          Pasta Pai               Nome       Extensão .pdf, .png etc.
                out:File = output_dir.join_file(f'{fmt.value}{src_file.extension()}')
                print(f'Movendo: {out.absolute()}')
                self.move_file(src_file, out)
            except Exception as e:
                print(e)
                self.error_num += 1
            else:
                print(f'Movido: {out.basename()}')
                self.sucess_num += 1
    
    def move_file(self, src:File, dest:File) -> bool:
        if not isinstance(src, File):
            print(f'{__class__.__name__} Erro: use File(), não {type(src)} - PULANDO')
            return False
        if not isinstance(dest, File):
            print(f'{__class__.__name__} Erro: use File(), não {type(dest)} - PULANDO')
            return False
        if dest.path.exists():
            print(f'[PULANDO]: o arquivo já existe {dest.basename()}')
            return False
        shutil.move(src.absolute(), dest.absolute())
        return True