#!/usr/bin/env python3
#
from __future__ import annotations
from typing import (List, Tuple, Dict, LiteralString)
import utm

import pandas
from pandas import DataFrame


class LatLongPoint(object):
    """
        Representação de um par de coordenadas latitude e longitude.
    """
    def __init__(self, lat:float, long:float, name='ROTA'):
        self.lat:float = float(lat)
        self.long:float = float(long)
        self.name:str = name

    def to_tuple(self) -> Tuple[float, float]:
        """Retorna o par de coordenadas em forma de tupla."""
        return (self.lat, self.long)
    
    def to_string(self) -> str:
        """Conerter o par de coordenadas em string"""
        lat = str(self.lat).replace(',', '.')
        long = str(self.long).replace(',', '.')
        return f'{lat}, {long}'
    
    def to_utm_point(self, *, zone:int, latter:str) -> UtmPoint | None:
        """Converter em coordenadas UTM"""
        try:
            _east=utm.from_latlon(self.lat, self.long)[0] 
            _north=utm.from_latlon(self.lat, self.long)[1]
        except Exception as e:
            print(f'\n{__class__.__name__}\n{e}')
            return None
        else:
            return UtmPoint(
                    east=_east, 
                    north=_north, 
                    zone=zone, 
                    letter=latter
                )


class UtmPoint(object):
    """
        Objeto que representa uma coordenada UTM.
    """
    def __init__(self, *, east:float, north:float, zone:int=20, letter:str='K'):
        
        self.east:float = float(east)
        self.north:float = float(north)
        self.zone:int = int(zone)
        self.letter:str = letter # hemisphere

        if (self.north < 0) or (self.north > 10000000):
            raise ValueError(f'{__class__.__name__} o valor de north deve estar entre 0 e 10000000. Recebido: {self.north}')
        if (self.east < 100000) or (self.east > 999999):
            raise ValueError(f'{__class__.__name__} o valor de east deve estar entre 100 e 999999. Recebido: {self.east}')

    def to_latlong(self) -> LatLongPoint | None:
        """Converte a coordenada atual para latitude longitude."""
        # Conversão de UTM para Latitude/Longitude
        try:
            lat, long = utm.to_latlon(self.east, self.north, self.zone, self.letter)
        except Exception as e:
            print(f'{__class__.__name__} -> {e} [East: {self.east} - North: {self.north}]')
            return None
        else:
            return LatLongPoint(lat, long)
        

#======================================================================#
# Conversão de vários pontos de coordenadas
#======================================================================#
class ConvertPoints(object):
    def __init__(self):
        self.__prog:float = 0
        self.__running = False
        
    def is_running(self) -> bool:
        return self.__running
        
    def get_progress(self) -> float:
        return self.__prog

    def from_lat_lon_points(self, *, points:List[LatLongPoint], zone:int, latter:str) -> List[UtmPoint]:
        utm_points = []
        for latlong in points:
            p = latlong.to_utm_point(zone=zone, latter=latter)
            if p is not None:
                utm_points.append(p)
        return utm_points

    def from_utm_points(self, points:List[UtmPoint]) -> List[LatLongPoint]:
        """
            Recebe uma lista de pontos UTM e retorna uma lista de pontos latitude longitude.
        """
        latlon_points:List[LatLongPoint] = []
        for utm_point in points:
            try:
                p = utm_point.to_latlong()
            except:
                continue
            else:
                if p is not None:
                    latlon_points.append(p)
        return latlon_points
    
    def from_data_utm(
            self, *,
            data:DataFrame, 
            column_east:str, 
            column_north:str, 
            zone:int=20, 
            letter:str='K',
        ) -> DataFrame:
        """
            Recebe um DataFrame contendo coordenadas UTM e
        retorna um novo DataFrame() inserindo as coordenadas
        Latitude/Longitude.
        """
        #
        # Apagar linhas vazias nas colunas de coordenadas.
        #data = data.dropna(subset=[column_east, column_north])
        if data.empty:
            return data
        data = data.astype('str')
        
        if not column_east in data.columns.tolist():
            return data
        if not column_north in data.columns.tolist():
            return data
        
        # posição da coluna com valores EASTING.
        index_esting:int = data.columns.tolist().index(column_east)
        # posição da coluna com valores NORTHING.
        index_nort:int = data.columns.tolist().index(column_north)
        
        new_column_lat = []
        new_column_long = []
        new_column_latlong_str = []
        
        for num, value in enumerate(data.values):
            #
            #
            
            try:
                current_utm_point = UtmPoint(
                east=value[index_esting][0:6] if len(value[index_esting]) > 6 else value[index_esting], 
                north=value[index_nort][0:7] if len(value[index_nort]) > 7 else value[index_nort], 
                zone=zone, 
                letter=letter,
                )
            except Exception as e:
                print(f'{__class__.__name__} | [PULANDO] NUM {num} |{value[index_esting]} - {e}')
                new_column_lat.append('nan')
                new_column_long.append('nan')
                new_column_latlong_str.append('nan')
            else:
                _latlon = current_utm_point.to_latlong()
                if _latlon is None:
                    new_column_lat.append('nan')
                    new_column_long.append('nan')
                    new_column_latlong_str.append('nan')
                else:
                    new_column_lat.append(_latlon.to_tuple()[0])
                    new_column_long.append(_latlon.to_tuple()[1])
                    new_column_latlong_str.append(_latlon.to_string())
        
        data['LATITUDE'] = new_column_lat
        data['LONGITUDE'] = new_column_long
        data['LAT-LONG'] = new_column_latlong_str
        #
        #
        #data = data[data['LATITUDE'] != '']  # Remover strings vazias
        #data = data.dropna(subset=['LATITUDE'])  # Remover valores nulos 
        return data

   
#======================================================================#
class RouteLatLon(object):
    """
        Representação de uma rota com vários pares de coordenada LATITUDE/LONGITUDE.
    """
    def __init__(self, points:List[LatLongPoint]):
        self.points:List[LatLongPoint] = points
        self.num_points:int = len(self.points)

    def add_point(self, p:LatLongPoint):
        if not isinstance(p, LatLongPoint):
            print(f'{__class__.__name__}\n{p} não é válido.')
            return
        self.points.append(p)

    def first(self) -> LatLongPoint:
        return self.points[0]

    def last(self) -> LatLongPoint:
        return self.points[-1]

    def is_empty(self) -> bool:
        return True if self.num_points == 0 else False
    
    def get_point(self, p:int) -> LatLongPoint:
        return self.points[p]

#======================================================================#
'''
class CreateMap(object):
    """
        Recebe um obejto RouteLatLon e pode 
    gerar um mapa ou um arquivo HTML de mapa com os dados do objeto RouteLatLon.
    """
    def __init__(self, route:RouteLatLon):
        self.route:RouteLatLon = route
        
    def is_empty(self) -> bool:
        return self.route.is_empty()
    
    def get_map_from_route(self) -> folium.Map | None:
        """
            Gera um objeto mapa de pontos.
        """
        if not isinstance(self.route, RouteLatLon):
            print(f'{__class__.__name__}\n{self.route} não é válido.')
            return None
        if self.route.is_empty():
            return None
        
        map:folium.Map = folium.Map(
                location=[
                    self.route.first().lat, 
                    self.route.first().long,
                ], 
                zoom_start=15
            )

        # Adiciona um marcador no ponto
        if self.route.num_points > 1:
            
            for num in range(1, self.route.num_points):
                folium.Marker(
                    [self.route.get_point(num).lat, self.route.get_point(num).long], 
                    popup=f"Lat: {self.route.get_point(num).lat} | Lon: {self.route.get_point(num).long} | {self.route.get_point(num).name}"
                ).add_to(map)
        else:
            folium.Marker(
                [self.route.first().lat, self.route.first().long], 
                popup=f"Lat: {self.route.first().lat} | Lon: {self.route.first().long} | {self.route.first().name}"
            ).add_to(map)
        #
        return map

    def to_html(self, file:str) -> None:
        """
            Salva um objeto mapa de pontos em um arquivo HTML.
        """
        if not isinstance(file, str):
            raise ValueError(f'{__class__.__name__}\n{file} não é um arquivo válido')
        #
        # Cria um mapa centrado no ponto convertido
        _map:folium.Map = self.get_map_from_route()
        # Salva o mapa em um arquivo HTML
        _map.save(file)
        print(f'Mapa salvo em {file}')
'''

#======================================================================#

def get_utm(*, lat:float, lon:float) -> UtmPoint:
    """
        Recebe um par de coordenadas Latitude/Longitude e retorna um objeto UtmPoint() com as coordenadas UTM.
    """
    # Tuple[float, float, int, object]
    _utm = utm.from_latlon(lat, lon)
    return UtmPoint(
                east=_utm[0], 
                north=_utm[1], 
                zone=_utm[2], 
                letter=_utm[3]
            )

def get_data_latlong(
        file:str, 
        col_lat='vlr_coordenada_latitude', 
        col_long='vlr_coordenada_longitude'
        ) -> DataFrame:
    
    df = pandas.read_excel(file)
    df = df[[col_lat, col_long]]
    return df




#======================================================================#
'''
def create_map(rota:Rota, outfile:str):
    if rota.is_empty():
        raise ValueError('Rota Vazia')
    
    # Cria um mapa centrado no ponto convertido
    map = folium.Map(
            location=[
                rota.first()[0], 
                rota.first()[1]
            ], 
            zoom_start=12
        )

    # Adiciona um marcador no ponto
    # folium.Marker([lat, lon], popup=f"Lat: {lat}, Lon: {lon}").add_to(mapa)
    if rota.max_pontos > 1:
        for num in range(1, rota.max_pontos):
            folium.Marker(
                [rota.get_point(num)[0], rota.get_point(num)[1]], 
                popup=f"Lat: {rota.get_point(num)[0]} | Lon: {rota.get_point(num)[1]}"
                ).add_to(map)
    else:
        folium.Marker(
            [rota.first()[0], rota.first()[1]], 
            popup=f"Lat: {rota.first()[0]} | Lon: {rota.first()[1]}"
            ).add_to(map)


    # Salva o mapa em um arquivo HTML
    map.save(outfile)
    print(f'Mapa salvo em {outfile}')
'''

#======================================================================#

'''
def create_map_from_df(data:DataFrame, outfile:str):
    values = list(data.itertuples(index=False, name=None))
    rota = Rota(values)
    create_map(rota, outfile)
    return
    if KERNEL_TYPE == 'Linux':
        os.system(f'xdg-open {outfile}')
    elif KERNEL_TYPE == 'Windows':
        # chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        # subprocess.run([chrome_path, outfile])
        os.startfile(outfile)
'''


    
