"""
Bot Vision Suite - OCR Engine

Este módulo gerencia o reconhecimento óptico de caracteres (OCR) usando Tesseract
com múltiplas configurações e técnicas otimizadas para diferentes tipos de texto.
"""

import logging
from typing import List, Tuple, Optional, Dict, Any
from PIL import Image

from ..utils.text_filters import limpar_texto, matches_filter
from ..utils.config import BotVisionConfig
from ..exceptions import OCRProcessingError, TesseractNotFoundError
from .image_processing import ImageProcessor

logger = logging.getLogger(__name__)


class OCRResult:
    """
    Classe para armazenar resultados de OCR.
    """
    def __init__(self, text: str, confidence: float, box: Tuple[int, int, int, int], 
                 method_index: int = 0, config_index: int = 0):
        self.text = text
        self.confidence = confidence
        self.box = box  # (x, y, width, height)
        self.method_index = method_index
        self.config_index = config_index
    
    def __repr__(self):
        return f"OCRResult(text='{self.text}', confidence={self.confidence:.2f})"


class OCREngine:
    """
    Engine de OCR com múltiplas configurações e processamento otimizado.
    
    Usa diferentes configurações do Tesseract e técnicas de pré-processamento
    para maximizar a precisão na detecção de texto.
    """
    
    def __init__(self, config: Optional[BotVisionConfig] = None):
        """
        Inicializa o engine de OCR.
        
        Args:
            config (BotVisionConfig, optional): Configuração da biblioteca
        """
        self.config = config or BotVisionConfig()
        self.image_processor = ImageProcessor()
        
        # Configurações OCR otimizadas
        self.ocr_configs = [
            r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789',  # Números linha única
            r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',  # Números palavra única
            r'--oem 3 --psm 6',  # Layout de página comum
            r'--oem 3 --psm 11', # Texto esparso
            r'--oem 3 --psm 7',  # Linha única
            r'--oem 3 --psm 8',  # Palavra única
            r'--oem 3 --psm 13', # Raw line. Treat the image as a single text line
        ]
        
        # Bônus de confiança por configuração e tipo de filtro
        self.confidence_bonuses = {
            "numbers": {0: 8, 1: 5, 2: 2, 3: 1},  # PSM 7 e 8 com whitelist para números
            "letters": {2: 3, 3: 2, 4: 4, 5: 3},  # PSM 6 e 11 para letras
            "both": {2: 2, 3: 1, 4: 2, 5: 1}      # Configurações gerais
        }
        
        self._setup_tesseract()
    
    def _setup_tesseract(self) -> None:
        """Configura o Tesseract com as configurações atuais."""
        try:
            self.config.setup_tesseract()
        except Exception as e:
            logger.error(f"Erro ao configurar Tesseract: {e}")
            raise TesseractNotFoundError("Não foi possível configurar o Tesseract OCR")
    
    def find_text(self, region_img: Image.Image, target_text: str, filter_type: str = "both",
                  early_confidence_threshold: float = 75.0) -> Tuple[List[Tuple], List[float], bool]:
        """
        Encontra texto usando múltiplas versões pré-processadas da imagem.
        
        Args:
            region_img (PIL.Image): Imagem da região onde buscar
            target_text (str): Texto a ser encontrado
            filter_type (str): Tipo de filtro ("numbers", "letters", "both")
            early_confidence_threshold (float): Limiar para retorno antecipado
            
        Returns:
            tuple: (boxes_encontradas, scores_confiança, encontrou_antecipado)
            
        Raises:
            OCRProcessingError: Se houver erro no processamento OCR
        """
        try:
            # Pré-processa a imagem
            processed_images = self.image_processor.preprocess_for_ocr(region_img)
            
            all_found_boxes = []
            all_confidence_scores = []
            
            logger.info(f"Buscando texto '{target_text}' com limiar de {early_confidence_threshold}%")
            
            # Bônus para métodos prioritários (primeiros métodos são otimizados)
            high_confidence_bonus = 8.0
            
            # Processa cada imagem pré-processada
            for img_index, img in enumerate(processed_images):
                for config_index, config in enumerate(self.ocr_configs):
                    results = self._process_single_image(
                        img, target_text, filter_type, config_index, config,
                        img_index, len(processed_images), high_confidence_bonus
                    )
                    
                    for result in results:
                        # Verifica se encontrou com alta confiança
                        if result.confidence >= early_confidence_threshold:
                            logger.info(f">>> Detecção com alta confiança ({result.confidence:.2f}%) encontrada!")
                            return [result.box], [result.confidence], True
                        
                        # Adiciona aos resultados gerais
                        all_found_boxes.append(result.box)
                        all_confidence_scores.append(result.confidence)
            
            return all_found_boxes, all_confidence_scores, False
            
        except Exception as e:
            logger.error(f"Erro no processamento OCR: {e}")
            raise OCRProcessingError(f"Falha na busca de texto: {e}")
    
    def _process_single_image(self, img: Image.Image, target_text: str, filter_type: str,
                             config_index: int, config: str, img_index: int, 
                             total_images: int, high_confidence_bonus: float) -> List[OCRResult]:
        """
        Processa uma única imagem com uma configuração específica de OCR.
        
        Args:
            img (PIL.Image): Imagem a ser processada
            target_text (str): Texto alvo
            filter_type (str): Tipo de filtro
            config_index (int): Índice da configuração
            config (str): String de configuração do Tesseract
            img_index (int): Índice da imagem processada
            total_images (int): Total de imagens
            high_confidence_bonus (float): Bônus de confiança
            
        Returns:
            list: Lista de OCRResult encontrados
        """
        try:
            import pytesseract
            
            # Executa OCR
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=config)
            
            # Filtra palavras reconhecidas
            recognized_words = [limpar_texto(w, filter_type) for w in data['text'] if w.strip()]
            recognized_words = [w for w in recognized_words if matches_filter(w, filter_type)]
            
            # Log para debug
            if filter_type == "numbers" and recognized_words:
                logger.debug(f"OCR Numbers (método {img_index+1}/{total_images}): {recognized_words}")
            elif filter_type == "both":
                numeric_words = [w for w in recognized_words if w.isdigit()]
                if numeric_words:
                    logger.debug(f"OCR Numbers (método {img_index+1}/{total_images}): {numeric_words}")
            
            # Processa texto alvo
            target_words = [limpar_texto(word, filter_type) for word in target_text.split()]
            target_words = [w for w in target_words if matches_filter(w, filter_type)]
            n_words = len(target_words)
            
            results = []
            
            # Busca combinações de palavras
            for idx in range(len(data['text']) - n_words + 1):
                candidate = [limpar_texto(data['text'][j], filter_type) for j in range(idx, idx + n_words)]
                
                if not all(candidate) or not all(matches_filter(word, filter_type) for word in candidate):
                    continue
                
                # Verifica correspondência
                if all(candidate[k].lower() == target_words[k].lower() for k in range(n_words)):
                    result = self._create_ocr_result(
                        data, idx, n_words, candidate, config_index, filter_type,
                        img_index, high_confidence_bonus
                    )
                    
                    if result:
                        results.append(result)
                        logger.debug(f"Encontrado '{' '.join(candidate)}' com confiança: {result.confidence:.2f}%")
            
            return results
            
        except ImportError:
            raise OCRProcessingError("pytesseract não está instalado")
        except Exception as e:
            logger.debug(f"Erro em OCR com configuração {config}: {e}")
            return []
    
    def _create_ocr_result(self, data: Dict, idx: int, n_words: int, candidate: List[str],
                          config_index: int, filter_type: str, img_index: int,
                          high_confidence_bonus: float) -> Optional[OCRResult]:
        """
        Cria um OCRResult a partir dos dados do Tesseract.
        
        Args:
            data (dict): Dados retornados pelo Tesseract
            idx (int): Índice inicial da palavra
            n_words (int): Número de palavras
            candidate (list): Palavras candidatas
            config_index (int): Índice da configuração
            filter_type (str): Tipo de filtro
            img_index (int): Índice da imagem
            high_confidence_bonus (float): Bônus de confiança
            
        Returns:
            OCRResult or None: Resultado do OCR ou None se inválido
        """
        try:
            # Calcula confiança média
            confidence_values = [
                float(data['conf'][j]) for j in range(idx, idx + n_words) 
                if float(data['conf'][j]) > 0
            ]
            
            if confidence_values:
                avg_confidence = sum(confidence_values) / len(confidence_values)
            else:
                avg_confidence = 0
            
            # Calcula bounding box
            lefts = [data['left'][j] for j in range(idx, idx + n_words)]
            tops = [data['top'][j] for j in range(idx, idx + n_words)]
            rights = [data['left'][j] + data['width'][j] for j in range(idx, idx + n_words)]
            bottoms = [data['top'][j] + data['height'][j] for j in range(idx, idx + n_words)]
            
            box = (
                min(lefts),
                min(tops),
                max(rights) - min(lefts),
                max(bottoms) - min(tops)
            )
            
            # Calcula bônus de confiança
            config_bonus = self.confidence_bonuses.get(filter_type, {}).get(config_index, 0)
            
            # Bônus para métodos de alta prioridade
            method_bonus = 0
            if img_index < 10:
                method_bonus = high_confidence_bonus * (1.0 - (img_index / 10.0))
            
            final_confidence = avg_confidence + config_bonus + method_bonus
            
            return OCRResult(
                text=' '.join(candidate),
                confidence=final_confidence,
                box=box,
                method_index=img_index,
                config_index=config_index
            )
            
        except Exception as e:
            logger.debug(f"Erro ao criar OCRResult: {e}")
            return None
    
    def extract_all_text(self, img: Image.Image, filter_type: str = "both") -> List[OCRResult]:
        """
        Extrai todo o texto encontrado na imagem.
        
        Args:
            img (PIL.Image): Imagem a ser processada
            filter_type (str): Tipo de filtro
            
        Returns:
            list: Lista de OCRResult com todo texto encontrado
        """
        try:
            import pytesseract
            
            # Usa configuração padrão para extração completa
            config = r'--oem 3 --psm 6'
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=config)
            
            results = []
            
            for i, text in enumerate(data['text']):
                if text.strip():
                    cleaned_text = limpar_texto(text, filter_type)
                    if cleaned_text and matches_filter(cleaned_text, filter_type):
                        confidence = float(data['conf'][i])
                        box = (
                            data['left'][i],
                            data['top'][i],
                            data['width'][i],
                            data['height'][i]
                        )
                        
                        results.append(OCRResult(
                            text=cleaned_text,
                            confidence=confidence,
                            box=box
                        ))
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na extração completa de texto: {e}")
            raise OCRProcessingError(f"Falha na extração: {e}")


# Funções de conveniência
def find_text_with_multiple_preprocessing(region_img: Image.Image, target_text: str, 
                                        filter_type: str = "both", 
                                        early_confidence_threshold: float = 75.0) -> Tuple[List[Tuple], List[float], bool]:
    """
    Função de conveniência para encontrar texto com processamento múltiplo.
    
    Args:
        region_img (PIL.Image): Imagem da região
        target_text (str): Texto a buscar
        filter_type (str): Tipo de filtro
        early_confidence_threshold (float): Limiar de confiança
        
    Returns:
        tuple: (boxes, confidences, early_match)
    """
    engine = OCREngine()
    return engine.find_text(region_img, target_text, filter_type, early_confidence_threshold)


def extract_text_from_image(img: Image.Image, filter_type: str = "both") -> List[str]:
    """
    Função de conveniência para extrair texto de uma imagem.
    
    Args:
        img (PIL.Image): Imagem a ser processada
        filter_type (str): Tipo de filtro
        
    Returns:
        list: Lista de textos encontrados
    """
    engine = OCREngine()
    results = engine.extract_all_text(img, filter_type)
    return [result.text for result in results]
