"""
Sistema Integrado de Análisis de Coples
Combina clasificación y detección en un solo pipeline
"""

import numpy as np
import cv2
import time
import json
from typing import Dict, List, Tuple, Optional
import os
import sys

# Agregar path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from modules.capture import CamaraTiempoOptimizada
from modules.classification import ClasificadorCoplesONNX, ProcesadorImagenClasificacion
from modules.detection import DetectorPiezasCoples, ProcesadorPiezasCoples, DetectorDefectosCoples, ProcesadorDefectos
from modules.segmentation import SegmentadorDefectosCoples, ProcesadorSegmentacionDefectos
from modules.segmentation.segmentation_piezas_engine import SegmentadorPiezasCoples
from modules.segmentation.piezas_segmentation_processor import ProcesadorSegmentacionPiezas
from config import GlobalConfig


class SistemaAnalisisIntegrado:
    """
    Sistema que integra clasificación y detección de coples
    """
    
    def __init__(self):
        """Inicializa el sistema integrado de análisis"""
        # Componentes del sistema
        self.camara = None
        self.clasificador = None
        self.detector_piezas = None
        self.detector_defectos = None
        self.segmentador_defectos = None
        self.segmentador_piezas = None
        self.procesador_clasificacion = None
        self.procesador_deteccion_piezas = None
        self.procesador_deteccion_defectos = None
        self.procesador_segmentacion_defectos = None
        self.procesador_segmentacion_piezas = None
        
        # Estado del sistema
        self.inicializado = False
        self.contador_resultados = 0
        
        # Directorios de salida por módulo
        self.directorios_salida = {
            "clasificacion": "Salida_cople/Salida_clas_def",
            "deteccion_piezas": "Salida_cople/Salida_det_pz",
            "deteccion_defectos": "Salida_cople/Salida_det_def",
            "segmentacion_defectos": "Salida_cople/Salida_seg_def",
            "segmentacion_piezas": "Salida_cople/Salida_seg_pz"
        }
        
        # Crear directorios si no existen
        for directorio in self.directorios_salida.values():
            if not os.path.exists(directorio):
                os.makedirs(directorio)
    
    def inicializar(self) -> bool:
        """
        Inicializa todos los componentes del sistema
        
        Returns:
            True si se inicializó correctamente
        """
        try:
            print("🚀 Inicializando sistema integrado de análisis...")
            
            # 1. Inicializar cámara
            print("📷 Inicializando cámara...")
            self.camara = CamaraTiempoOptimizada()
            if not self.camara.configurar_camara():
                print("❌ Error configurando cámara")
                return False
            
            # 2. Inicializar clasificador
            print("🧠 Inicializando clasificador...")
            self.clasificador = ClasificadorCoplesONNX()
            if not self.clasificador.inicializar():
                print("❌ Error inicializando clasificador")
                return False
            self.procesador_clasificacion = ProcesadorImagenClasificacion()
            
            # 3. Inicializar detector de piezas
            print("🎯 Inicializando detector de piezas...")
            self.detector_piezas = DetectorPiezasCoples()
            self.procesador_deteccion_piezas = ProcesadorPiezasCoples()
            
            # 4. Inicializar detector de defectos
            print("🎯 Inicializando detector de defectos...")
            self.detector_defectos = DetectorDefectosCoples()
            if not self.detector_defectos.inicializar():
                print("❌ Error inicializando detector de defectos")
                return False
            self.procesador_deteccion_defectos = ProcesadorDefectos()
            
            # 5. Inicializar segmentador de defectos
            print("🎯 Inicializando segmentador de defectos...")
            self.segmentador_defectos = SegmentadorDefectosCoples()
            if not self.segmentador_defectos._inicializar_modelo():
                print("❌ Error inicializando segmentador de defectos")
                return False
            self.procesador_segmentacion_defectos = ProcesadorSegmentacionDefectos()
            
            # 6. Inicializar segmentador de piezas
            print("🎯 Inicializando segmentador de piezas...")
            self.segmentador_piezas = SegmentadorPiezasCoples()
            if not self.segmentador_piezas.stats['inicializado']:
                print("❌ Error inicializando segmentador de piezas")
                return False
            self.procesador_segmentacion_piezas = ProcesadorSegmentacionPiezas()
            
            # 7. Iniciar captura continua
            print("🎬 Iniciando captura continua...")
            if not self.camara.iniciar_captura_continua():
                print("❌ Error iniciando captura continua")
                return False
            
            self.inicializado = True
            print("✅ Sistema integrado inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando sistema: {e}")
            return False
    
    def capturar_imagen_unica(self) -> Dict:
        """
        Captura una sola imagen para procesamiento por módulos
        
        Returns:
            Diccionario con la imagen capturada y metadatos
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            tiempo_inicio = time.time()
            
            # Capturar imagen
            resultado_captura = self.camara.obtener_frame_instantaneo()
            if resultado_captura is None or resultado_captura[0] is None:
                return {"error": "No se pudo capturar imagen"}
            
            # resultado_captura es una tupla: (frame, tiempo_acceso_ms, timestamp)
            frame, tiempo_acceso_ms, timestamp = resultado_captura
            
            tiempo_captura = (time.time() - tiempo_inicio) * 1000
            
            # Crear timestamp único para esta captura
            timestamp_captura = time.strftime("%Y%m%d_%H%M%S")
            
            resultados = {
                "frame": frame,
                "timestamp_captura": timestamp_captura,
                "tiempos": {
                    "captura_ms": tiempo_captura,
                    "tiempo_acceso_ms": tiempo_acceso_ms
                },
                "timestamp_original": timestamp
            }
            
            print(f"📷 Imagen capturada: {timestamp_captura}")
            return resultados
            
        except Exception as e:
            print(f"❌ Error capturando imagen: {e}")
            return {"error": str(e)}
    
    def analisis_completo(self) -> Dict:
        """
        Realiza análisis completo: clasificación + detección de manera SECUENCIAL
        
        Returns:
            Diccionario con resultados completos
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            print("🚀 INICIANDO ANÁLISIS COMPLETO SECUENCIAL...")
            
            # 1. Pausar captura continua temporalmente
            print("⏸️ Pausando captura continua para análisis...")
            self.camara.pausar_captura_continua()
            
            # 2. Capturar imagen única
            print("📷 Capturando imagen única...")
            tiempo_captura_inicio = time.time()
            resultado_captura = self.capturar_imagen_unica()
            if "error" in resultado_captura:
                # Reanudar captura continua en caso de error
                self.camara.reanudar_captura_continua()
                return resultado_captura
            
            frame = resultado_captura["frame"]
            timestamp_captura = resultado_captura["timestamp_captura"]
            tiempo_captura = (time.time() - tiempo_captura_inicio) * 1000
            print(f"✅ Imagen capturada en {tiempo_captura:.2f} ms")
            
            # Verificar frame capturado
            print(f"🔍 DEBUG - Frame capturado:")
            print(f"   Tipo: {type(frame)}")
            print(f"   Shape: {frame.shape if hasattr(frame, 'shape') else 'No shape'}")
            print(f"   Dtype: {frame.dtype if hasattr(frame, 'dtype') else 'No dtype'}")
            print(f"   Rango valores: [{frame.min() if hasattr(frame, 'min') else 'N/A'}, {frame.max() if hasattr(frame, 'max') else 'N/A'}]")
            print(f"   ID del objeto: {id(frame)}")
            
            tiempo_inicio_total = time.time()
            
            # 3. CLASIFICACIÓN (SECUENCIAL)
            print("\n🧠 EJECUTANDO CLASIFICACIÓN...")
            print(f"🔍 DEBUG - Frame para clasificación:")
            print(f"   Tipo: {type(frame)}")
            print(f"   Shape: {frame.shape if hasattr(frame, 'shape') else 'No shape'}")
            print(f"   Dtype: {frame.dtype if hasattr(frame, 'dtype') else 'No dtype'}")
            print(f"   Rango valores: [{frame.min() if hasattr(frame, 'min') else 'N/A'}, {frame.max() if hasattr(frame, 'max') else 'N/A'}]")
            
            tiempo_clasificacion_inicio = time.time()
            resultado_clasificacion = self.clasificador.clasificar(frame)
            tiempo_clasificacion = (time.time() - tiempo_clasificacion_inicio) * 1000
            clase_predicha, confianza, tiempo_inferencia_clas = resultado_clasificacion
            print(f"✅ Clasificación completada en {tiempo_clasificacion:.2f} ms")
            print(f"   Resultado: {clase_predicha} ({confianza:.2%})")
            print(f"   🔍 Frame ID después de clasificación: {id(frame)}")
            
            # 4. DETECCIÓN DE PIEZAS (SECUENCIAL)
            print("\n🎯 EJECUTANDO DETECCIÓN DE PIEZAS...")
            print(f"🔍 DEBUG - Frame para detección de piezas:")
            print(f"   Tipo: {type(frame)}")
            print(f"   Shape: {frame.shape if hasattr(frame, 'shape') else 'No shape'}")
            print(f"   Dtype: {frame.dtype if hasattr(frame, 'dtype') else 'No dtype'}")
            print(f"   Rango valores: [{frame.min() if hasattr(frame, 'min') else 'N/A'}, {frame.max() if hasattr(frame, 'max') else 'N/A'}]")
            
            # SOLUCIÓN CRÍTICA: Reinicializar detector de piezas antes de usar
            print("   🔧 Reinicializando detector de piezas...")
            try:
                self.detector_piezas.liberar()
                # Crear nueva instancia del detector de piezas
                from modules.detection.detection_engine import DetectorPiezasCoples
                self.detector_piezas = DetectorPiezasCoples(confianza_min=0.55)
                print("   ✅ Detector de piezas reinicializado correctamente")
                
                tiempo_deteccion_piezas_inicio = time.time()
                detecciones_piezas = self.detector_piezas.detectar_piezas(frame)
                tiempo_deteccion_piezas = (time.time() - tiempo_deteccion_piezas_inicio) * 1000
                print(f"✅ Detección de piezas completada en {tiempo_deteccion_piezas:.2f} ms")
                print(f"   Piezas detectadas: {len(detecciones_piezas)}")
                print(f"   🔍 Frame ID después de detección de piezas: {id(frame)}")
                
            except Exception as e:
                print(f"❌ ERROR en detección de piezas: {e}")
                detecciones_piezas = []
                tiempo_deteccion_piezas = 0
            
            # 5. DETECCIÓN DE DEFECTOS (SECUENCIAL)
            print("\n🔍 EJECUTANDO DETECCIÓN DE DEFECTOS...")
            print(f"🔍 DEBUG - Frame para detección de defectos:")
            print(f"   Tipo: {type(frame)}")
            print(f"   Shape: {frame.shape if hasattr(frame, 'shape') else 'No shape'}")
            print(f"   Dtype: {frame.dtype if hasattr(frame, 'dtype') else 'No dtype'}")
            print(f"   Rango valores: [{frame.min() if hasattr(frame, 'min') else 'N/A'}, {frame.max() if hasattr(frame, 'max') else 'N/A'}]")
            print(f"   ID del objeto: {id(frame)}")
            
            # SOLUCIÓN CRÍTICA: Reinicializar detector de defectos antes de usar
            print("   🔧 Reinicializando detector de defectos...")
            try:
                self.detector_defectos.liberar()
                if not self.detector_defectos.inicializar():
                    print("❌ Error reinicializando detector de defectos")
                    detecciones_defectos = []
                    tiempo_deteccion_defectos = 0
                else:
                    print("   ✅ Detector de defectos reinicializado correctamente")
                    
                    tiempo_deteccion_defectos_inicio = time.time()
                    detecciones_defectos = self.detector_defectos.detectar_defectos(frame)
                    tiempo_deteccion_defectos = (time.time() - tiempo_deteccion_defectos_inicio) * 1000
                    print(f"✅ Detección de defectos completada en {tiempo_deteccion_defectos:.2f} ms")
                    print(f"   Defectos detectados: {len(detecciones_defectos)}")
                    
            except Exception as e:
                print(f"❌ ERROR en detección de defectos: {e}")
                print(f"   🔍 Frame original intacto - ID: {id(frame)}")
                detecciones_defectos = []
                tiempo_deteccion_defectos = (time.time() - tiempo_deteccion_defectos_inicio) * 1000
            
            # 6. SEGMENTACIÓN DE DEFECTOS (SECUENCIAL)
            print("\n🎨 EJECUTANDO SEGMENTACIÓN DE DEFECTOS...")
            print(f"🔍 DEBUG - Frame para segmentación:")
            print(f"   Tipo: {type(frame)}")
            print(f"   Shape: {frame.shape if hasattr(frame, 'shape') else 'No shape'}")
            print(f"   Dtype: {frame.dtype if hasattr(frame, 'dtype') else 'No dtype'}")
            print(f"   Rango valores: [{frame.min() if hasattr(frame, 'min') else 'N/A'}, {frame.max() if hasattr(frame, 'max') else 'N/A'}]")
            print(f"   ID del objeto: {id(frame)}")
            
            # SOLUCIÓN CRÍTICA: Reinicializar segmentador antes de usar
            print("   🔧 Reinicializando segmentador de defectos...")
            tiempo_segmentacion_inicio = time.time()  # Inicializar antes del try
            try:
                self.segmentador_defectos.liberar()
                # Crear nueva instancia del segmentador
                from modules.segmentation.segmentation_defectos_engine import SegmentadorDefectosCoples
                self.segmentador_defectos = SegmentadorDefectosCoples(confianza_min=0.55)
                print("   ✅ Segmentador de defectos reinicializado correctamente")
                
                tiempo_segmentacion_inicio = time.time()
                segmentaciones_defectos = self.segmentador_defectos.segmentar_defectos(frame)
                tiempo_segmentacion = (time.time() - tiempo_segmentacion_inicio) * 1000
                print(f"✅ Segmentación de defectos completada en {tiempo_segmentacion:.2f} ms")
                print(f"   Segmentaciones detectadas: {len(segmentaciones_defectos)}")
                
            except Exception as e:
                print(f"❌ ERROR en segmentación de defectos: {e}")
                print(f"   🔍 Frame original intacto - ID: {id(frame)}")
                segmentaciones_defectos = []
                tiempo_segmentacion = (time.time() - tiempo_segmentacion_inicio) * 1000
            
            # 6. SEGMENTACIÓN DE PIEZAS (SECUENCIAL)
            print("\n🎨 EJECUTANDO SEGMENTACIÓN DE PIEZAS...")
            print(f"🔍 DEBUG - Frame para segmentación de piezas:")
            print(f"   Tipo: {type(frame)}")
            print(f"   Shape: {frame.shape if hasattr(frame, 'shape') else 'No shape'}")
            print(f"   Dtype: {frame.dtype if hasattr(frame, 'dtype') else 'No dtype'}")
            print(f"   Rango valores: [{frame.min() if hasattr(frame, 'min') else 'N/A'}, {frame.max() if hasattr(frame, 'max') else 'N/A'}]")
            print(f"   ID del objeto: {id(frame)}")
            
            # SOLUCIÓN CRÍTICA: Reinicializar segmentador de piezas antes de usar
            print("   🔧 Reinicializando segmentador de piezas...")
            try:
                self.segmentador_piezas.liberar()
                # Recrear segmentador de piezas
                from modules.segmentation.segmentation_piezas_engine import SegmentadorPiezasCoples
                self.segmentador_piezas = SegmentadorPiezasCoples()
                if not self.segmentador_piezas.stats['inicializado']:
                    print("   ❌ Error reinicializando segmentador de piezas")
                    segmentaciones_piezas = []
                    tiempo_segmentacion_piezas = 0
                else:
                    print("   ✅ Segmentador de piezas reinicializado correctamente")
                    
                    tiempo_segmentacion_piezas_inicio = time.time()
                    segmentaciones_piezas = self.segmentador_piezas.segmentar(frame)
                    tiempo_segmentacion_piezas = (time.time() - tiempo_segmentacion_piezas_inicio) * 1000
                    print(f"✅ Segmentación de piezas completada en {tiempo_segmentacion_piezas:.2f} ms")
                    print(f"   Segmentaciones detectadas: {len(segmentaciones_piezas)}")
                
            except Exception as e:
                print(f"❌ ERROR en segmentación de piezas: {e}")
                print(f"   🔍 Frame original intacto - ID: {id(frame)}")
                segmentaciones_piezas = []
                tiempo_segmentacion_piezas = 0
            
            # 7. Calcular tiempo total
            tiempo_total = (time.time() - tiempo_inicio_total) * 1000
            
            # 8. Crear resultados
            resultados = {
                "clasificacion": {
                    "clase": clase_predicha,
                    "confianza": confianza,
                    "tiempo_inferencia": tiempo_inferencia_clas
                },
                "detecciones_piezas": detecciones_piezas,
                "detecciones_defectos": detecciones_defectos,
                "segmentaciones_defectos": segmentaciones_defectos,
                "segmentaciones_piezas": segmentaciones_piezas,
                "tiempos": {
                    "captura_ms": tiempo_captura,
                    "clasificacion_ms": tiempo_clasificacion,
                    "deteccion_piezas_ms": tiempo_deteccion_piezas,
                    "deteccion_defectos_ms": tiempo_deteccion_defectos,
                    "segmentacion_defectos_ms": tiempo_segmentacion,
                    "segmentacion_piezas_ms": tiempo_segmentacion_piezas,
                    "total_ms": tiempo_total
                },
                "frame": frame,
                "timestamp_captura": timestamp_captura
            }
            
            # 9. Guardar resultados por módulo
            print("\n💾 GUARDANDO RESULTADOS...")
            self._guardar_por_modulos(resultados)
            
            # 10. Reanudar captura continua
            print("▶️ Reanudando captura continua...")
            self.camara.reanudar_captura_continua()
            
            print(f"\n🎉 ANÁLISIS COMPLETO FINALIZADO EN {tiempo_total:.2f} ms")
            return resultados
            
        except Exception as e:
            print(f"❌ Error en análisis completo: {e}")
            import traceback
            traceback.print_exc()
            # Reanudar captura continua en caso de error
            try:
                self.camara.reanudar_captura_continua()
            except:
                pass
            return {"error": str(e)}
    
    def solo_clasificacion(self) -> Dict:
        """
        Realiza solo clasificación
        
        Returns:
            Diccionario con resultados de clasificación
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            # 1. Capturar imagen única
            resultado_captura = self.capturar_imagen_unica()
            if "error" in resultado_captura:
                return resultado_captura
            
            frame = resultado_captura["frame"]
            timestamp_captura = resultado_captura["timestamp_captura"]
            tiempo_captura = resultado_captura["tiempos"]["captura_ms"]
            
            tiempo_inicio = time.time()
            
            # 2. Clasificación
            tiempo_clasificacion_inicio = time.time()
            resultado_clasificacion = self.clasificador.clasificar(frame)
            tiempo_clasificacion = (time.time() - tiempo_clasificacion_inicio) * 1000
            
            # 3. Calcular tiempo total
            tiempo_total = (time.time() - tiempo_inicio) * 1000
            
            # 4. Crear resultados
            # resultado_clasificacion es una tupla: (clase, confianza, tiempo_inferencia)
            clase_predicha, confianza, tiempo_inferencia_clas = resultado_clasificacion
            
            resultados = {
                "clasificacion": {
                    "clase": clase_predicha,
                    "confianza": confianza,
                    "tiempo_inferencia": tiempo_inferencia_clas
                },
                "tiempos": {
                    "captura_ms": tiempo_captura,
                    "clasificacion_ms": tiempo_clasificacion,
                    "total_ms": tiempo_total
                },
                "frame": frame,
                "timestamp_captura": timestamp_captura
            }
            
            # 5. Guardar resultados por módulo
            self._guardar_por_modulos(resultados)
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error en clasificación: {e}")
            return {"error": str(e)}
    
    def solo_deteccion(self) -> Dict:
        """
        Realiza solo detección de piezas
        
        Returns:
            Diccionario con resultados de detección
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            # 1. Capturar imagen única
            resultado_captura = self.capturar_imagen_unica()
            if "error" in resultado_captura:
                return resultado_captura
            
            frame = resultado_captura["frame"]
            timestamp_captura = resultado_captura["timestamp_captura"]
            tiempo_captura = resultado_captura["tiempos"]["captura_ms"]
            
            tiempo_inicio = time.time()
            
            # 2. Detección de piezas
            tiempo_deteccion_inicio = time.time()
            detecciones = self.detector_piezas.detectar_piezas(frame)
            tiempo_deteccion = (time.time() - tiempo_deteccion_inicio) * 1000
            
            # 3. Calcular tiempo total
            tiempo_total = (time.time() - tiempo_inicio) * 1000
            
            # 4. Crear resultados
            resultados = {
                "detecciones": detecciones,
                "tiempos": {
                    "captura_ms": tiempo_captura,
                    "deteccion_ms": tiempo_deteccion,
                    "total_ms": tiempo_total
                },
                "frame": frame,
                "timestamp_captura": timestamp_captura
            }
            
            # 5. Guardar resultados por módulo
            self._guardar_por_modulos(resultados)
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error en detección de piezas: {e}")
            return {"error": str(e)}
    
    def solo_deteccion_defectos(self) -> Dict:
        """
        Realiza solo detección de defectos (sin clasificación)
        
        Returns:
            Diccionario con resultados de detección de defectos
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            # 1. Capturar imagen única
            resultado_captura = self.capturar_imagen_unica()
            if "error" in resultado_captura:
                return resultado_captura
            
            frame = resultado_captura["frame"]
            timestamp_captura = resultado_captura["timestamp_captura"]
            tiempo_captura = resultado_captura["tiempos"]["captura_ms"]
            
            tiempo_inicio = time.time()
            
            # 2. Detección de defectos
            tiempo_deteccion_inicio = time.time()
            detecciones_defectos = self.detector_defectos.detectar_defectos(frame)
            tiempo_deteccion = (time.time() - tiempo_deteccion_inicio) * 1000
            
            # 3. Calcular tiempo total
            tiempo_total = (time.time() - tiempo_inicio) * 1000
            
            # 4. Crear resultados
            resultados = {
                "detecciones_defectos": detecciones_defectos,
                "tiempos": {
                    "captura_ms": tiempo_captura,
                    "deteccion_defectos_ms": tiempo_deteccion,
                    "total_ms": tiempo_total
                },
                "frame": frame,
                "timestamp_captura": timestamp_captura
            }
            
            # 5. Guardar resultados por módulo
            self._guardar_por_modulos(resultados)
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error en detección de defectos: {e}")
            return {"error": str(e)}
    
    def solo_segmentacion_defectos(self) -> Dict:
        """
        Realiza solo segmentación de defectos (sin clasificación ni detección)
        
        Returns:
            Diccionario con resultados de segmentación de defectos
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            # 1. Capturar imagen única
            resultado_captura = self.capturar_imagen_unica()
            if "error" in resultado_captura:
                return resultado_captura
            
            frame = resultado_captura["frame"]
            timestamp_captura = resultado_captura["timestamp_captura"]
            tiempo_captura = resultado_captura["tiempos"]["captura_ms"]
            
            tiempo_inicio = time.time()
            
            # 2. Segmentación de defectos
            tiempo_segmentacion_inicio = time.time()
            segmentaciones_defectos = self.segmentador_defectos.segmentar_defectos(frame)
            tiempo_segmentacion = (time.time() - tiempo_segmentacion_inicio) * 1000
            
            # 3. Calcular tiempo total
            tiempo_total = (time.time() - tiempo_inicio) * 1000
            
            # 4. Crear resultados
            resultados = {
                "segmentaciones_defectos": segmentaciones_defectos,
                "tiempos": {
                    "captura_ms": tiempo_captura,
                    "segmentacion_defectos_ms": tiempo_segmentacion,
                    "total_ms": tiempo_total
                },
                "frame": frame,
                "timestamp_captura": timestamp_captura
            }
            
            # 5. Guardar resultados por módulo
            self._guardar_por_modulos(resultados)
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error en segmentación de defectos: {e}")
            return {"error": str(e)}
    
    def solo_segmentacion_piezas(self) -> Dict:
        """
        Realiza solo segmentación de piezas (sin clasificación ni detección)
        
        Returns:
            Diccionario con resultados de segmentación de piezas
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            # 1. Capturar imagen única
            resultado_captura = self.capturar_imagen_unica()
            if "error" in resultado_captura:
                return resultado_captura
            
            frame = resultado_captura["frame"]
            timestamp_captura = resultado_captura["timestamp_captura"]
            tiempo_captura = resultado_captura["tiempos"]["captura_ms"]
            
            tiempo_inicio = time.time()
            
            # 2. Segmentación de piezas
            tiempo_segmentacion_inicio = time.time()
            segmentaciones_piezas = self.segmentador_piezas.segmentar(frame)
            tiempo_segmentacion = (time.time() - tiempo_segmentacion_inicio) * 1000
            
            # 3. Calcular tiempo total
            tiempo_total = (time.time() - tiempo_inicio) * 1000
            
            # 4. Crear resultados
            resultados = {
                "frame": frame,
                "timestamp_captura": timestamp_captura,
                "segmentaciones_piezas": segmentaciones_piezas,
                "tiempos": {
                    "captura_ms": tiempo_captura,
                    "segmentacion_ms": tiempo_segmentacion,
                    "total_ms": tiempo_total
                }
            }
            
            # 5. Procesar y guardar resultados
            self.procesador_segmentacion_piezas.procesar_segmentaciones(
                frame, segmentaciones_piezas, timestamp_captura
            )
            
            # 6. Mostrar resultados
            print(f"\n🎯 SEGMENTACIÓN DE PIEZAS:")
            print(f"   Segmentaciones detectadas: {len(segmentaciones_piezas)}")
            for i, seg in enumerate(segmentaciones_piezas):
                print(f"   Segmentación #{i+1}: {seg['clase']} - {seg['confianza']:.2%}")
                print(f"     BBox: ({seg['bbox']['x1']}, {seg['bbox']['y1']}) a ({seg['bbox']['x2']}, {seg['bbox']['y2']})")
                print(f"     Centroide: ({seg['centroide']['x']}, {seg['centroide']['y']})")
                print(f"     Área: {seg['area']}")
                print(f"     Dimensiones máscara: {seg['ancho_mascara']}x{seg['alto_mascara']}")
            
            print(f"\n⏱️  TIEMPOS:")
            print(f"   Captura:      {tiempo_captura:.2f} ms")
            print(f"   Segmentación: {tiempo_segmentacion:.2f} ms")
            print(f"   Total:        {tiempo_total:.2f} ms")
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error en segmentación de piezas: {e}")
            return {"error": str(e)}
    
    def _guardar_por_modulos(self, resultados: Dict):
        """Guarda resultados por módulos en carpetas separadas"""
        try:
            self.contador_resultados += 1
            timestamp_captura = resultados.get("timestamp_captura", "unknown")
            
            # 1. Guardar clasificación (si existe)
            if "clasificacion" in resultados:
                self._guardar_clasificacion_modulo(resultados, timestamp_captura)
            
            # 2. Guardar detección de piezas (si existe)
            if "detecciones_piezas" in resultados:
                self._guardar_deteccion_piezas_modulo(resultados, timestamp_captura)
            
            # 3. Guardar detección de defectos (si existe)
            if "detecciones_defectos" in resultados:
                self._guardar_deteccion_defectos_modulo(resultados, timestamp_captura)
            
            # 4. Guardar segmentación de defectos (si existe)
            if "segmentaciones_defectos" in resultados:
                self._guardar_segmentacion_defectos_modulo(resultados, timestamp_captura)
            
            # 5. Guardar segmentación de piezas (si existe)
            if "segmentaciones_piezas" in resultados:
                self._guardar_segmentacion_piezas_modulo(resultados, timestamp_captura)
            
            print(f"✅ Resultados #{self.contador_resultados} guardados por módulos")
            
        except Exception as e:
            print(f"❌ Error guardando por módulos: {e}")
    
    def _guardar_clasificacion_modulo(self, resultados: Dict, timestamp_captura: str):
        """Guarda resultados de clasificación en su módulo específico"""
        try:
            # Crear imagen anotada
            frame_anotado = self.procesador_clasificacion.agregar_anotaciones_clasificacion(
                resultados["frame"],
                resultados["clasificacion"]["clase"],
                resultados["clasificacion"]["confianza"],
                resultados["tiempos"]["captura_ms"],
                resultados["tiempos"]["clasificacion_ms"]
            )
            
            # Guardar imagen en módulo de clasificación
            nombre_imagen = f"clasificacion_{timestamp_captura}_{self.contador_resultados}.jpg"
            ruta_imagen = os.path.join(self.directorios_salida["clasificacion"], nombre_imagen)
            cv2.imwrite(ruta_imagen, frame_anotado)
            
            # Crear y guardar JSON de clasificación
            metadatos_clasificacion = {
                "archivo_imagen": nombre_imagen,
                "tipo_analisis": "clasificacion_defectos",
                "timestamp_captura": timestamp_captura,
                "clasificacion": resultados["clasificacion"],
                "tiempos": resultados["tiempos"],
                "modelo": "CopleClasDef2C1V.onnx",
                "resolucion": {
                    "ancho": 640,
                    "alto": 640,
                    "canales": 3
                }
            }
            
            nombre_json = f"clasificacion_{timestamp_captura}_{self.contador_resultados}.json"
            ruta_json = os.path.join(self.directorios_salida["clasificacion"], nombre_json)
            
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(metadatos_clasificacion, f, indent=2, ensure_ascii=False)
            
            print(f"   📁 Clasificación guardada en: {self.directorios_salida['clasificacion']}")
            
        except Exception as e:
            print(f"❌ Error guardando clasificación: {e}")
    
    def _guardar_deteccion_piezas_modulo(self, resultados: Dict, timestamp_captura: str):
        """Guarda resultados de detección de piezas en su módulo específico"""
        try:
            # Guardar detección de piezas en módulo específico
            self.procesador_deteccion_piezas.procesar_deteccion_piezas(
                resultados["frame"],
                resultados["detecciones_piezas"],   
                resultados["tiempos"],
                self.directorios_salida["deteccion_piezas"],
                timestamp_captura
            )
            
            print(f"   📁 Detección de piezas guardada en: {self.directorios_salida['deteccion_piezas']}")
            
        except Exception as e:
            print(f"❌ Error guardando detección de piezas: {e}")
    
    def _guardar_deteccion_defectos_modulo(self, resultados: Dict, timestamp_captura: str):
        """Guarda resultados de detección de defectos en su módulo específico"""
        try:
            # Guardar detección de defectos en módulo específico
            self.procesador_deteccion_defectos.procesar_deteccion_defectos(
                resultados["frame"],
                resultados["detecciones_defectos"],
                resultados["tiempos"],
                self.directorios_salida["deteccion_defectos"],
                timestamp_captura
            )
            
            print(f"   📁 Detección de defectos guardada en: {self.directorios_salida['deteccion_defectos']}")
            
        except Exception as e:
            print(f"❌ Error guardando detección de defectos: {e}")
    
    def _guardar_segmentacion_defectos_modulo(self, resultados: Dict, timestamp_captura: str):
        """Guarda resultados de segmentación de defectos en su módulo específico"""
        try:
            # Guardar segmentación de defectos en módulo específico
            self.procesador_segmentacion_defectos.procesar_segmentacion_defectos(
                resultados["frame"],
                resultados["segmentaciones_defectos"],
                resultados["tiempos"],
                self.directorios_salida["segmentacion_defectos"],
                timestamp_captura
            )
            
            print(f"   📁 Segmentación de defectos guardada en: {self.directorios_salida['segmentacion_defectos']}")
            
        except Exception as e:
            print(f"❌ Error guardando segmentación de defectos: {e}")
    
    def _guardar_segmentacion_piezas_modulo(self, resultados: Dict, timestamp_captura: str):
        """Guarda resultados de segmentación de piezas en su módulo específico"""
        try:
            # Guardar segmentación de piezas en módulo específico
            self.procesador_segmentacion_piezas.procesar_segmentaciones(
                resultados["frame"],
                resultados["segmentaciones_piezas"],
                timestamp_captura
            )
            
            print(f"   📁 Segmentación de piezas guardada en: {self.directorios_salida['segmentacion_piezas']}")
            
        except Exception as e:
            print(f"❌ Error guardando segmentación de piezas: {e}")
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del sistema"""
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        stats = {
            "sistema": "Integrado (Clasificación + Detección de Piezas + Detección de Defectos + Segmentación de Defectos + Segmentación de Piezas)",
            "resultados_procesados": self.contador_resultados,
            "camara": self.camara.obtener_estadisticas() if self.camara else {},
            "clasificador": self.clasificador.obtener_estadisticas() if self.clasificador else {},
            "detector_piezas": self.detector_piezas.obtener_estadisticas() if self.detector_piezas else {},
            "detector_defectos": self.detector_defectos.obtener_estadisticas() if self.detector_defectos else {},
            "segmentador_defectos": self.segmentador_defectos.obtener_estadisticas() if self.segmentador_defectos else {},
            "segmentador_piezas": self.segmentador_piezas.obtener_estadisticas() if self.segmentador_piezas else {}
        }
        
        return stats
    
    def liberar(self):
        """Libera todos los recursos del sistema"""
        try:
            print("🧹 Liberando recursos del sistema integrado...")
            
            if self.camara:
                self.camara.liberar()
            
            if self.clasificador:
                self.clasificador.liberar()
            
            if self.detector_piezas:
                self.detector_piezas.liberar()
            
            if self.detector_defectos:
                self.detector_defectos.liberar()
            
            if self.segmentador_defectos:
                self.segmentador_defectos.liberar()
            
            if self.segmentador_piezas:
                self.segmentador_piezas.liberar()
            
            self.inicializado = False
            print("✅ Recursos del sistema integrado liberados")
            
        except Exception as e:
            print(f"❌ Error liberando recursos: {e}")
