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
        Realiza análisis completo: clasificación + detección
        
        Returns:
            Diccionario con resultados completos
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
                "frame": frame,
                "timestamp_captura": timestamp_captura
            }
            
            # 6. Guardar resultados por módulo
            self._guardar_por_modulos(resultados)
            
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
                "frame": frame,
                "timestamp_captura": timestamp_captura
            }
            
            # 5. Guardar resultados por módulo
            self._guardar_por_modulos(resultados)
            
            return resultados
            
        except Exception as e:
            print(f"❌ Error en detección: {e}")
            return {"error": str(e)}
    
    def _guardar_por_modulos(self, resultados: Dict):
        """Guarda resultados por módulos en carpetas separadas"""
        try:
            self.contador_resultados += 1
            timestamp_captura = resultados.get("timestamp_captura", "unknown")
            
            # 1. Guardar clasificación (si existe)
            if "clasificacion" in resultados:
                self._guardar_clasificacion_modulo(resultados, timestamp_captura)
            
            # 2. Guardar detección (si existe)
            if "detecciones" in resultados:
                self._guardar_deteccion_modulo(resultados, timestamp_captura)
            
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
    
    def _guardar_deteccion_modulo(self, resultados: Dict, timestamp_captura: str):
        """Guarda resultados de detección en su módulo específico"""
        try:
            # Guardar detección en módulo específico
            self.procesador_deteccion.procesar_deteccion_piezas(
                resultados["frame"],
                resultados["detecciones"],
                resultados["tiempos"],
                self.directorios_salida["deteccion_piezas"],
                timestamp_captura
            )
            
            print(f"   📁 Detección guardada en: {self.directorios_salida['deteccion_piezas']}")
            
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
