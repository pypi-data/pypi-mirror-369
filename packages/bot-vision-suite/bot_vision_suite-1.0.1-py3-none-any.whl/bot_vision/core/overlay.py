"""
Bot Vision Suite - Visual Overlay

Este módulo gerencia a exibição de overlays visuais para destacar regiões na tela.
"""

import tkinter as tk
import threading
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class VisualOverlay:
    """
    Classe para criar overlays visuais na tela.
    
    Permite destacar regiões específicas da tela com retângulos coloridos,
    útil para debug e feedback visual durante a automação.
    """
    
    def __init__(self, color: str = "red", width: int = 4, duration: int = 1000):
        """
        Inicializa o overlay.
        
        Args:
            color (str): Cor do overlay (red, blue, green, etc.)
            width (int): Largura da linha do retângulo
            duration (int): Duração em milissegundos
        """
        self.color = color
        self.width = width
        self.duration = duration
        self._root = None
    
    def show(self, region: Tuple[int, int, int, int], blocking: bool = False) -> None:
        """
        Exibe o overlay na região especificada.
        
        Args:
            region (tuple): (x, y, width, height) da região a destacar
            blocking (bool): Se True, bloqueia até o overlay desaparecer
        """
        if blocking:
            self._create_overlay(region)
        else:
            thread = threading.Thread(target=self._create_overlay, args=(region,))
            thread.daemon = True
            thread.start()
    
    def _create_overlay(self, region: Tuple[int, int, int, int]) -> None:
        """
        Cria e exibe o overlay.
        
        Args:
            region (tuple): (x, y, width, height) da região
        """
        try:
            x, y, w, h = region
            
            # Cria janela transparente
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.config(bg='black')
            root.attributes('-transparentcolor', 'black')
            
            # Define tamanho da tela
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.geometry(f"{screen_width}x{screen_height}+0+0")
            
            # Cria canvas e desenha retângulo
            canvas = tk.Canvas(
                root, 
                width=screen_width, 
                height=screen_height, 
                bg='black', 
                highlightthickness=0
            )
            canvas.pack()
            
            # Desenha o retângulo destacando a região
            canvas.create_rectangle(
                x, y, x + w, y + h, 
                outline=self.color, 
                width=self.width
            )
            
            # Agenda destruição da janela
            root.after(self.duration, root.destroy)
            
            # Inicia loop principal
            root.mainloop()
            
        except Exception as e:
            logger.error(f"Erro ao criar overlay: {e}")
    
    def show_multiple(self, regions: list, blocking: bool = False) -> None:
        """
        Exibe múltiplos overlays simultaneamente.
        
        Args:
            regions (list): Lista de tuplas (x, y, width, height)
            blocking (bool): Se True, bloqueia até todos os overlays desaparecerem
        """
        if blocking:
            self._create_multiple_overlays(regions)
        else:
            thread = threading.Thread(target=self._create_multiple_overlays, args=(regions,))
            thread.daemon = True
            thread.start()
    
    def _create_multiple_overlays(self, regions: list) -> None:
        """
        Cria múltiplos overlays.
        
        Args:
            regions (list): Lista de regiões
        """
        try:
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.config(bg='black')
            root.attributes('-transparentcolor', 'black')
            
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.geometry(f"{screen_width}x{screen_height}+0+0")
            
            canvas = tk.Canvas(
                root, 
                width=screen_width, 
                height=screen_height, 
                bg='black', 
                highlightthickness=0
            )
            canvas.pack()
            
            # Desenha todos os retângulos
            for region in regions:
                x, y, w, h = region
                canvas.create_rectangle(
                    x, y, x + w, y + h, 
                    outline=self.color, 
                    width=self.width
                )
            
            root.after(self.duration, root.destroy)
            root.mainloop()
            
        except Exception as e:
            logger.error(f"Erro ao criar múltiplos overlays: {e}")


def show_overlay(region: Tuple[int, int, int, int], duration: int = 1000, 
                color: str = "red", width: int = 4) -> None:
    """
    Função de conveniência para exibir um overlay rapidamente.
    
    Args:
        region (tuple): (x, y, width, height) da região a destacar
        duration (int): Duração em milissegundos
        color (str): Cor do overlay
        width (int): Largura da linha
    
    Examples:
        >>> show_overlay((100, 100, 200, 50), duration=2000, color="blue")
    """
    overlay = VisualOverlay(color=color, width=width, duration=duration)
    overlay.show(region, blocking=False)


def show_overlay_blocking(region: Tuple[int, int, int, int], duration: int = 1000,
                         color: str = "red", width: int = 4) -> None:
    """
    Função de conveniência para exibir um overlay de forma bloqueante.
    
    Args:
        region (tuple): (x, y, width, height) da região a destacar
        duration (int): Duração em milissegundos
        color (str): Cor do overlay
        width (int): Largura da linha
    """
    overlay = VisualOverlay(color=color, width=width, duration=duration)
    overlay.show(region, blocking=True)


def show_multiple_overlays(regions: list, duration: int = 1000,
                          color: str = "red", width: int = 4) -> None:
    """
    Função de conveniência para exibir múltiplos overlays.
    
    Args:
        regions (list): Lista de tuplas (x, y, width, height)
        duration (int): Duração em milissegundos
        color (str): Cor do overlay
        width (int): Largura da linha
    
    Examples:
        >>> regions = [(100, 100, 200, 50), (300, 200, 150, 30)]
        >>> show_multiple_overlays(regions, duration=2000, color="green")
    """
    overlay = VisualOverlay(color=color, width=width, duration=duration)
    overlay.show_multiple(regions, blocking=False)
