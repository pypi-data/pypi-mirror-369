#!/usr/bin/env python3
#

from enum import Enum
from tkinter import ttk, Tk


#=================================================================#
# Temas e Estilos
#=================================================================#

class AppThemes(Enum):
    # Tema dos Frames
    DARK = 'Black.TFrame'
    LIGHT = 'LightFrame.TFrame'
    DARK_PURPLE = 'DarkPurple.TFrame'
    LIGHT_PURPLE = 'LightPurple.TFrame'
    GRAY = 'CinzaFrame.TFrame'
    # Tama dos botões
    BUTTON_PURPLE_LIGHT = 'Custom.TButtonPurpleLight'
    BUTTON_GREEN = 'Custom.TButtonGreen'
    # Tema da barra de progresso
    PBAR_GREEN = "Custom.Horizontal.TProgressbar"
    PBAR_PURPLE_LIGHT = "Thin.Horizontal.TProgressbar"
    PBAR_PURPLE = "Purple.Horizontal.TProgressbar"
    

class AppStyles(object):

    def __init__(self, root: Tk):
        self.root = root
        self.rootStyle = ttk.Style(self.root)
        
        self.PADDING_BTN = (6, 8)
        self.WIDTH_BTN = 13

        # ==============================================================#
        # Estilo para os Frames
        # ==============================================================#
        # Defina as cores para o estilo "LightFrame"
        self.styleLight = ttk.Style(self.root)
        self.styleLight.configure(
            "LightFrame.TFrame",
            background="white",
            relief="solid",
            borderwidth=1
        )

        self.styleGray = ttk.Style(self.root)
        self.styleGray.configure(
            "CinzaFrame.TFrame",
            background="lightgray",
            relief="solid",
            borderwidth=1
        )

        self.styleFrameBlack = ttk.Style(self.root)
        self.styleFrameBlack.theme_use("default")
        self.styleFrameBlack.configure(
            "Black.TFrame",
            background="#2C2C2C"
        )  # Cor de fundo preta

        # Fundo Roxo Claro
        self.styleFrameLightPurple = ttk.Style(self.root)
        self.styleFrameLightPurple.theme_use("default")
        self.styleFrameLightPurple.configure(
            "LightPurple.TFrame",  # Nome do estilo alterado
            background="#9370DB"  # Roxo claro (MediumPurple)
        )

        # Fundo Roxo Escuro
        self.styleFrameDarkPurple = ttk.Style(self.root)
        self.styleFrameDarkPurple.theme_use("default")
        self.styleFrameDarkPurple.configure(
            "DarkPurple.TFrame",
            background="#4B0082"  # Roxo escuro
        )

        # Fundo Cinza escuro
        self.styleFrameDarkGray = ttk.Style(self.root)
        self.styleFrameDarkGray.theme_use("default")
        self.styleFrameDarkGray.configure(
            "DarkGray.TFrame",  # Nome do estilo alterado
            background="#2F4F4F"  # Cinza escuro (DarkSlateGray)
        )

        # Laranja escuro
        self.styleFrameDarkOrange = ttk.Style(self.root)
        self.styleFrameDarkOrange.theme_use("default")
        self.styleFrameDarkOrange.configure(
            "DarkOrange.TFrame",  # Nome do estilo alterado
            background="#FF8C00"  # Laranja escuro (DarkOrange)
        )

        # ==============================================================#
        # Estilo para os botões
        # ==============================================================#
        # Roxo Claro
        self.styleButtonPurpleLight = ttk.Style(self.root)
        self.styleButtonPurpleLight.theme_use("default")
        self.styleButtonPurpleLight.layout(
            "Custom.TButtonPurpleLight",
            self.styleButtonPurpleLight.layout("TButton")
        )
        # Define o estilo do botão roxo claro
        self.styleButtonPurpleLight.configure(
            "Custom.TButtonPurpleLight",
            foreground="white",
            background="#B388EB",  # Roxo claro
            borderwidth=1,
            focusthickness=3,
            focuscolor='none',
            anchor='center',
            padding=self.PADDING_BTN,
            width=self.WIDTH_BTN,
        )

        self.styleButtonPurpleLight.map(
            "Custom.TButtonPurpleLight",
            background=[("active", "#a070d6"), ("pressed", "#8b5fc0")]
        )

        # Verde
        self.styleButtonGreen = ttk.Style(self.root)
        self.styleButtonGreen.theme_use("default")
        self.styleButtonGreen.layout(
            "Custom.TButtonGreen",
            self.styleButtonGreen.layout("TButton")
        )
        # Define o estilo do botão verde
        self.styleButtonGreen.configure(
            "Custom.TButtonGreen",
            foreground="white",
            background="#5cb85c",  # Verde
            borderwidth=1,
            focusthickness=3,
            focuscolor='none',
            anchor='center',
            padding=self.PADDING_BTN,
            width=self.WIDTH_BTN,
        )

        self.styleButtonGreen.map(
            "Custom.TButtonGreen",
            background=[("active", "#4cae4c"), ("pressed", "#449d44")]
        )

        #==============================================================#
        # Estilo para Labels
        #==============================================================#
        self.stylePurple = ttk.Style(self.root)
        self.stylePurple.configure(
            "LargeFont.TLabel",  # Nome do estilo
            font=("Helvetica", 14),  # Fonte maior
            background="#9370DB",  # Cor de fundo roxo claro
            foreground="white"  # Cor do texto branco
        )
        # Default
        self.styleDefault = ttk.Style(self.root)
        self.styleDefault.configure(
            "BoldLargeFont.TLabel",  # Nome do estilo
            font=("Helvetica", 14, "bold")  # Fonte maior e negrito
        )
        
        #==============================================================#
        # Estilo para Barra de progresso
        #==============================================================#
        # Verde
        self.pbarGreen = ttk.Style(self.root)
        self.pbarGreen.theme_use('default')
        # Define o novo estilo
        self.pbarGreen.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#f0f0f0',     # cor de fundo da barra
            background='#4CAF50',      # cor da barra de progresso
            thickness=6,                # espessura da barra
            bordercolor='#cccccc',     # borda
            lightcolor='#4CAF50',       # brilho da barra
            darkcolor='#4CAF50',       # sombra da barra
        )
        
        # roxo claro
        self.pbarPurpleLight = ttk.Style(self.root)
        self.pbarPurpleLight.theme_use('default')
        self.pbarPurpleLight.configure("Thin.Horizontal.TProgressbar",
            thickness=6,                         # altura fina
            troughcolor="#eeeeee",             # fundo da barra
            background="#D19FE8"               # roxo claro (pode ajustar)
        )
        
        # roxo escuro
        self.pbarPurple = ttk.Style(self.root)
        self.pbarPurple.theme_use('default')
        self.pbarPurple.configure("Purple.Horizontal.TProgressbar",
            thickness=6,                         # altura fina
            troughcolor="#eeeeee",             # fundo da barra
            background="#4B0081"               # roxo claro (pode ajustar)
        )
        

