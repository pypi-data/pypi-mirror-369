"""
Bot Vision Suite - Visual Overlay

Este módulo gerencia a exibição de overlays visuais para destacar regiões na tela.
"""

import tkinter as tk
import threading
import logging
import os
import sys
from typing import Tuple

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
        self._tkinter_available = self._check_tkinter_availability()
    
    def _check_tkinter_availability(self) -> bool:
        """
        Verifica se o Tkinter está disponível e funcionando.
        
        Returns:
            bool: True se Tkinter estiver funcionando
        """
        try:
            # Teste simples de criação de janela
            test_root = tk.Tk()
            test_root.withdraw()  # Esconde a janela
            test_root.destroy()
            return True
        except Exception as e:
            logger.debug(f"Tkinter não disponível: {e}")
            return False
    
    def _fix_tkinter_environment(self) -> bool:
        """
        Tenta corrigir problemas comuns do Tkinter de forma dinâmica.
        
        Returns:
            bool: True se conseguiu corrigir
        """
        try:
            import glob
            import platform
            
            # Método 1: Detectar automaticamente TCL/TK
            python_path = sys.executable
            python_dir = os.path.dirname(python_path)
            
            # Buscar versões do TCL dinamicamente
            tcl_search_patterns = []
            
            # Para qualquer ambiente Python (venv, conda, sistema)
            base_dirs = [
                python_dir,  # Diretório do executável Python
                os.path.dirname(python_dir),  # Diretório pai
                os.path.join(python_dir, '..'),  # Relativo
            ]
            
            # Adicionar locais específicos do sistema se existirem
            if platform.system() == "Windows":
                # Detectar instalações padrão do Windows
                program_files = [
                    os.environ.get('PROGRAMFILES', r'C:\Program Files'),
                    os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)'),
                ]
                
                for pf in program_files:
                    if pf and os.path.exists(pf):
                        # Buscar qualquer versão do Python
                        python_installs = glob.glob(os.path.join(pf, 'Python*'))
                        base_dirs.extend(python_installs)
            
            # Padrões de busca para TCL
            for base_dir in base_dirs:
                if not base_dir or not os.path.exists(base_dir):
                    continue
                    
                # Buscar TCL em vários locais possíveis
                tcl_patterns = [
                    os.path.join(base_dir, 'tcl*'),
                    os.path.join(base_dir, 'lib', 'tcl*'),
                    os.path.join(base_dir, 'Scripts', 'tcl*'),
                    os.path.join(base_dir, 'Lib', 'tcl*'),
                    os.path.join(base_dir, 'share', 'tcl*'),
                    os.path.join(base_dir, 'Library', 'lib', 'tcl*'),  # Conda
                ]
                
                tcl_search_patterns.extend(tcl_patterns)
            
            # Buscar TCL usando os padrões
            tcl_paths = []
            for pattern in tcl_search_patterns:
                matches = glob.glob(pattern)
                tcl_paths.extend([m for m in matches if os.path.isdir(m)])
            
            # Remover duplicatas e ordenar (versões mais recentes primeiro)
            tcl_paths = sorted(list(set(tcl_paths)), reverse=True)
            
            logger.debug(f"Encontrados {len(tcl_paths)} possíveis caminhos TCL")
            
            # Testar cada caminho TCL encontrado
            for tcl_path in tcl_paths:
                try:
                    os.environ['TCL_LIBRARY'] = tcl_path
                    
                    # Buscar TK correspondente
                    tk_path = tcl_path.replace('tcl', 'tk')
                    if not os.path.exists(tk_path):
                        # Tentar outros padrões para TK
                        tk_dir = os.path.dirname(tcl_path)
                        tk_patterns = [
                            os.path.join(tk_dir, 'tk*'),
                            tcl_path.replace('tcl', 'tk'),
                        ]
                        for tk_pattern in tk_patterns:
                            tk_matches = glob.glob(tk_pattern)
                            if tk_matches:
                                tk_path = tk_matches[0]
                                break
                    
                    if os.path.exists(tk_path):
                        os.environ['TK_LIBRARY'] = tk_path
                    
                    # Testa se funcionou
                    if self._check_tkinter_availability():
                        logger.info(f"✅ Tkinter corrigido - TCL: {tcl_path}")
                        if 'TK_LIBRARY' in os.environ:
                            logger.info(f"✅ TK: {os.environ['TK_LIBRARY']}")
                        return True
                        
                except Exception as e:
                    logger.debug(f"Erro testando {tcl_path}: {e}")
                    continue
            
            logger.debug("Nenhum caminho TCL/TK funcionou")
            return False
            
        except Exception as e:
            logger.debug(f"Erro ao tentar corrigir Tkinter: {e}")
            
            # Método alternativo: tentar importar tkinter diretamente
            try:
                import tkinter as tk_test
                test_root = tk_test.Tk()
                test_root.withdraw()
                test_root.destroy()
                logger.info("✅ Tkinter funcionou sem correção de ambiente")
                return True
            except Exception as e2:
                logger.debug(f"Tkinter completamente indisponível: {e2}")
                return False
    
    def _create_overlay_alternative(self, region: Tuple[int, int, int, int]) -> None:
        """
        Cria overlay usando método alternativo (Windows apenas).
        
        Args:
            region (tuple): (x, y, width, height) da região
        """
        try:
            import ctypes
            from ctypes import wintypes
            
            x, y, w, h = region
            
            # Usar Windows API para criar overlay
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            
            # Obter DC da tela
            screen_dc = user32.GetDC(0)
            
            # Criar pen vermelho
            red_pen = gdi32.CreatePen(0, self.width, 0x0000FF)  # RGB vermelho
            old_pen = gdi32.SelectObject(screen_dc, red_pen)
            
            # Desenhar retângulo
            gdi32.MoveToEx(screen_dc, x, y, None)
            gdi32.LineTo(screen_dc, x + w, y)
            gdi32.LineTo(screen_dc, x + w, y + h)
            gdi32.LineTo(screen_dc, x, y + h)
            gdi32.LineTo(screen_dc, x, y)
            
            # Aguardar duração
            import time
            time.sleep(self.duration / 1000.0)
            
            # Limpar
            gdi32.SelectObject(screen_dc, old_pen)
            gdi32.DeleteObject(red_pen)
            user32.ReleaseDC(0, screen_dc)
            
            # Forçar repaint da tela
            user32.InvalidateRect(0, None, True)
            
            logger.info(f"Overlay alternativo criado na região: x={x}, y={y}, w={w}, h={h}")
            
        except Exception as e:
            logger.warning(f"Overlay alternativo falhou: {e}")
            logger.info(f"Região destacada seria: x={x}, y={y}, width={w}, height={h}")
    
    def show(self, region: Tuple[int, int, int, int], blocking: bool = False) -> None:
        """
        Exibe o overlay na região especificada.
        
        Args:
            region (tuple): (x, y, width, height) da região a destacar
            blocking (bool): Se True, bloqueia até o overlay desaparecer
        """
        if blocking:
            self._create_overlay_with_fallback(region)
        else:
            thread = threading.Thread(target=self._create_overlay_with_fallback, args=(region,))
            thread.daemon = True
            thread.start()
    
    def _create_overlay_with_fallback(self, region: Tuple[int, int, int, int]) -> None:
        """
        Cria overlay com múltiplos métodos de fallback.
        
        Args:
            region (tuple): (x, y, width, height) da região
        """
        # Método 1: Tentar Tkinter direto
        if self._tkinter_available:
            if self._create_overlay_tkinter(region):
                return
        
        # Método 2: Tentar corrigir Tkinter e usar
        if self._fix_tkinter_environment():
            if self._create_overlay_tkinter(region):
                return
        
        # Método 3: Overlay alternativo (Windows)
        if os.name == 'nt':
            self._create_overlay_alternative(region)
            return
        
        # Método 4: Log apenas
        x, y, w, h = region
        logger.info(f"💡 Overlay visual na região: x={x}, y={y}, width={w}, height={h}")
    
    def _create_overlay_tkinter(self, region: Tuple[int, int, int, int]) -> bool:
        """
        Cria overlay usando Tkinter.
        
        Args:
            region (tuple): (x, y, width, height) da região
            
        Returns:
            bool: True se criou com sucesso
        """
        try:
            x, y, w, h = region
            
            # Cria janela transparente
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.config(bg='black')
            
            # Configurações específicas do Windows
            if os.name == 'nt':
                try:
                    root.attributes('-transparentcolor', 'black')
                    root.attributes('-alpha', 0.3)
                except:
                    pass
            
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
            
            logger.info(f"✅ Overlay Tkinter criado com sucesso na região: x={x}, y={y}, w={w}, h={h}")
            return True
            
        except Exception as e:
            logger.debug(f"Falha no overlay Tkinter: {e}")
            return False
    
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
        Cria múltiplos overlays com fallback.
        
        Args:
            regions (list): Lista de regiões
        """
        # Tentar com Tkinter primeiro
        if self._tkinter_available or self._fix_tkinter_environment():
            if self._create_multiple_overlays_tkinter(regions):
                return
        
        # Fallback: overlay individual para cada região
        for region in regions:
            self._create_overlay_with_fallback(region)
    
    def _create_multiple_overlays_tkinter(self, regions: list) -> bool:
        """
        Cria múltiplos overlays usando Tkinter.
        
        Args:
            regions (list): Lista de regiões
            
        Returns:
            bool: True se criou com sucesso
        """
        try:
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.config(bg='black')
            
            if os.name == 'nt':
                try:
                    root.attributes('-transparentcolor', 'black')
                    root.attributes('-alpha', 0.3)
                except:
                    pass
            
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
            
            logger.info(f"✅ Múltiplos overlays criados: {len(regions)} regiões")
            return True
            
        except Exception as e:
            logger.debug(f"Falha nos múltiplos overlays Tkinter: {e}")
            return False


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
