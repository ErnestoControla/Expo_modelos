"""
Sistema Integrado de Análisis de Coples
Combina clasificación y detección en un solo pipeline
"""

import numpy as np
import cv2
import time
from typing import Dict, List, Tuple, Optional
import os
import sys

# Agregar path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from modules.capture import CamaraTiempoOptimizada
from modules.classification import ClasificadorCoplesONNX, ProcesadorImagenClasificacion
from modules.detection import DetectorPiezasCoples, ProcesadorPiezasCoples
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
        self.detector = None
        self.procesador_clasificacion = None
        self.procesador_deteccion = None
        
        # Estado del sistema
        self.inicializado = False
        self.contador_resultados = 0
        
        # Directorio de salida
        self.directorio_salida = "Salida_cople"
        
        # Crear directorio si no existe
        if not os.path.exists(self.directorio_salida):
            os.makedirs(self.directorio_salida)
    
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
            
            # 3. Inicializar detector
            print("🎯 Inicializando detector de piezas...")
            self.detector = DetectorPiezasCoples()
            self.procesador_deteccion = ProcesadorPiezasCoples()
            
            # 4. Iniciar captura continua
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
    
    def analisis_completo(self) -> Dict:
        """
        Realiza análisis completo: clasificación + detección
        
        Returns:
            Diccionario con resultados completos
        """
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        try:
            tiempo_inicio = time.time()
            
            # 1. Capturar imagen
            tiempo_captura_inicio = time.time()
            resultado_captura = self.camara.obtener_frame_instantaneo()
            if resultado_captura is None or resultado_captura[0] is None:
                return {"error": "No se pudo capturar imagen"}
            
            # resultado_captura es una tupla: (frame, tiempo_acceso_ms, timestamp)
            frame, tiempo_acceso_ms, timestamp = resultado_captura
            
            tiempo_captura = (time.time() - tiempo_captura_inicio) * 1000
            
            # 2. Clasificación
            tiempo_clasificacion_inicio = time.time()
            resultado_clasificacion = self.clasificador.clasificar(frame)
            tiempo_clasificacion = (time.time() - tiempo_clasificacion_inicio) * 1000
            
            # 3. Detección
            tiempo_deteccion_inicio = time.time()
            detecciones = self.detector.detectar_piezas(frame)
            tiempo_deteccion = (time.time() - tiempo_deteccion_inicio) * 1000
            
            # 4. Calcular tiempo total
            tiempo_total = (time.time() - tiempo_inicio) * 1000
            
            # 5. Crear resultados
            # resultado_clasificacion es una tupla: (clase, confianza, tiempo_inferencia)
            clase_predicha, confianza, tiempo_inferencia_clas = resultado_clasificacion
            
            resultados = {
                "clasificacion": {
                    "clase": clase_predicha,
                    "confianza": confianza,
                    "tiempo_inferencia": tiempo_inferencia_clas
                },
                "detecciones": detecciones,
                "tiempos": {
                    "captura_ms": tiempo_captura,
                    "clasificacion_ms": tiempo_clasificacion,
                    "deteccion_ms": tiempo_deteccion,
                    "total_ms": tiempo_total
                },
                "frame": frame
            }
            
            # 6. Guardar resultados
            self._guardar_analisis_completo(resultados)
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error en análisis completo: {e}")
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
            tiempo_inicio = time.time()
            
            # 1. Capturar imagen
            tiempo_captura_inicio = time.time()
            resultado_captura = self.camara.obtener_frame_instantaneo()
            if resultado_captura is None or resultado_captura[0] is None:
                return {"error": "No se pudo capturar imagen"}
            
            # resultado_captura es una tupla: (frame, tiempo_acceso_ms, timestamp)
            frame, tiempo_acceso_ms, timestamp = resultado_captura
            
            tiempo_captura = (time.time() - tiempo_captura_inicio) * 1000
            
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
                "frame": frame
            }
            
            # 5. Guardar resultados
            self._guardar_solo_clasificacion(resultados)
            
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
            tiempo_inicio = time.time()
            
            # 1. Capturar imagen
            tiempo_captura_inicio = time.time()
            resultado_captura = self.camara.obtener_frame_instantaneo()
            if resultado_captura is None or resultado_captura[0] is None:
                return {"error": "No se pudo capturar imagen"}
            
            # resultado_captura es una tupla: (frame, tiempo_acceso_ms, timestamp)
            frame, tiempo_acceso_ms, timestamp = resultado_captura
            
            tiempo_captura = (time.time() - tiempo_captura_inicio) * 1000
            
            # 2. Detección
            tiempo_deteccion_inicio = time.time()
            detecciones = self.detector.detectar_piezas(frame)
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
                "frame": frame
            }
            
            # 5. Guardar resultados
            self._guardar_solo_deteccion(resultados)
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error en detección: {e}")
            return {"error": str(e)}
    
    def _guardar_analisis_completo(self, resultados: Dict):
        """Guarda resultados del análisis completo"""
        try:
            self.contador_resultados += 1
            
            # Guardar clasificación
            if "clasificacion" in resultados:
                # Crear imagen anotada
                frame_anotado = self.procesador_clasificacion.agregar_anotaciones_clasificacion(
                    resultados["frame"],
                    resultados["clasificacion"]["clase"],
                    resultados["clasificacion"]["confianza"],
                    resultados["tiempos"]["captura_ms"],
                    resultados["tiempos"]["clasificacion_ms"]
                )
                
                # Guardar imagen
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                nombre_imagen = f"completo_clasificacion_{timestamp}_{self.contador_resultados}.jpg"
                ruta_imagen = os.path.join(self.directorio_salida, nombre_imagen)
                cv2.imwrite(ruta_imagen, frame_anotado)
            
            # Guardar detección
            if "detecciones" in resultados:
                self.procesador_deteccion.procesar_deteccion_piezas(
                    resultados["frame"],
                    resultados["detecciones"],
                    resultados["tiempos"],
                    self.directorio_salida
                )
            
            print(f"✅ Análisis completo #{self.contador_resultados} guardado")
            
        except Exception as e:
            print(f"❌ Error guardando análisis completo: {e}")
    
    def _guardar_solo_clasificacion(self, resultados: Dict):
        """Guarda resultados de solo clasificación"""
        try:
            self.contador_resultados += 1
            
            # Crear imagen anotada
            frame_anotado = self.procesador_clasificacion.agregar_anotaciones_clasificacion(
                resultados["frame"],
                resultados["clasificacion"]["clase"],
                resultados["clasificacion"]["confianza"],
                resultados["tiempos"]["captura_ms"],
                resultados["tiempos"]["clasificacion_ms"]
            )
            
            # Guardar imagen
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            nombre_imagen = f"solo_clasificacion_{timestamp}_{self.contador_resultados}.jpg"
            ruta_imagen = os.path.join(self.directorio_salida, nombre_imagen)
            cv2.imwrite(ruta_imagen, frame_anotado)
            
            print(f"✅ Clasificación #{self.contador_resultados} guardada")
            
        except Exception as e:
            print(f"❌ Error guardando clasificación: {e}")
    
    def _guardar_solo_deteccion(self, resultados: Dict):
        """Guarda resultados de solo detección"""
        try:
            self.contador_resultados += 1
            
            self.procesador_deteccion.procesar_deteccion_piezas(
                resultados["frame"],
                resultados["detecciones"],
                resultados["tiempos"],
                self.directorio_salida
            )
            
            print(f"✅ Detección #{self.contador_resultados} guardada")
            
        except Exception as e:
            print(f"❌ Error guardando detección: {e}")
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del sistema"""
        if not self.inicializado:
            return {"error": "Sistema no inicializado"}
        
        stats = {
            "sistema": "Integrado (Clasificación + Detección)",
            "resultados_procesados": self.contador_resultados,
            "camara": self.camara.obtener_estadisticas() if self.camara else {},
            "clasificador": self.clasificador.obtener_estadisticas() if self.clasificador else {},
            "detector": self.detector.obtener_estadisticas() if self.detector else {}
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
            
            if self.detector:
                self.detector.liberar()
            
            self.inicializado = False
            print("✅ Recursos del sistema integrado liberados")
            
        except Exception as e:
            print(f"❌ Error liberando recursos: {e}")
