"""
Módulo de Detección para Análisis de Coples
Implementa detección de objetos usando modelos ONNX
"""

from .detection_engine import DetectorCoplesONNX, DetectorPiezasCoples
from .bbox_processor import ProcesadorBoundingBoxes, ProcesadorPiezasCoples

__all__ = [
    'DetectorCoplesONNX',
    'DetectorPiezasCoples', 
    'ProcesadorBoundingBoxes',
    'ProcesadorPiezasCoples'
]
