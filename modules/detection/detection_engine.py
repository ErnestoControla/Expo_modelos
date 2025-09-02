"""
Motor de Detección ONNX para Coples
Implementa detección de objetos usando modelos ONNX
"""

import numpy as np
import onnxruntime as ort
import cv2
from typing import List, Dict, Tuple, Optional
import time
import os
import sys

# Agregar path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from config import ModelsConfig, GlobalConfig


class DetectorCoplesONNX:
    """
    Motor de detección ONNX para coples
    Basado en el motor de clasificación pero adaptado para detección
    """
    
    def __init__(self, modelo_path: str, clases_path: str, confianza_min: float = 0.5):
        """
        Inicializa el detector ONNX
        
        Args:
            modelo_path: Ruta al archivo .onnx
            clases_path: Ruta al archivo de clases
            confianza_min: Umbral mínimo de confianza
        """
        self.modelo_path = modelo_path
        self.clases_path = clases_path
        self.confianza_min = confianza_min
        
        # Cargar clases
        self.clases = self._cargar_clases()
        
        # Inicializar motor ONNX
        self.session = None
        self.input_name = None
        self.output_names = []
        self.input_shape = None
        
        # Estadísticas
        self.tiempo_inferencia = 0.0
        self.frames_procesados = 0
        
        # Inicializar
        self._inicializar_modelo()
    
    def _cargar_clases(self) -> List[str]:
        """Carga las clases desde el archivo de texto"""
        try:
            with open(self.clases_path, 'r', encoding='utf-8') as f:
                clases = [linea.strip() for linea in f.readlines() if linea.strip()]
            print(f"✅ Clases de detección cargadas: {clases}")
            return clases
        except Exception as e:
            print(f"❌ Error cargando clases: {e}")
            return ["Pieza_Cople"]  # Clase por defecto
    
    def _inicializar_modelo(self):
        """Inicializa el modelo ONNX"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(self.modelo_path):
                raise FileNotFoundError(f"Modelo no encontrado: {self.modelo_path}")
            
            # Configurar proveedores ONNX
            providers = ModelsConfig.PROVIDERS
            
            # Crear sesión ONNX
            self.session = ort.InferenceSession(
                self.modelo_path,
                providers=providers
            )
            
            # Obtener información del modelo
            self.input_name = self.session.get_inputs()[0].name
            self.output_names = [output.name for output in self.session.get_outputs()]
            
            # Obtener forma de entrada
            input_shape = self.session.get_inputs()[0].shape
            self.input_shape = (input_shape[2], input_shape[3])  # (height, width)
            
            print(f"🧠 Motor de detección ONNX inicializado:")
            print(f"   📁 Modelo: {os.path.basename(self.modelo_path)}")
            print(f"   📊 Input: {self.input_name} - Shape: {self.session.get_inputs()[0].shape}")
            print(f"   📊 Outputs: {self.output_names}")
            print(f"   🎯 Clases: {len(self.clases)}")
            print(f"   🔧 Proveedores: {providers}")
            
        except Exception as e:
            print(f"❌ Error inicializando modelo de detección: {e}")
            raise
    
    def preprocesar_imagen(self, imagen: np.ndarray) -> np.ndarray:
        """
        Preprocesa la imagen para el modelo de detección
        
        Args:
            imagen: Imagen RGB de entrada (H, W, C)
            
        Returns:
            Imagen preprocesada lista para inferencia
        """
        try:
            # Redimensionar a la entrada del modelo
            imagen_resized = cv2.resize(imagen, self.input_shape)
            
            # Convertir a float32 y normalizar [0, 1]
            imagen_float = imagen_resized.astype(np.float32) / 255.0
            
            # Transponer de HWC a CHW: (H, W, C) -> (C, H, W)
            imagen_chw = np.transpose(imagen_float, (2, 0, 1))
            
            # Agregar dimensión de batch: (C, H, W) -> (1, C, H, W)
            imagen_batch = np.expand_dims(imagen_chw, axis=0)
            
            return imagen_batch
            
        except Exception as e:
            print(f"❌ Error en preprocesamiento: {e}")
            raise
    
    def detectar_piezas(self, imagen: np.ndarray) -> List[Dict]:
        """
        Detecta piezas en la imagen
        
        Args:
            imagen: Imagen RGB de entrada (H, W, C)
            
        Returns:
            Lista de detecciones con bbox, clase y confianza
        """
        try:
            # Preprocesar imagen
            imagen_input = self.preprocesar_imagen(imagen)
            
            # Ejecutar inferencia
            tiempo_inicio = time.time()
            
            outputs = self.session.run(
                self.output_names,
                {self.input_name: imagen_input}
            )
            
            tiempo_inferencia = (time.time() - tiempo_inicio) * 1000  # ms
            
            # Actualizar estadísticas
            self.tiempo_inferencia = tiempo_inferencia
            self.frames_procesados += 1
            
            # Procesar salidas (asumiendo formato YOLO/ONNX)
            detecciones = self._procesar_salidas(outputs, imagen.shape[:2])
            
            return detecciones
            
        except Exception as e:
            print(f"❌ Error en detección: {e}")
            return []
    
    def _procesar_salidas(self, outputs: List[np.ndarray], imagen_shape: Tuple[int, int]) -> List[Dict]:
        """
        Procesa las salidas del modelo ONNX en formato estándar YOLO
        
        Args:
            outputs: Lista de arrays de salida del modelo
            imagen_shape: (height, width) de la imagen original
            
        Returns:
            Lista de detecciones procesadas
        """
        detecciones = []
        
        try:
            # Debug: Mostrar información de las salidas
            print(f"🔍 Debug detección - Outputs shapes: {[out.shape for out in outputs]}")
            
            # Formato estándar YOLO: [batch, num_detections, 6]
            # Donde 6 = [x1, y1, x2, y2, conf, class_id]
            detections_array = outputs[0]
            
            if len(detections_array.shape) == 3:
                detections_array = detections_array[0]  # Remover batch dimension
            
            print(f"🔍 Debug detección - Detections array shape: {detections_array.shape}")
            
            # Verificar que el formato sea el esperado
            if detections_array.shape[1] != 6:
                print(f"⚠️ Formato inesperado: esperado 6 columnas, obtenido {detections_array.shape[1]}")
                print(f"   Intentando procesar como formato estándar...")
            
            # Procesar cada detección
            for i, detection in enumerate(detections_array):
                if len(detection) >= 6:
                    x1, y1, x2, y2, conf, class_id = detection[:6]
                    
                    # Debug: Mostrar detección cruda
                    print(f"🔍 Detección {i}: x1={x1:.2f}, y1={y1:.2f}, x2={x2:.2f}, y2={y2:.2f}, conf={conf:.4f}, class_id={class_id:.2f}")
                    
                    # Filtrar por confianza (50% = 0.5)
                    if conf >= self.confianza_min:
                        # Validar coordenadas del bounding box
                        if x1 >= x2 or y1 >= y2:
                            print(f"⚠️ Bounding box inválido en detección {i}: ({x1:.2f},{y1:.2f}) a ({x2:.2f},{y2:.2f})")
                            continue
                        
                        # Convertir coordenadas a enteros
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        class_id = int(class_id)
                        
                        # Validar que las coordenadas estén dentro de la imagen
                        if x1 < 0 or y1 < 0 or x2 > imagen_shape[1] or y2 > imagen_shape[0]:
                            print(f"⚠️ Bounding box fuera de imagen en detección {i}: ({x1},{y1}) a ({x2},{y2})")
                            continue
                        
                        # Obtener nombre de clase (solo tenemos 1 clase: "Cople")
                        clase = "Cople"  # Forzar clase única
                        
                        # Calcular centroide
                        centroide_x = (x1 + x2) // 2
                        centroide_y = (y1 + y2) // 2
                        
                        # Calcular área
                        area = (x2 - x1) * (y2 - y1)
                        
                        # Validar área mínima
                        if area < 10:  # Área mínima de 10 píxeles
                            print(f"⚠️ Área muy pequeña en detección {i}: {area} píxeles")
                            continue
                        
                        # Crear detección
                        deteccion = {
                            "clase": clase,
                            "confianza": float(conf),
                            "bbox": {
                                "x1": x1, "y1": y1,
                                "x2": x2, "y2": y2
                            },
                            "centroide": {
                                "x": centroide_x,
                                "y": centroide_y
                            },
                            "area": area
                        }
                        
                        detecciones.append(deteccion)
                        print(f"✅ Detección {i} válida: {clase} - {conf:.2%} - BBox: ({x1},{y1}) a ({x2},{y2}) - Área: {area}")
            
            # Ordenar por confianza (mayor a menor)
            detecciones.sort(key=lambda x: x["confianza"], reverse=True)
            
            print(f"🎯 Total detecciones válidas: {len(detecciones)}")
            
        except Exception as e:
            print(f"❌ Error procesando salidas del modelo: {e}")
            print(f"   Formato de salida: {[out.shape for out in outputs]}")
        
        return detecciones
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del detector"""
        return {
            "modelo": os.path.basename(self.modelo_path),
            "clases": len(self.clases),
            "frames_procesados": self.frames_procesados,
            "tiempo_inferencia_promedio_ms": self.tiempo_inferencia,
            "confianza_minima": self.confianza_min
        }
    
    def liberar(self):
        """Libera recursos del detector"""
        if self.session:
            self.session = None
        print("✅ Recursos del detector liberados")


class DetectorPiezasCoples(DetectorCoplesONNX):
    """
    Detector específico para piezas de coples
    Usa el modelo CopleDetPz1C1V.onnx
    """
    
    def __init__(self, confianza_min: float = 0.5):
        """
        Inicializa detector de piezas de coples
        
        Args:
            confianza_min: Umbral mínimo de confianza
        """
        modelo_path = os.path.join(ModelsConfig.MODELS_DIR, "CopleDetPz1C1V.onnx")
        clases_path = os.path.join(ModelsConfig.MODELS_DIR, "clases_CopleDetPz1C1V.txt")
        
        super().__init__(modelo_path, clases_path, confianza_min)
        print(f"🎯 Detector de piezas de coples inicializado")
    
    def detectar_piezas_coples(self, imagen: np.ndarray) -> List[Dict]:
        """
        Detecta piezas específicas de coples
        
        Args:
            imagen: Imagen RGB de entrada
            
        Returns:
            Lista de piezas detectadas
        """
        return self.detectar_piezas(imagen)
