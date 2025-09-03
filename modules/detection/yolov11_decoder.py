"""
Decodificador específico para YOLOv11
Interpreta el formato de salida (1, 5, 8400) y lo convierte a coordenadas reales
"""

import numpy as np
from typing import List, Dict, Tuple
import cv2

class YOLOv11Decoder:
    """
    Decodificador para el formato de salida específico de YOLOv11
    """
    
    def __init__(self, input_shape: Tuple[int, int] = (640, 640)):
        self.input_shape = input_shape
        self.height, self.width = input_shape
        
    def decode_output(self, output: np.ndarray) -> List[Dict]:
        """
        Decodifica la salida de YOLOv11
        
        Args:
            output: Array de salida con formato (1, 5, 8400)
            
        Returns:
            Lista de detecciones con bbox, clase y confianza
        """
        detecciones = []
        
        try:
            # Formato: (1, 5, 8400)
            if len(output.shape) == 3:
                output = output[0]  # Remover batch dimension
            
            print(f"🔍 YOLOv11 Decoder - Formato: {output.shape}")
            
            # Para YOLOv11, cada fila (5) representa una detección
            # Los 8400 valores contienen características que necesitan decodificación
            
            for i in range(output.shape[0]):
                detection_features = output[i]
                
                # Analizar la distribución de valores
                self._analizar_features(detection_features, i)
                
                # Intentar diferentes estrategias de decodificación
                deteccion = self._decodificar_features(detection_features, i)
                
                if deteccion:
                    detecciones.append(deteccion)
            
            return detecciones
            
        except Exception as e:
            print(f"❌ Error en decodificación YOLOv11: {e}")
            return []
    
    def _analizar_features(self, features: np.ndarray, deteccion_id: int):
        """Analiza las características de una detección"""
        print(f"🔍 Detección {deteccion_id} - Análisis de features:")
        print(f"   - Rango: [{np.min(features):.4f}, {np.max(features):.4f}]")
        print(f"   - Valores > 0: {np.sum(features > 0)}")
        print(f"   - Valores > 1: {np.sum(features > 1)}")
        print(f"   - Valores > 100: {np.sum(features > 100)}")
        
        # Buscar valores que podrían ser coordenadas
        coord_candidates = features[(features >= 0) & (features <= 640)]
        if len(coord_candidates) > 0:
            print(f"   - Coordenadas candidatas: {coord_candidates[:5]}")
        
        # Análisis avanzado de distribución
        self._analisis_distribucion_avanzado(features, deteccion_id)
    
    def _analisis_distribucion_avanzado(self, features: np.ndarray, deteccion_id: int):
        """Análisis avanzado de la distribución de features para entender mejor YOLOv11"""
        try:
            # Calcular percentiles para entender la distribución
            percentiles = np.percentile(features, [10, 25, 50, 75, 90])
            print(f"   📊 Percentiles: 10%={percentiles[0]:.2f}, 25%={percentiles[1]:.2f}, 50%={percentiles[2]:.2f}, 75%={percentiles[3]:.2f}, 90%={percentiles[4]:.2f}")
            
            # Buscar valores únicos y su frecuencia
            valores_unicos, conteos = np.unique(features, return_counts=True)
            valores_frecuentes = valores_unicos[conteos > 1]
            
            if len(valores_frecuentes) > 0:
                print(f"   🔢 Valores repetidos: {valores_frecuentes[:5]} (conteos: {conteos[conteos > 1][:5]})")
            
            # Buscar patrones en la distribución
            # YOLOv11 podría usar diferentes rangos para diferentes tipos de información
            rangos_analisis = [
                (0, 1, "Normalizados"),
                (1, 10, "Pequeños"),
                (10, 100, "Medianos"),
                (100, 640, "Coordenadas"),
                (640, 1000, "Grandes"),
                (1000, float('inf'), "Muy grandes")
            ]
            
            for min_val, max_val, desc in rangos_analisis:
                if max_val == float('inf'):
                    valores_en_rango = features[features >= min_val]
                else:
                    valores_en_rango = features[(features >= min_val) & (features < max_val)]
                
                if len(valores_en_rango) > 0:
                    print(f"   📈 Rango {desc} [{min_val}-{max_val}): {len(valores_en_rango)} valores, ejemplo: {valores_en_rango[:3]}")
            
            # Buscar valores que podrían ser coordenadas de diferentes formas
            # Coordenadas como enteros
            coord_enteras = features[np.mod(features, 1) == 0]
            if len(coord_enteras) > 0:
                coord_validas = coord_enteras[(coord_enteras >= 0) & (coord_enteras <= 640)]
                if len(coord_validas) > 0:
                    print(f"   🎯 Coordenadas enteras válidas: {coord_validas[:5]}")
            
            # Coordenadas como flotantes con precisión específica
            for precision in [0.1, 0.5, 1.0]:
                coord_precision = features[np.abs(np.mod(features, precision)) < 0.01]
                coord_validas = coord_precision[(coord_precision >= 0) & (coord_precision <= 640)]
                if len(coord_validas) > 0:
                    print(f"   🎯 Coordenadas con precisión {precision}: {coord_validas[:3]}")
            
        except Exception as e:
            print(f"❌ Error en análisis avanzado de detección {deteccion_id}: {e}")
    
    def _decodificar_features(self, features: np.ndarray, deteccion_id: int) -> Dict:
        """
        Intenta decodificar las características a una detección válida
        
        Args:
            features: Array de 8400 características
            deteccion_id: ID de la detección
            
        Returns:
            Diccionario con la detección o None si falla
        """
        try:
            # Estrategia 1: Buscar coordenadas en rangos específicos
            deteccion = self._estrategia_coordenadas_directas(features, deteccion_id)
            if deteccion:
                return deteccion
            
            # Estrategia 2: Buscar coordenadas normalizadas
            deteccion = self._estrategia_coordenadas_normalizadas(features, deteccion_id)
            if deteccion:
                return deteccion
            
            # Estrategia 3: Buscar patrones en los features
            deteccion = self._estrategia_patrones_features(features, deteccion_id)
            if deteccion:
                return deteccion
            
            # Estrategia 4: Buscar coordenadas escaladas
            deteccion = self._estrategia_coordenadas_escaladas(features, deteccion_id)
            if deteccion:
                return deteccion
            
            # Estrategia 5: Buscar coordenadas en clusters
            deteccion = self._estrategia_clusters_coordenadas(features, deteccion_id)
            if deteccion:
                return deteccion
            
            print(f"⚠️ No se pudo decodificar detección {deteccion_id}")
            return None
            
        except Exception as e:
            print(f"❌ Error decodificando detección {deteccion_id}: {e}")
            return None
    
    def _estrategia_coordenadas_directas(self, features: np.ndarray, deteccion_id: int) -> Dict:
        """Estrategia 1: Buscar coordenadas directas (0-640)"""
        # Buscar valores en rango de coordenadas
        coord_candidates = features[(features >= 0) & (features <= 640)]
        
        if len(coord_candidates) >= 4:
            # Tomar las primeras 4 coordenadas
            coords = coord_candidates[:4]
            
            # Intentar diferentes combinaciones
            for j in range(0, len(coords), 2):
                if j + 1 < len(coords):
                    x1, y1 = coords[j], coords[j + 1]
                    
                    # Buscar x2, y2 en el resto
                    remaining = [c for k, c in enumerate(coords) if k not in [j, j + 1]]
                    if len(remaining) >= 2:
                        x2, y2 = remaining[0], remaining[1]
                        
                        # Validar y crear detección
                        deteccion = self._crear_deteccion_valida(x1, y1, x2, y2, features, deteccion_id)
                        if deteccion:
                            return deteccion
        
        return None
    
    def _estrategia_coordenadas_normalizadas(self, features: np.ndarray, deteccion_id: int) -> Dict:
        """Estrategia 2: Buscar coordenadas normalizadas (0.0-1.0)"""
        # Buscar valores normalizados
        norm_candidates = features[(features >= 0.0) & (features <= 1.0)]
        
        if len(norm_candidates) >= 4:
            # Convertir a píxeles
            coords_pixels = []
            for i, coord in enumerate(norm_candidates[:4]):
                if i % 2 == 0:  # Coordenada X
                    coords_pixels.append(int(coord * self.width))
                else:  # Coordenada Y
                    coords_pixels.append(int(coord * self.height))
            
            if len(coords_pixels) >= 4:
                x1, y1, x2, y2 = coords_pixels[:4]
                return self._crear_deteccion_valida(x1, y1, x2, y2, features, deteccion_id)
        
        return None
    
    def _estrategia_patrones_features(self, features: np.ndarray, deteccion_id: int) -> Dict:
        """Estrategia 3: Buscar patrones en los features"""
        # Buscar valores que podrían ser coordenadas (múltiplos de 8, 16, 32)
        for divisor in [8, 16, 32, 64]:
            valores_divisibles = features[features % divisor == 0]
            if len(valores_divisibles) >= 4:
                coords = valores_divisibles[:4]
                
                # Intentar crear detección
                if len(coords) >= 4:
                    x1, y1, x2, y2 = coords[:4]
                    deteccion = self._crear_deteccion_valida(x1, y1, x2, y2, features, deteccion_id)
                    if deteccion:
                        return deteccion
        
        return None
    
    def _estrategia_coordenadas_escaladas(self, features: np.ndarray, deteccion_id: int) -> Dict:
        """Estrategia 4: Buscar coordenadas escaladas (valores grandes divididos por factor)"""
        try:
            # Buscar valores que podrían ser coordenadas escaladas
            # YOLOv11 podría usar coordenadas multiplicadas por un factor
            for factor in [2, 4, 8, 16, 32, 64]:
                # Dividir valores grandes por el factor
                coords_escaladas = features / factor
                
                # Buscar coordenadas en rango válido después del escalado
                coord_candidates = coords_escaladas[(coords_escaladas >= 0) & (coords_escaladas <= 640)]
                
                if len(coord_candidates) >= 4:
                    coords = coord_candidates[:4]
                    
                    # Intentar diferentes combinaciones
                    for j in range(0, len(coords), 2):
                        if j + 1 < len(coords):
                            x1, y1 = coords[j], coords[j + 1]
                            
                            # Buscar x2, y2 en el resto
                            remaining = [c for k, c in enumerate(coords) if k not in [j, j + 1]]
                            if len(remaining) >= 2:
                                x2, y2 = remaining[0], remaining[1]
                                
                                # Validar y crear detección
                                deteccion = self._crear_deteccion_valida(x1, y1, x2, y2, features, deteccion_id)
                                if deteccion:
                                    print(f"🔍 Detección {deteccion_id} - Escalada por factor {factor}")
                                    return deteccion
            
            return None
            
        except Exception as e:
            print(f"❌ Error en estrategia escalada para detección {deteccion_id}: {e}")
            return None
    
    def _estrategia_clusters_coordenadas(self, features: np.ndarray, deteccion_id: int) -> Dict:
        """Estrategia 5: Buscar coordenadas agrupadas en clusters"""
        try:
            # Buscar valores que podrían formar clusters de coordenadas
            # YOLOv11 podría agrupar coordenadas relacionadas
            
            # Buscar valores en rangos específicos que podrían ser coordenadas
            coord_ranges = [
                (0, 100),      # Coordenadas pequeñas
                (100, 300),    # Coordenadas medianas
                (300, 500),    # Coordenadas grandes
                (500, 640)     # Coordenadas muy grandes
            ]
            
            for min_val, max_val in coord_ranges:
                coords_en_rango = features[(features >= min_val) & (features <= max_val)]
                
                if len(coords_en_rango) >= 4:
                    # Ordenar coordenadas por valor
                    coords_ordenadas = np.sort(coords_en_rango)[:4]
                    
                    # Intentar crear bounding box con coordenadas ordenadas
                    # Asumir que están en orden: x1, y1, x2, y2
                    if len(coords_ordenadas) >= 4:
                        x1, y1, x2, y2 = coords_ordenadas[:4]
                        
                        # Validar y crear detección
                        deteccion = self._crear_deteccion_valida(x1, y1, x2, y2, features, deteccion_id)
                        if deteccion:
                            print(f"🔍 Detección {deteccion_id} - Cluster en rango [{min_val}, {max_val}]")
                            return deteccion
            
            return None
            
        except Exception as e:
            print(f"❌ Error en estrategia de clusters para detección {deteccion_id}: {e}")
            return None
    
    def _crear_deteccion_valida(self, x1: float, y1: float, x2: float, y2: float, 
                               features: np.ndarray, deteccion_id: int) -> Dict:
        """Crea una detección válida si las coordenadas son correctas"""
        try:
            # Asegurar que x1 < x2 y y1 < y2
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            
            # Validar coordenadas
            if (x1 < x2 and y1 < y2 and 
                x1 >= 0 and y1 >= 0 and 
                x2 <= self.width and y2 <= self.height):
                
                # Calcular área
                area = (x2 - x1) * (y2 - y1)
                
                # Validar área mínima
                if area >= 10:
                    # Estimar confianza (usar el valor máximo de los features)
                    confianza = float(np.max(features))
                    if confianza > 100:
                        confianza = confianza / 100
                    
                    # Calcular centroide
                    centroide_x = int((x1 + x2) // 2)
                    centroide_y = int((y1 + y2) // 2)
                    
                    deteccion = {
                        "clase": "Cople",
                        "confianza": confianza,
                        "bbox": {
                            "x1": int(x1), "y1": int(y1),
                            "x2": int(x2), "y2": int(y2)
                        },
                        "centroide": {
                            "x": centroide_x,
                            "y": centroide_y
                        },
                        "area": int(area)
                    }
                    
                    print(f"✅ Detección {deteccion_id} decodificada: BBox({int(x1)},{int(y1)}) a ({int(x2)},{int(y2)}) - Conf: {confianza:.2%}")
                    return deteccion
            
            return None
            
        except Exception as e:
            print(f"❌ Error creando detección {deteccion_id}: {e}")
            return None
