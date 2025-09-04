"""
Motor de segmentación de piezas de coples usando ONNX
Basado en el modelo CopleSegPZ1C1V.onnx
"""

import cv2
import numpy as np
import time
import os
from typing import List, Dict, Tuple, Optional

# Importar configuración
from config import ModelsConfig, GlobalConfig


class SegmentadorPiezasCoples:
    """
    Motor de segmentación de piezas de coples usando ONNX.
    
    Características:
    - Carga y ejecuta modelo ONNX de segmentación de piezas
    - Preprocesamiento automático de imágenes
    - Postprocesamiento de máscaras de segmentación
    - Gestión de confianza y umbrales
    - Estadísticas de rendimiento
    """
    
    def __init__(self, model_path: Optional[str] = None, confianza_min: float = 0.6):
        """
        Inicializa el segmentador de piezas de coples.
        
        Args:
            model_path (str, optional): Ruta al modelo ONNX. Si no se proporciona, usa el por defecto.
            confianza_min (float): Umbral mínimo de confianza para segmentaciones
        """
        self.model_path = model_path or os.path.join(
            ModelsConfig.MODELS_DIR, 
            ModelsConfig.SEGMENTATION_PARTS_MODEL
        )
        self.classes_path = os.path.join(
            ModelsConfig.MODELS_DIR, 
            ModelsConfig.SEGMENTATION_PARTS_CLASSES
        )
        
        # Estado del modelo
        self.model = None
        self.session = None
        self.input_name = None
        self.output_names = None
        self.input_shape = None
        self.output_shapes = None
        self.classes = []
        
        # Parámetros de configuración
        self.confianza_min = confianza_min
        self.input_size = ModelsConfig.INPUT_SIZE
        
        # Filtros de calidad para máscaras
        self.min_area_mascara = 2000        # Mínimo 2000 píxeles
        self.min_ancho_mascara = 30         # Mínimo 30 píxeles de ancho
        self.min_alto_mascara = 30          # Mínimo 30 píxeles de alto
        self.min_area_bbox = 500            # Mínimo 500 píxeles en BBox
        self.min_cobertura_bbox = 0.4       # Mínimo 40% de cobertura del BBox
        self.min_densidad_mascara = 0.1     # Mínimo 10% de densidad en la máscara
        self.max_ratio_aspecto = 10.0       # Máximo ratio de aspecto 10:1
        
        # Estadísticas
        self.stats = {
            'inicializado': False,
            'inferencias_totales': 0,
            'tiempo_total': 0.0,
            'tiempo_promedio': 0.0,
            'ultima_inferencia': 0.0
        }
        
        # Inicializar modelo
        self._inicializar_modelo()
    
    def _inicializar_modelo(self):
        """Inicializa el modelo ONNX y carga las clases."""
        try:
            # Verificar que el archivo del modelo existe
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Modelo no encontrado: {self.model_path}")
            
            # Verificar que el archivo de clases existe
            if not os.path.exists(self.classes_path):
                raise FileNotFoundError(f"Archivo de clases no encontrado: {self.classes_path}")
            
            # Cargar clases
            self._cargar_clases()
            
            # Importar ONNX Runtime
            try:
                import onnxruntime as ort
                print("✅ ONNX Runtime disponible")
            except ImportError:
                raise ImportError("ONNX Runtime no está instalado")
            
            # Configurar sesión ONNX
            providers = ModelsConfig.PROVIDERS
            session_options = ort.SessionOptions()
            session_options.intra_op_num_threads = ModelsConfig.INTRA_OP_THREADS
            session_options.inter_op_num_threads = ModelsConfig.INTER_OP_THREADS
            
            # Crear sesión
            self.session = ort.InferenceSession(
                self.model_path, 
                sess_options=session_options,
                providers=providers
            )
            
            # Obtener información de entrada y salida
            self.input_name = self.session.get_inputs()[0].name
            self.output_names = [output.name for output in self.session.get_outputs()]
            self.input_shape = self.session.get_inputs()[0].shape
            self.output_shapes = [output.shape for output in self.session.get_outputs()]
            
            print(f"🧠 Motor de segmentación de piezas ONNX inicializado:")
            print(f"   📁 Modelo: {os.path.basename(self.model_path)}")
            print(f"   📊 Input: {self.input_name} - Shape: {self.input_shape}")
            print(f"   📊 Outputs: {self.output_names}")
            print(f"   🎯 Clases: {len(self.classes)}")
            print(f"   🔧 Proveedores: {providers}")
            
            self.stats['inicializado'] = True
            
        except Exception as e:
            print(f"❌ Error inicializando segmentador de piezas: {e}")
            self.stats['inicializado'] = False
            raise
    
    def _cargar_clases(self):
        """Carga las clases desde el archivo de texto."""
        try:
            with open(self.classes_path, 'r', encoding='utf-8') as f:
                self.classes = [line.strip() for line in f.readlines() if line.strip()]
            
            print(f"✅ Clases de segmentación de piezas cargadas: {self.classes}")
            
        except Exception as e:
            print(f"❌ Error cargando clases de segmentación de piezas: {e}")
            self.classes = []
            raise
    
    def preprocesar_imagen(self, imagen: np.ndarray) -> np.ndarray:
        """
        Preprocesa la imagen para la inferencia ONNX.
        
        Args:
            imagen (np.ndarray): Imagen de entrada (H, W, C)
            
        Returns:
            np.ndarray: Imagen preprocesada (1, C, H, W)
        """
        try:
            # Debug información de entrada
            print(f"🔍 Debug imagen segmentación piezas - Original: {imagen.shape}")
            print(f"🔍 Debug imagen segmentación piezas - Input shape esperado: {self.input_size}")
            
            # Redimensionar a la resolución del modelo
            imagen_resized = cv2.resize(imagen, (self.input_size, self.input_size))
            
            # Convertir de BGR a RGB
            imagen_rgb = cv2.cvtColor(imagen_resized, cv2.COLOR_BGR2RGB)
            
            # Normalizar a [0, 1]
            imagen_normalizada = imagen_rgb.astype(np.float32) / 255.0
            
            # Transponer a formato CHW (1, 3, H, W)
            imagen_chw = np.transpose(imagen_normalizada, (2, 0, 1))
            imagen_batch = np.expand_dims(imagen_chw, axis=0)
            
            print(f"✅ Preprocesamiento exitoso: {imagen_batch.shape}")
            print(f"🔍 Debug imagen segmentación piezas - Procesada: {imagen_batch.shape}")
            
            return imagen_batch
            
        except Exception as e:
            print(f"❌ Error en preprocesamiento de imagen: {e}")
            raise
    
    def _procesar_salidas_yolo11_seg(self, outputs: List[np.ndarray], imagen_shape: Tuple[int, int]) -> List[Dict]:
        """
        Procesa las salidas del modelo YOLO11-SEG para obtener segmentaciones.
        
        Args:
            outputs (List[np.ndarray]): Salidas del modelo ONNX
            imagen_shape (Tuple[int, int]): Forma de la imagen original (H, W)
            
        Returns:
            List[Dict]: Lista de segmentaciones detectadas
        """
        try:
            print(f"🔍 Procesando salidas de segmentación de piezas...")
            print(f"   Número de outputs: {len(outputs)}")
            print(f"   Shape del primer output: {outputs[0].shape}")
            
            # Verificar que tenemos los outputs esperados
            if len(outputs) != 2:
                raise ValueError(f"Se esperaban 2 outputs, se recibieron {len(outputs)}")
            
            detections = outputs[0]  # (1, 37, 8400) - detecciones + coeficientes de máscara
            mask_protos = outputs[1]  # (1, 32, 160, 160) - prototipos de máscara
            
            print(f"🔍 DEBUG: Verificando outputs de YOLO11-SEG piezas...")
            print(f"🔍 DEBUG: Hay {len(outputs)} outputs")
            print(f"✅ DEBUG: Output 0 (detections): {detections.shape}")
            print(f"✅ DEBUG: Output 1 (mask_protos): {mask_protos.shape}")
            
            # Extraer información de detecciones
            detections = detections[0]  # (37, 8400)
            
            # Separar boxes, confidences y mask coefficients
            boxes = detections[:4].T  # (8400, 4) - x_center, y_center, width, height
            confidences = detections[4:5].T  # (8400, 1)
            mask_coeffs = detections[5:].T  # (8400, 32) - coeficientes para prototipos
            
            print(f"🔍 DEBUG: Boxes shape: {boxes.shape}")
            print(f"🔍 DEBUG: Confidences shape: {confidences.shape}")
            print(f"🔍 DEBUG: Mask coefficients shape: {mask_coeffs.shape}")
            
            # Aplicar sigmoid a las confidencias
            confidences = 1 / (1 + np.exp(-confidences))  # Sigmoid
            
            # Filtrar por confianza mínima
            valid_indices = confidences.flatten() > self.confianza_min
            valid_boxes = boxes[valid_indices]
            valid_confidences = confidences[valid_indices]
            valid_mask_coeffs = mask_coeffs[valid_indices]
            
            print(f"✅ {len(valid_confidences)} detecciones pasaron el filtro de confianza")
            
            if len(valid_confidences) == 0:
                return []
            
            # Convertir boxes de formato YOLO a formato XYXY
            boxes_xyxy = self._yolo_to_xyxy(valid_boxes, imagen_shape)
            
            # Aplicar NMS
            indices = self._aplicar_nms(boxes_xyxy, valid_confidences.flatten())
            print(f"✅ {len(indices)} detecciones después de NMS")
            
            # Procesar cada detección válida
            segmentaciones = []
            mask_protos = mask_protos[0]  # (32, 160, 160)
            
            for i, idx in enumerate(indices):
                try:
                    # Información de la detección
                    confianza = float(valid_confidences[idx])
                    bbox = boxes_xyxy[idx]
                    
                    # Generar máscara usando prototipos
                    mask_coeff = valid_mask_coeffs[idx]  # (32,)
                    mask = self._generar_mascara_prototipos(mask_coeff, mask_protos, bbox, imagen_shape)
                    
                    if mask is not None:
                        # Calcular área de la máscara
                        area_mascara = int(np.sum(mask > 0.5))
                        
                        # Calcular centroide
                        y_coords, x_coords = np.where(mask > 0.5)
                        if len(x_coords) > 0:
                            centroide_x = int(np.mean(x_coords))
                            centroide_y = int(np.mean(y_coords))
                        else:
                            centroide_x = int((bbox[0] + bbox[2]) / 2)
                            centroide_y = int((bbox[1] + bbox[3]) / 2)
                        
                        # Calcular área del bbox
                        area_bbox = int((bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))
                        
                        segmentacion = {
                            'clase': self.classes[0],  # Solo hay una clase: 'Cople'
                            'confianza': confianza,
                            'bbox': {
                                'x1': int(bbox[0]),
                                'y1': int(bbox[1]),
                                'x2': int(bbox[2]),
                                'y2': int(bbox[3])
                            },
                            'centroide': {
                                'x': centroide_x,
                                'y': centroide_y
                            },
                            'area': area_bbox,
                            'area_mascara': area_mascara,
                            'mascara': mask,
                            'alto_mascara': int(bbox[3] - bbox[1]),
                            'ancho_mascara': int(bbox[2] - bbox[0])
                        }
                        
                        # Validar calidad de la máscara
                        if self._validar_calidad_mascara(segmentacion):
                            segmentaciones.append(segmentacion)
                            
                            print(f"✅ Segmentación: {segmentacion['clase']} - {confianza:.3f} - "
                                  f"BBox: ({bbox[0]:.0f},{bbox[1]:.0f}) a ({bbox[2]:.0f},{bbox[3]:.0f}) - "
                                  f"Área: {area_bbox}")
                        else:
                            print(f"⚠️ Segmentación descartada por calidad: {segmentacion['clase']} - {confianza:.3f}")
                        
                except Exception as e:
                    print(f"⚠️ Error procesando segmentación {i}: {e}")
                    continue
            
            print(f"🎯 Total segmentaciones encontradas: {len(segmentaciones)}")
            return segmentaciones
            
        except Exception as e:
            print(f"❌ Error procesando salidas de segmentación: {e}")
            return []
    
    def _validar_calidad_mascara(self, segmentacion: Dict) -> bool:
        """
        Valida la calidad de una segmentación basada en múltiples criterios.
        
        Args:
            segmentacion (Dict): Segmentación a validar
            
        Returns:
            bool: True si la segmentación pasa todos los filtros de calidad
        """
        try:
            # Extraer información
            bbox = segmentacion['bbox']
            area_bbox = segmentacion['area']
            area_mascara = segmentacion['area_mascara']
            ancho_mascara = segmentacion['ancho_mascara']
            alto_mascara = segmentacion['alto_mascara']
            mascara = segmentacion['mascara']
            
            # 1. Validar área mínima del BBox
            if area_bbox < self.min_area_bbox:
                print(f"   ❌ BBox muy pequeño: {area_bbox} < {self.min_area_bbox}")
                return False
            
            # 2. Validar área mínima de la máscara
            if area_mascara < self.min_area_mascara:
                print(f"   ❌ Máscara muy pequeña: {area_mascara} < {self.min_area_mascara}")
                return False
            
            # 3. Validar dimensiones mínimas
            if ancho_mascara < self.min_ancho_mascara:
                print(f"   ❌ Ancho muy pequeño: {ancho_mascara} < {self.min_ancho_mascara}")
                return False
            
            if alto_mascara < self.min_alto_mascara:
                print(f"   ❌ Alto muy pequeño: {alto_mascara} < {self.min_alto_mascara}")
                return False
            
            # 4. Validar cobertura del BBox
            cobertura = area_mascara / area_bbox if area_bbox > 0 else 0
            if cobertura < self.min_cobertura_bbox:
                print(f"   ❌ Cobertura muy baja: {cobertura:.2%} < {self.min_cobertura_bbox:.2%}")
                return False
            
            # 5. Validar ratio de aspecto
            ratio_aspecto = max(ancho_mascara, alto_mascara) / min(ancho_mascara, alto_mascara)
            if ratio_aspecto > self.max_ratio_aspecto:
                print(f"   ❌ Ratio de aspecto muy alto: {ratio_aspecto:.1f} > {self.max_ratio_aspecto}")
                return False
            
            # 6. Validar densidad de la máscara
            if mascara is not None and isinstance(mascara, np.ndarray):
                # Calcular densidad en la región del BBox
                x1, y1 = bbox['x1'], bbox['y1']
                x2, y2 = bbox['x2'], bbox['y2']
                region_mascara = mascara[y1:y2, x1:x2]
                area_region = region_mascara.shape[0] * region_mascara.shape[1]
                pixels_activos_region = np.sum(region_mascara > 0.5)
                densidad = pixels_activos_region / area_region if area_region > 0 else 0
                
                if densidad < self.min_densidad_mascara:
                    print(f"   ❌ Densidad muy baja: {densidad:.2%} < {self.min_densidad_mascara:.2%}")
                    return False
            
            print(f"   ✅ Máscara válida: área={area_mascara}, cobertura={cobertura:.2%}, ratio={ratio_aspecto:.1f}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error validando máscara: {e}")
            return False
    
    def _yolo_to_xyxy(self, boxes: np.ndarray, imagen_shape: Tuple[int, int]) -> np.ndarray:
        """
        Convierte boxes de formato YOLO (x_center, y_center, width, height) a formato XYXY.
        
        Args:
            boxes (np.ndarray): Boxes en formato YOLO (N, 4)
            imagen_shape (Tuple[int, int]): Forma de la imagen (H, W)
            
        Returns:
            np.ndarray: Boxes en formato XYXY (N, 4)
        """
        h, w = imagen_shape
        
        # Convertir de coordenadas normalizadas a píxeles
        x_center = boxes[:, 0] * w
        y_center = boxes[:, 1] * h
        width = boxes[:, 2] * w
        height = boxes[:, 3] * h
        
        # Convertir a formato XYXY
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center + height / 2
        
        # Asegurar que estén dentro de los límites de la imagen
        x1 = np.clip(x1, 0, w - 1)
        y1 = np.clip(y1, 0, h - 1)
        x2 = np.clip(x2, 0, w - 1)
        y2 = np.clip(y2, 0, h - 1)
        
        return np.column_stack([x1, y1, x2, y2])
    
    def _aplicar_nms(self, boxes: np.ndarray, confidences: np.ndarray, iou_threshold: float = 0.45) -> List[int]:
        """
        Aplica Non-Maximum Suppression a las detecciones.
        
        Args:
            boxes (np.ndarray): Boxes en formato XYXY (N, 4)
            confidences (np.ndarray): Confidencias (N,)
            iou_threshold (float): Umbral de IoU para NMS
            
        Returns:
            List[int]: Índices de las detecciones que pasaron NMS
        """
        try:
            # Convertir a formato OpenCV
            boxes_cv = boxes.astype(np.float32)
            confidences_cv = confidences.astype(np.float32)
            
            # Aplicar NMS
            indices = cv2.dnn.NMSBoxes(
                boxes_cv.tolist(),
                confidences_cv.tolist(),
                self.confianza_min,
                iou_threshold
            )
            
            if len(indices) > 0:
                return indices.flatten().tolist()
            else:
                return []
                
        except Exception as e:
            print(f"⚠️ Error en NMS: {e}")
            return []
    
    def _generar_mascara_prototipos(self, mask_coeff: np.ndarray, mask_protos: np.ndarray, 
                                   bbox: np.ndarray, imagen_shape: Tuple[int, int]) -> Optional[np.ndarray]:
        """
        Genera una máscara usando los prototipos y coeficientes.
        
        Args:
            mask_coeff (np.ndarray): Coeficientes de la máscara (32,)
            mask_protos (np.ndarray): Prototipos de máscara (32, 160, 160)
            bbox (np.ndarray): Bounding box (x1, y1, x2, y2)
            imagen_shape (Tuple[int, int]): Forma de la imagen (H, W)
            
        Returns:
            Optional[np.ndarray]: Máscara generada o None si hay error
        """
        try:
            # Calcular dimensiones del bbox
            x1, y1, x2, y2 = bbox
            bbox_w = x2 - x1
            bbox_h = y2 - y1
            
            # Combinar prototipos usando los coeficientes
            mask_proto = np.zeros((160, 160), dtype=np.float32)
            for i, coeff in enumerate(mask_coeff):
                mask_proto += coeff * mask_protos[i]
            
            # Aplicar sigmoid
            mask_proto = 1 / (1 + np.exp(-mask_proto))
            
            # Redimensionar al tamaño del bbox (asegurar dimensiones válidas)
            bbox_w_int = max(1, int(bbox_w))
            bbox_h_int = max(1, int(bbox_h))
            mask_bbox = cv2.resize(mask_proto, (bbox_w_int, bbox_h_int))
            
            # Crear máscara de tamaño completo de la imagen
            mask_full = np.zeros(imagen_shape, dtype=np.float32)
            
            # Colocar la máscara en la posición correcta
            x1_int, y1_int = int(x1), int(y1)
            x2_int, y2_int = int(x2), int(y2)
            
            # Asegurar que los índices estén dentro de los límites
            h, w = imagen_shape
            x1_int = max(0, min(x1_int, w - 1))
            y1_int = max(0, min(y1_int, h - 1))
            x2_int = max(0, min(x2_int, w - 1))
            y2_int = max(0, min(y2_int, h - 1))
            
            # Ajustar el tamaño de la máscara si es necesario
            mask_h, mask_w = mask_bbox.shape
            if y1_int + mask_h > h:
                mask_h = max(0, h - y1_int)
            if x1_int + mask_w > w:
                mask_w = max(0, w - x1_int)
            
            if mask_h > 0 and mask_w > 0 and y1_int >= 0 and x1_int >= 0:
                mask_full[y1_int:y1_int + mask_h, x1_int:x1_int + mask_w] = mask_bbox[:mask_h, :mask_w]
            
            # Calcular estadísticas de la máscara
            pixels_activos = np.sum(mask_full > 0.5)
            mask_min, mask_max = np.min(mask_full), np.max(mask_full)
            
            print(f"   ✅ Máscara generada (con prototipos): {mask_full.shape}, rango: [{mask_min:.3f}, {mask_max:.3f}]")
            print(f"   📊 Píxeles activos: {pixels_activos} de {mask_full.size}")
            
            if pixels_activos > 0:
                print(f"   ✅ Máscara creada: {mask_full.shape}, área: {pixels_activos}")
                return mask_full
            else:
                print(f"   ⚠️ Máscara vacía, descartando")
                return None
                
        except Exception as e:
            print(f"❌ Error generando máscara con prototipos: {e}")
            return None
    
    def segmentar(self, imagen: np.ndarray) -> List[Dict]:
        """
        Realiza segmentación de piezas en la imagen.
        
        Args:
            imagen (np.ndarray): Imagen de entrada (H, W, C)
            
        Returns:
            List[Dict]: Lista de segmentaciones detectadas
        """
        if not self.stats['inicializado']:
            raise RuntimeError("El segmentador no está inicializado")
        
        inicio = time.time()
        
        try:
            # Preprocesar imagen
            imagen_procesada = self.preprocesar_imagen(imagen)
            
            # Realizar inferencia
            print("✅ Inferencia ONNX exitosa")
            outputs = self.session.run(self.output_names, {self.input_name: imagen_procesada})
            
            # Procesar salidas
            segmentaciones = self._procesar_salidas_yolo11_seg(outputs, imagen.shape[:2])
            
            # Actualizar estadísticas
            tiempo_inferencia = time.time() - inicio
            self.stats['inferencias_totales'] += 1
            self.stats['tiempo_total'] += tiempo_inferencia
            self.stats['tiempo_promedio'] = self.stats['tiempo_total'] / self.stats['inferencias_totales']
            self.stats['ultima_inferencia'] = tiempo_inferencia
            
            return segmentaciones
            
        except Exception as e:
            print(f"❌ Error en segmentación de piezas: {e}")
            return []
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene las estadísticas del segmentador.
        
        Returns:
            Dict: Estadísticas del segmentador
        """
        return self.stats.copy()
    
    def configurar_filtros(self, **kwargs):
        """
        Configura los filtros de calidad de máscaras dinámicamente.
        
        Args:
            **kwargs: Parámetros de filtrado a configurar
                - min_area_mascara: Área mínima de máscara
                - min_ancho_mascara: Ancho mínimo de máscara
                - min_alto_mascara: Alto mínimo de máscara
                - min_area_bbox: Área mínima de BBox
                - min_cobertura_bbox: Cobertura mínima del BBox
                - min_densidad_mascara: Densidad mínima de máscara
                - max_ratio_aspecto: Ratio máximo de aspecto
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                    print(f"✅ Filtro {key} configurado: {value}")
                else:
                    print(f"⚠️ Filtro {key} no existe")
        except Exception as e:
            print(f"❌ Error configurando filtros: {e}")
    
    def obtener_filtros_actuales(self) -> Dict:
        """
        Obtiene la configuración actual de todos los filtros.
        
        Returns:
            Dict: Configuración actual de filtros
        """
        return {
            'confianza_min': self.confianza_min,
            'min_area_mascara': self.min_area_mascara,
            'min_ancho_mascara': self.min_ancho_mascara,
            'min_alto_mascara': self.min_alto_mascara,
            'min_area_bbox': self.min_area_bbox,
            'min_cobertura_bbox': self.min_cobertura_bbox,
            'min_densidad_mascara': self.min_densidad_mascara,
            'max_ratio_aspecto': self.max_ratio_aspecto
        }
    
    def liberar(self):
        """Libera los recursos del segmentador."""
        try:
            if self.session is not None:
                del self.session
                self.session = None
            
            self.stats['inicializado'] = False
            print("✅ Recursos del segmentador de piezas liberados")
            
        except Exception as e:
            print(f"⚠️ Error liberando recursos del segmentador de piezas: {e}")
    
    def liberar_recursos(self):
        """Libera los recursos del segmentador (alias para compatibilidad)."""
        self.liberar()
