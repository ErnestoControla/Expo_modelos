"""
Sistema de Análisis de Coples - Aplicación Principal
Integra módulos de captura y clasificación para análisis automático de coples
"""

import cv2
import time
import os
import numpy as np

# Importar módulos propios
from config import GlobalConfig, FileConfig, CameraConfig, ModelsConfig
from utils import (
    verificar_dependencias, 
    mostrar_info_sistema,
    guardar_imagen_clasificacion,
    limpiar_memoria,
    verificar_archivo_modelo
)
from modules.capture import CamaraTiempoOptimizada
from modules.classification import ClasificadorCoplesONNX, ProcesadorImagenClasificacion
from modules.analysis_system import SistemaAnalisisIntegrado


class SistemaAnalisisCoples:
    """
    Sistema principal de análisis de coples.
    
    Integra el controlador de cámara, clasificador y detector para proporcionar
    una interfaz completa de captura, clasificación y detección de imágenes.
    """
    
    def __init__(self, ip_camara=None, modelo_path=None):
        """
        Inicializa el sistema completo.
        
        Args:
            ip_camara (str, optional): IP de la cámara
            modelo_path (str, optional): Ruta del modelo ONNX
        """
        # Sistema integrado (clasificación + detección)
        self.sistema_integrado = SistemaAnalisisIntegrado()
        
        # Sistema original (solo clasificación) - para compatibilidad
        self.camara = CamaraTiempoOptimizada(ip=ip_camara)
        self.clasificador = ClasificadorCoplesONNX(model_path=modelo_path)
        self.procesador_imagen = ProcesadorImagenClasificacion()
        
        self.frame_count = 0
        self.inicializado = False
        
        # Asegurar que el directorio de salida existe
        GlobalConfig.ensure_output_dir()
    
    def inicializar(self):
        """
        Inicializa todos los componentes del sistema.
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        print("🚀 Inicializando sistema de análisis de coples...")
        
        # Verificar dependencias
        if not verificar_dependencias():
            return False
        
        # Inicializar sistema integrado
        print("\n🔧 Inicializando sistema integrado...")
        if not self.sistema_integrado.inicializar():
            print("❌ Error inicializando sistema integrado")
            return False
        
        # El sistema integrado ya maneja todo, no necesitamos duplicar
        # Solo verificar que esté funcionando
        if not self.sistema_integrado.inicializado:
            print("❌ Sistema integrado no está inicializado")
            return False
        
        self.inicializado = True
        print("✅ Sistema inicializado correctamente")
        return True
    
    def capturar_y_clasificar(self):
        """
        Captura una imagen y la clasifica con el modelo ONNX.
        
        Returns:
            tuple: (frame, clase_predicha, confianza, tiempo_captura, tiempo_inferencia, tiempo_total)
        """
        if not self.inicializado:
            return None, None, 0, 0, 0, 0
        
        start_total = time.time()
        
        # Capturar frame
        start_capture = time.time()
        frame, tiempo_acceso, timestamp = self.camara.obtener_frame_instantaneo()
        tiempo_captura = (time.time() - start_capture) * 1000
        
        if frame is None:
            tiempo_total = (time.time() - start_total) * 1000
            return None, None, 0, tiempo_captura, 0, tiempo_total
        
        # Clasificar imagen
        clase_predicha, confianza, tiempo_inferencia = self.clasificador.clasificar(frame)
        
        tiempo_total = (time.time() - start_total) * 1000
        return frame, clase_predicha, confianza, tiempo_captura, tiempo_inferencia, tiempo_total
    
    def obtener_frame_simple(self):
        """
        Obtiene un frame simple sin clasificación.
        
        Returns:
            tuple: (frame, tiempo_acceso, timestamp)
        """
        if not self.inicializado:
            return None, 0, 0
        
        # Usar el sistema integrado para obtener el frame
        if hasattr(self, 'sistema_integrado') and self.sistema_integrado.inicializado:
            return self.sistema_integrado.camara.obtener_frame_instantaneo()
        else:
            return None, 0, 0
    
    def guardar_resultado_clasificacion(
        self, 
        imagen: np.ndarray, 
        clase_predicha: str, 
        confianza: float,
        tiempo_captura: float,
        tiempo_inferencia: float
    ):
        """
        Guarda el resultado de la clasificación.
        
        Args:
            imagen (np.ndarray): Imagen procesada
            clase_predicha (str): Clase predicha
            confianza (float): Nivel de confianza
            tiempo_captura (float): Tiempo de captura en ms
            tiempo_inferencia (float): Tiempo de inferencia en ms
        """
        try:
            # Incrementar contador
            self.frame_count += 1
            
            # Guardar imagen y JSON
            ruta_imagen, ruta_json = guardar_imagen_clasificacion(
                imagen, clase_predicha, confianza, 
                tiempo_captura, tiempo_inferencia, self.frame_count
            )
            
            if ruta_imagen and ruta_json:
                print(f"✅ Resultado #{self.frame_count} guardado correctamente")
            else:
                print(f"❌ Error guardando resultado #{self.frame_count}")
                
        except Exception as e:
            print(f"❌ Error guardando resultado: {e}")
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas completas del sistema.
        
        Returns:
            dict: Estadísticas del sistema
        """
        stats_camara = self.camara.obtener_estadisticas()
        stats_clasificador = self.clasificador.obtener_estadisticas_inferencia()
        
        return {
            'camara': stats_camara,
            'clasificador': stats_clasificador,
            'frames_procesados': self.frame_count,
            'sistema_inicializado': self.inicializado
        }
    
    def mostrar_configuracion(self):
        """Muestra la configuración completa del sistema."""
        print("\n" + "="*70)
        print("📋 CONFIGURACIÓN DEL SISTEMA")
        print("="*70)
        
        # Configuración de cámara
        self.camara.mostrar_configuracion()
        
        # Configuración del clasificador
        self.clasificador.mostrar_configuracion()
        
        print("="*70)
    
    def liberar(self):
        """Libera todos los recursos del sistema."""
        print("\n🧹 Liberando recursos del sistema...")
        
        try:
            # Liberar cámara
            self.camara.liberar()
            
            # Liberar clasificador
            self.clasificador.liberar()
            
            # Limpiar memoria
            limpiar_memoria()
            
            print("✅ Recursos liberados correctamente")
            
        except Exception as e:
            print(f"❌ Error liberando recursos: {e}")


def mostrar_menu():
    """Muestra el menú de opciones disponibles."""
    print("\n" + "="*60)
    print("🎯 SISTEMA DE ANÁLISIS DE COPLES")
    print("="*60)
    print("📋 OPCIONES PRINCIPALES:")
    print("  ENTER - Análisis Completo (Recomendado)")
    print("  '1'   - Análisis Completo")
    print("  '2'   - Solo Clasificación")
    print("  '3'   - Solo Detección de Piezas")
    print("  '4'   - Solo Detección de Defectos")
    print("  '5'   - Solo Segmentación de Defectos")
    print("  '6'   - Solo Segmentación de Piezas")
    print("")
    print("🔧 OPCIONES AVANZADAS:")
    print("  'v'   - Ver Frame Actual")
    print("  's'   - Estadísticas del Sistema")
    print("  'c'   - Configuración")
    print("  'r'   - Configuración de Robustez")
    print("  'f'   - Configuración de Fusión de Máscaras")
    print("  'q'   - Salir del Sistema")
    print("="*60)


def procesar_comando_analisis_completo(sistema, ventana_cv):
    """
    Procesa el comando de análisis completo (clasificación + detección).
    
    Args:
        sistema (SistemaAnalisisCoples): Sistema principal
        ventana_cv (str): Nombre de la ventana OpenCV
    """
    print("\n🔍 REALIZANDO ANÁLISIS COMPLETO...")
    
    # Usar sistema integrado para análisis completo
    resultados = sistema.sistema_integrado.analisis_completo()
    
    if "error" in resultados:
        print(f"❌ Error en análisis completo: {resultados['error']}")
        return True
    
    # Mostrar resultados de clasificación
    if "clasificacion" in resultados:
        clasificacion = resultados["clasificacion"]
        print(f"\n🎯 CLASIFICACIÓN:")
        print(f"   Clase:      {clasificacion['clase']}")
        print(f"   Confianza:  {clasificacion['confianza']:.2%}")
        
        if "aceptado" in clasificacion['clase'].lower():
            print(f"   Estado:     ✅ ACEPTADO")
        elif "rechazado" in clasificacion['clase'].lower():
            print(f"   Estado:     ❌ RECHAZADO")
        else:
            print(f"   Estado:     ❓ DESCONOCIDO")
    
    # Mostrar resultados de detección de piezas
    if "detecciones_piezas" in resultados:
        detecciones_piezas = resultados["detecciones_piezas"]
        print(f"\n🎯 DETECCIÓN DE PIEZAS:")
        print(f"   Piezas detectadas: {len(detecciones_piezas)}")
        
        for i, deteccion in enumerate(detecciones_piezas):
            bbox = deteccion["bbox"]
            centroide = deteccion["centroide"]
            print(f"   Pieza #{i+1}: {deteccion['clase']} - {deteccion['confianza']:.2%}")
            print(f"     BBox: ({bbox['x1']}, {bbox['y1']}) a ({bbox['x2']}, {bbox['y2']})")
            print(f"     Centroide: ({centroide['x']}, {centroide['y']})")
    
    # Mostrar resultados de detección de defectos
    if "detecciones_defectos" in resultados:
        detecciones_defectos = resultados["detecciones_defectos"]
        print(f"\n🎯 DETECCIÓN DE DEFECTOS:")
        print(f"   Defectos detectados: {len(detecciones_defectos)}")
        
        for i, defecto in enumerate(detecciones_defectos):
            bbox = defecto["bbox"]
            centroide = defecto["centroide"]
            print(f"   Defecto #{i+1}: {defecto['clase']} - {defecto['confianza']:.2%}")
            print(f"     BBox: ({bbox['x1']}, {bbox['y1']}) a ({bbox['x2']}, {bbox['y2']})")
            print(f"     Centroide: ({centroide['x']}, {centroide['y']})")
    
    # Mostrar resultados de segmentación de piezas
    if "segmentaciones_piezas" in resultados:
        segmentaciones_piezas = resultados["segmentaciones_piezas"]
        print(f"\n🎨 SEGMENTACIÓN DE PIEZAS:")
        print(f"   Segmentaciones detectadas: {len(segmentaciones_piezas)}")
        
        for i, segmentacion in enumerate(segmentaciones_piezas):
            bbox = segmentacion["bbox"]
            centroide = segmentacion["centroide"]
            print(f"   Segmentación #{i+1}: {segmentacion['clase']} - {segmentacion['confianza']:.2%}")
            print(f"     BBox: ({bbox['x1']}, {bbox['y1']}) a ({bbox['x2']}, {bbox['y2']})")
            print(f"     Centroide: ({centroide['x']}, {centroide['y']})")
            print(f"     Área: {segmentacion['area']}")
            print(f"     Dimensiones máscara: {segmentacion['ancho_mascara']}x{segmentacion['alto_mascara']}")
    
    # Mostrar tiempos
    if "tiempos" in resultados:
        tiempos = resultados["tiempos"]
        print(f"\n⏱️  TIEMPOS:")
        print(f"   Captura:      {tiempos.get('captura_ms', 0):.2f} ms")
        print(f"   Clasificación: {tiempos.get('clasificacion_ms', 0):.2f} ms")
        print(f"   Detección Piezas: {tiempos.get('deteccion_piezas_ms', 0):.2f} ms")
        print(f"   Detección Defectos: {tiempos.get('deteccion_defectos_ms', 0):.2f} ms")
        print(f"   Segmentación Defectos: {tiempos.get('segmentacion_defectos_ms', 0):.2f} ms")
        print(f"   Segmentación Piezas: {tiempos.get('segmentacion_piezas_ms', 0):.2f} ms")
        print(f"   Total:         {tiempos.get('total_ms', 0):.2f} ms")
    
    print("=" * 60)
    
    # Mostrar imagen con detecciones (si hay)
    if "frame" in resultados:
        frame = resultados["frame"]
        
        # Crear imagen anotada con detecciones de piezas
        if "detecciones_piezas" in resultados and resultados["detecciones_piezas"]:
            procesador_piezas = sistema.sistema_integrado.procesador_deteccion_piezas
            frame_anotado = procesador_piezas.dibujar_detecciones(frame, resultados["detecciones_piezas"])
            frame_anotado = procesador_piezas.agregar_informacion_tiempo(frame_anotado, resultados["tiempos"])
            frame = frame_anotado
        
        # Agregar detecciones de defectos
        if "detecciones_defectos" in resultados and resultados["detecciones_defectos"]:
            procesador_defectos = sistema.sistema_integrado.procesador_deteccion_defectos
            frame_anotado = procesador_defectos.dibujar_defectos(frame, resultados["detecciones_defectos"])
            frame_anotado = procesador_defectos.agregar_informacion_tiempo(frame_anotado, resultados["tiempos"])
            frame = frame_anotado
        
        # Mostrar imagen
        cv2.imshow(ventana_cv, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
    
    return True


def procesar_comando_solo_clasificacion(sistema, ventana_cv):
    """
    Procesa el comando de solo clasificación.
    
    Args:
        sistema (SistemaAnalisisCoples): Sistema principal
        ventana_cv (str): Nombre de la ventana OpenCV
    """
    print("\n🧠 REALIZANDO SOLO CLASIFICACIÓN...")
    
    # Usar sistema integrado para solo clasificación
    resultados = sistema.sistema_integrado.solo_clasificacion()
    
    if "error" in resultados:
        print(f"❌ Error en clasificación: {resultados['error']}")
        return True
    
    # Mostrar resultados
    if "clasificacion" in resultados:
        clasificacion = resultados["clasificacion"]
        print(f"\n🎯 CLASIFICACIÓN:")
        print(f"   Clase:      {clasificacion['clase']}")
        print(f"   Confianza:  {clasificacion['confianza']:.2%}")
        
        if "aceptado" in clasificacion['clase'].lower():
            print(f"   Estado:     ✅ ACEPTADO")
        elif "rechazado" in clasificacion['clase'].lower():
            print(f"   Estado:     ❌ RECHAZADO")
        else:
            print(f"   Estado:     ❓ DESCONOCIDO")
    
    # Mostrar tiempos
    if "tiempos" in resultados:
        tiempos = resultados["tiempos"]
        print(f"\n⏱️  TIEMPOS:")
        print(f"   Captura:      {tiempos.get('captura_ms', 0):.2f} ms")
        print(f"   Clasificación: {tiempos.get('clasificacion_ms', 0):.2f} ms")
        print(f"   Total:         {tiempos.get('total_ms', 0):.2f} ms")
    
    print("=" * 60)
    
    # Mostrar imagen
    if "frame" in resultados:
        frame = resultados["frame"]
        cv2.imshow(ventana_cv, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
    
    return True


def procesar_comando_solo_deteccion_piezas(sistema, ventana_cv):
    """
    Procesa el comando de solo detección de piezas.
    
    Args:
        sistema (SistemaAnalisisCoples): Sistema principal
        ventana_cv (str): Nombre de la ventana OpenCV
    """
    print("\n🎯 REALIZANDO SOLO DETECCIÓN DE PIEZAS...")
    
    # Usar sistema integrado para solo detección de piezas
    resultados = sistema.sistema_integrado.solo_deteccion()
    
    if "error" in resultados:
        print(f"❌ Error en detección de piezas: {resultados['error']}")
        return True
    
    # Mostrar resultados
    if "detecciones_piezas" in resultados:
        detecciones = resultados["detecciones_piezas"]
        print(f"\n🎯 DETECCIÓN DE PIEZAS:")
        print(f"   Piezas detectadas: {len(detecciones)}")
        
        for i, deteccion in enumerate(detecciones):
            bbox = deteccion["bbox"]
            centroide = deteccion["centroide"]
            print(f"   Pieza #{i+1}: {deteccion['clase']} - {deteccion['confianza']:.2%}")
            print(f"   BBox: ({bbox['x1']}, {bbox['y1']}) a ({bbox['x2']}, {bbox['y2']})")
            print(f"   Centroide: ({centroide['x']}, {centroide['y']})")
    
    # Mostrar tiempos
    if "tiempos" in resultados:
        tiempos = resultados["tiempos"]
        print(f"\n⏱️  TIEMPOS:")
        print(f"   Captura:   {tiempos.get('captura_ms', 0):.2f} ms")
        print(f"   Detección: {tiempos.get('deteccion_ms', 0):.2f} ms")
        print(f"   Total:     {tiempos.get('total_ms', 0):.2f} ms")
    
    print("=" * 60)
    
    # Mostrar imagen con detecciones
    if "frame" in resultados and "detecciones_piezas" in resultados:
        frame = resultados["frame"]
        detecciones = resultados["detecciones_piezas"]
        
        # Crear imagen anotada con detecciones
        procesador_deteccion = sistema.sistema_integrado.procesador_deteccion_piezas
        frame_anotado = procesador_deteccion.dibujar_detecciones(frame, detecciones)
        frame_anotado = procesador_deteccion.agregar_informacion_tiempo(frame_anotado, resultados["tiempos"])
        
        # Mostrar imagen
        cv2.imshow(ventana_cv, frame_anotado)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
    
    return True


def procesar_comando_solo_deteccion_defectos(sistema, ventana_cv):
    """
    Procesa el comando de solo detección de defectos.
    
    Args:
        sistema (SistemaAnalisisCoples): Sistema principal
        ventana_cv (str): Nombre de la ventana OpenCV
    """
    print("\n🎯 REALIZANDO SOLO DETECCIÓN DE DEFECTOS...")
    
    # Usar sistema integrado para solo detección de defectos
    resultados = sistema.sistema_integrado.solo_deteccion_defectos()
    
    if "error" in resultados:
        print(f"❌ Error en detección de defectos: {resultados['error']}")
        return True
    
    # Mostrar resultados
    if "detecciones_defectos" in resultados:
        detecciones = resultados["detecciones_defectos"]
        print(f"\n🎯 DETECCIÓN DE DEFECTOS:")
        print(f"   Defectos detectados: {len(detecciones)}")
        
        for i, defecto in enumerate(detecciones):
            bbox = defecto["bbox"]
            centroide = defecto["centroide"]
            print(f"   Defecto #{i+1}: {defecto['clase']} - {defecto['confianza']:.2%}")
            print(f"   BBox: ({bbox['x1']}, {bbox['y1']}) a ({bbox['x2']}, {bbox['y2']})")
            print(f"   Centroide: ({centroide['x']}, {centroide['y']})")
    
    # Mostrar tiempos
    if "tiempos" in resultados:
        tiempos = resultados["tiempos"]
        print(f"\n⏱️  TIEMPOS:")
        print(f"   Captura:   {tiempos.get('captura_ms', 0):.2f} ms")
        print(f"   Detección: {tiempos.get('deteccion_defectos_ms', 0):.2f} ms")
        print(f"   Total:     {tiempos.get('total_ms', 0):.2f} ms")
    
    print("=" * 60)
    
    # Mostrar imagen con detecciones
    if "frame" in resultados and "detecciones_defectos" in resultados:
        frame = resultados["frame"]
        detecciones = resultados["detecciones_defectos"]
        
        # Crear imagen anotada con detecciones
        procesador_defectos = sistema.sistema_integrado.procesador_deteccion_defectos
        frame_anotado = procesador_defectos.dibujar_defectos(frame, detecciones)
        frame_anotado = procesador_defectos.agregar_informacion_tiempo(frame_anotado, resultados["tiempos"])
        
        # Mostrar imagen
        cv2.imshow(ventana_cv, frame_anotado)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
    
    return True


def procesar_comando_solo_segmentacion_defectos(sistema, ventana_cv):
    """
    Procesa el comando de solo segmentación de defectos.
    
    Args:
        sistema (SistemaAnalisisCoples): Sistema principal
        ventana_cv (str): Nombre de la ventana OpenCV
    """
    print("\n🎯 REALIZANDO SOLO SEGMENTACIÓN DE DEFECTOS...")
    
    # Usar sistema integrado para solo segmentación de defectos
    resultados = sistema.sistema_integrado.solo_segmentacion_defectos()
    
    if "error" in resultados:
        print(f"❌ Error en segmentación de defectos: {resultados['error']}")
        return True
    
    # Mostrar resultados de segmentación de defectos
    if "segmentaciones_defectos" in resultados:
        segmentaciones_defectos = resultados["segmentaciones_defectos"]
        print(f"\n🎯 SEGMENTACIÓN DE DEFECTOS:")
        print(f"   Segmentaciones detectadas: {len(segmentaciones_defectos)}")
        
        for i, segmentacion in enumerate(segmentaciones_defectos):
            bbox = segmentacion["bbox"]
            centroide = segmentacion["centroide"]
            print(f"   Segmentación #{i+1}: {segmentacion['clase']} - {segmentacion['confianza']:.2%}")
            print(f"     BBox: ({bbox['x1']}, {bbox['y1']}) a ({bbox['x2']}, {bbox['y2']})")
            print(f"     Centroide: ({centroide['x']}, {centroide['y']})")
            print(f"     Área: {segmentacion['area']}")
    
    # Mostrar tiempos
    if "tiempos" in resultados:
        tiempos = resultados["tiempos"]
        print(f"\n⏱️  TIEMPOS:")
        print(f"   Captura:      {tiempos.get('captura_ms', 0):.2f} ms")
        print(f"   Segmentación: {tiempos.get('segmentacion_defectos_ms', 0):.2f} ms")
        print(f"   Total:        {tiempos.get('total_ms', 0):.2f} ms")
    
    print("=" * 60)
    
    # Mostrar imagen con segmentaciones (si hay)
    if "frame" in resultados:
        frame = resultados["frame"]
        
        # Crear imagen anotada con segmentaciones de defectos
        if "segmentaciones_defectos" in resultados and resultados["segmentaciones_defectos"]:
            frame_anotado = sistema.sistema_integrado.procesador_segmentacion_defectos.dibujar_segmentaciones(
                frame, resultados["segmentaciones_defectos"]
            )
            
            # Agregar información de tiempos
            frame_anotado = sistema.sistema_integrado.procesador_segmentacion_defectos.agregar_informacion_tiempo(
                frame_anotado, resultados["tiempos"]
            )
            
            # Mostrar imagen
            cv2.imshow(ventana_cv, frame_anotado)
            cv2.waitKey(1)
        else:
            # Mostrar imagen sin anotaciones
            cv2.imshow(ventana_cv, frame)
            cv2.waitKey(1)
    
    return True


def procesar_comando_solo_segmentacion_piezas(sistema, ventana_cv):
    """
    Procesa el comando de solo segmentación de piezas.
    
    Args:
        sistema (SistemaAnalisisCoples): Sistema principal
        ventana_cv (str): Nombre de la ventana OpenCV
    """
    print("\n🎯 REALIZANDO SOLO SEGMENTACIÓN DE PIEZAS...")
    
    # Usar sistema integrado para solo segmentación de piezas
    resultados = sistema.sistema_integrado.solo_segmentacion_piezas()
    
    if "error" in resultados:
        print(f"❌ Error en segmentación de piezas: {resultados['error']}")
        return True
    
    # Mostrar resultados de segmentación de piezas
    if "segmentaciones_piezas" in resultados:
        segmentaciones_piezas = resultados["segmentaciones_piezas"]
        print(f"\n🎯 SEGMENTACIÓN DE PIEZAS:")
        print(f"   Segmentaciones detectadas: {len(segmentaciones_piezas)}")
        for i, seg in enumerate(segmentaciones_piezas):
            print(f"   Segmentación #{i+1}: {seg['clase']} - {seg['confianza']:.2%}")
            print(f"     BBox: ({seg['bbox']['x1']}, {seg['bbox']['y1']}) a ({seg['bbox']['x2']}, {seg['bbox']['y2']})")
            print(f"     Centroide: ({seg['centroide']['x']}, {seg['centroide']['y']})")
            print(f"     Área: {seg['area']}")
            print(f"     Dimensiones máscara: {seg['ancho_mascara']}x{seg['alto_mascara']}")
    
    # Mostrar tiempos
    if "tiempos" in resultados:
        tiempos = resultados["tiempos"]
        print(f"\n⏱️  TIEMPOS:")
        print(f"   Captura:      {tiempos['captura_ms']:.2f} ms")
        print(f"   Segmentación: {tiempos['segmentacion_ms']:.2f} ms")
        print(f"   Total:        {tiempos['total_ms']:.2f} ms")
    
    print("=" * 60)
    
    # Mostrar imagen con segmentaciones (si hay)
    if "frame" in resultados:
        frame = resultados["frame"]
        
        # Crear imagen anotada con segmentaciones de piezas
        if "segmentaciones_piezas" in resultados and resultados["segmentaciones_piezas"]:
            frame_anotado = sistema.sistema_integrado.procesador_segmentacion_piezas._crear_visualizacion(
                frame, resultados["segmentaciones_piezas"]
            )
            
            # Mostrar imagen
            cv2.imshow(ventana_cv, frame_anotado)
            cv2.waitKey(1)
        else:
            # Mostrar imagen sin anotaciones
            cv2.imshow(ventana_cv, frame)
            cv2.waitKey(1)
    
    return True


def procesar_comando_clasificacion(sistema, ventana_cv):
    """
    Procesa el comando de captura y clasificación.
    
    Args:
        sistema (SistemaAnalisisCoples): Sistema principal
        ventana_cv (str): Nombre de la ventana OpenCV
    """
    frame, clase_predicha, confianza, tiempo_captura, tiempo_inferencia, tiempo_total = sistema.capturar_y_clasificar()
    
    if frame is not None and clase_predicha is not None:
        print(f"\n🔍 RESULTADO DE CLASIFICACIÓN #{sistema.frame_count}")
        print("=" * 60)
        print(f"⏱️  TIEMPOS:")
        print(f"   Captura:    {tiempo_captura:.2f} ms")
        print(f"   Inferencia: {tiempo_inferencia:.2f} ms")
        print(f"   Total:      {tiempo_total:.2f} ms")
        
        print(f"\n🎯 CLASIFICACIÓN:")
        print(f"   Clase:      {clase_predicha}")
        print(f"   Confianza:  {confianza:.2%}")
        
        # Determinar color para la etiqueta
        if "aceptado" in clase_predicha.lower():
            print(f"   Estado:     ✅ ACEPTADO")
        elif "rechazado" in clase_predicha.lower():
            print(f"   Estado:     ❌ RECHAZADO")
        else:
            print(f"   Estado:     ❓ DESCONOCIDO")
        
        print("=" * 60)
        
        # Crear imagen con anotaciones
        frame_anotado = sistema.procesador_imagen.agregar_anotaciones_clasificacion(
            frame, clase_predicha, confianza, tiempo_captura, tiempo_inferencia
        )
        
        # Guardar resultado
        sistema.guardar_resultado_clasificacion(
            frame_anotado, clase_predicha, confianza, tiempo_captura, tiempo_inferencia
        )
        
        # Mostrar imagen
        cv2.imshow(ventana_cv, frame_anotado)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
    else:
        print("⚠️ No hay frames disponibles o error en clasificación")
    
    return True


def procesar_comando_ver(sistema, ventana_cv):
    """
    Procesa el comando de ver frame sin clasificar.
    
    Args:
        sistema (SistemaAnalisisCoples): Sistema principal
        ventana_cv (str): Nombre de la ventana OpenCV
    """
    frame, tiempo_acceso, timestamp = sistema.obtener_frame_simple()
    
    if frame is not None:
        print(f"📷 Frame obtenido en {tiempo_acceso:.2f} ms")
        print(f"📐 Dimensiones: {frame.shape[1]}x{frame.shape[0]}")
        print(f"🎨 Tipo: {frame.dtype}")
        print(f"⏰ Timestamp: {timestamp}")
        
        # Mostrar frame
        cv2.imshow(ventana_cv, frame)
        print("🖼️  Frame mostrado. Presiona cualquier tecla para continuar...")
        
        # Esperar a que el usuario presione una tecla
        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            return False
        elif key == 27:  # ESC
            return False
    else:
        print("⚠️ No hay frames disponibles")
        print("💡 Verifica que la cámara esté conectada y funcionando")
    
    return True


def procesar_comando_estadisticas(sistema):
    """
    Procesa el comando de mostrar estadísticas.
    
    Args:
        sistema (SistemaAnalisisCoples): Sistema principal
    """
    stats = sistema.obtener_estadisticas()
    
    print(f"\n📊 ESTADÍSTICAS DEL SISTEMA:")
    print("=" * 50)
    
    # Estadísticas de cámara
    if stats['camara']:
        cam_stats = stats['camara']
        print(f"📷 CÁMARA:")
        print(f"   FPS Real: {cam_stats.get('fps_real', 0):.1f}")
        print(f"   Frames Totales: {cam_stats.get('frames_totales', 0)}")
        print(f"   Buffers Listos: {cam_stats.get('buffers_listos', 0)}/2")
        
        # Estadísticas de tiempo
        tiempo_cap = cam_stats.get('tiempo_captura', {})
        if tiempo_cap:
            print(f"   Tiempo Captura: {tiempo_cap.get('promedio', 0):.2f} ms (±{tiempo_cap.get('std', 0):.2f})")
    
    # Estadísticas del clasificador
    if stats['clasificador']:
        class_stats = stats['clasificador']
        print(f"\n🧠 CLASIFICADOR:")
        print(f"   Inferencias: {class_stats.get('total_inferences', 0)}")
        print(f"   Tiempo Promedio: {class_stats.get('tiempo_promedio', 0):.2f} ms")
        print(f"   Tiempo Min: {class_stats.get('tiempo_min', 0):.2f} ms")
        print(f"   Tiempo Max: {class_stats.get('tiempo_max', 0):.2f} ms")
    
    print(f"\n📈 SISTEMA:")
    print(f"   Frames Procesados: {stats['frames_procesados']}")
    print(f"   Estado: {'OPERATIVO' if stats['sistema_inicializado'] else 'NO INICIALIZADO'}")
    print("=" * 50)


def procesar_comando_umbral(sistema):
    """
    Procesa el comando de cambiar umbral de confianza.
    
    Args:
        sistema (SistemaAnalisisCoples): Sistema principal
    """
    try:
        print(f"\n🎯 Umbral actual: {sistema.clasificador.confidence_threshold}")
        nuevo_umbral = float(input("Nuevo umbral (0.0 - 1.0): "))
        
        if sistema.clasificador.cambiar_umbral_confianza(nuevo_umbral):
            print(f"✅ Umbral cambiado a: {nuevo_umbral}")
        else:
            print("❌ No se pudo cambiar el umbral")
            
    except ValueError:
        print("❌ Valor no válido. Debe ser un número entre 0.0 y 1.0")
    except Exception as e:
        print(f"❌ Error cambiando umbral: {e}")


def main():
    """Función principal del sistema de análisis de coples."""
    # Mostrar información del sistema
    mostrar_info_sistema()
    
    # Inicializar sistema
    sistema = SistemaAnalisisCoples()
    
    if not sistema.inicializar():
        print("❌ Error inicializando el sistema")
        return
    
    # Mostrar menú inicial
    mostrar_menu()
    
    # Crear ventana OpenCV
    ventana_cv = 'Sistema de Análisis de Coples'
    cv2.namedWindow(ventana_cv, cv2.WINDOW_NORMAL)
    
    try:
        # Bucle principal de la aplicación
        while True:
            entrada = input("\n🎯 Comando: ").strip().lower()
            
            if entrada == 'q':
                print("🔄 Saliendo del sistema...")
                break
            
            elif entrada == 's':
                procesar_comando_estadisticas(sistema)
            
            elif entrada == 'c':
                procesar_comando_configuracion(sistema)
            
            elif entrada == 'r':
                procesar_comando_robustez(sistema)
            
            elif entrada == 'f':
                procesar_comando_fusion(sistema)
            
            elif entrada == 'v':
                if not procesar_comando_ver(sistema, ventana_cv):
                    break
            
            elif entrada == '1' or entrada == '':
                # Comando de análisis completo (ENTER o '1')
                if not procesar_comando_analisis_completo(sistema, ventana_cv):
                    break
            
            elif entrada == '2':
                # Solo Clasificación
                if not procesar_comando_solo_clasificacion(sistema, ventana_cv):
                    break
            
            elif entrada == '3':
                # Solo Detección de Piezas
                if not procesar_comando_solo_deteccion_piezas(sistema, ventana_cv):
                    break
            
            elif entrada == '4':
                # Solo Detección de Defectos
                if not procesar_comando_solo_deteccion_defectos(sistema, ventana_cv):
                    break
            
            elif entrada == '5':
                # Solo Segmentación de Defectos
                if not procesar_comando_solo_segmentacion_defectos(sistema, ventana_cv):
                    break
            
            elif entrada == '6':
                # Solo Segmentación de Piezas
                if not procesar_comando_solo_segmentacion_piezas(sistema, ventana_cv):
                    break
            
            elif entrada == 'help' or entrada == 'h':
                mostrar_menu()
            
            else:
                print("❌ Comando no reconocido.")
                print("💡 Usa ENTER para análisis completo o 'q' para salir.")
                print("💡 Presiona 'h' para ver el menú de ayuda.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrumpido por usuario")
    
    finally:
        # Limpieza final
        print("\n🧹 Limpiando recursos...")
        try:
            # Liberar sistema integrado
            if hasattr(sistema, 'sistema_integrado'):
                sistema.sistema_integrado.liberar()
            
            # Liberar sistema original
            sistema.liberar()
        except:
            pass
        
        # Limpiar OpenCV
        try:
            cv2.destroyAllWindows()
            cv2.waitKey(1)
        except:
            pass
        
        # Liberar memoria final
        limpiar_memoria()
        
        print("✅ Sistema terminado correctamente")


def procesar_comando_configuracion(sistema):
    """Muestra la configuración actual del sistema."""
    print("\n🔧 CONFIGURACIÓN ACTUAL DEL SISTEMA")
    print("="*50)
    
    # Mostrar configuración de la cámara
    print("📷 Cámara:")
    print(f"   IP: {CameraConfig.DEFAULT_IP}")
    print(f"   Resolución: {CameraConfig.ROI_WIDTH}x{CameraConfig.ROI_HEIGHT}")
    print(f"   ROI: {CameraConfig.ROI_WIDTH}x{CameraConfig.ROI_HEIGHT}")
    print(f"   Offset: ({CameraConfig.ROI_OFFSET_X}, {CameraConfig.ROI_OFFSET_Y})")
    print(f"   Exposición: {CameraConfig.EXPOSURE_TIME}μs")
    print(f"   FPS: {CameraConfig.FRAMERATE}")
    print(f"   Ganancia: {CameraConfig.GAIN}")
    
    # Mostrar configuración de modelos
    print("\n🧠 Modelos:")
    print(f"   Clasificación: {ModelsConfig.CLASSIFICATION_MODEL}")
    print(f"   Detección de Piezas: {ModelsConfig.DETECTION_PARTS_MODEL}")
    print(f"   Detección de Defectos: {ModelsConfig.DETECTION_DEFECTOS_MODEL}")
    print(f"   Segmentación de Defectos: {ModelsConfig.SEGMENTATION_DEFECTOS_MODEL}")
    print(f"   Segmentación de Piezas: {ModelsConfig.SEGMENTATION_PARTS_MODEL}")
    
    # Mostrar configuración de inferencia
    print("\n⚙️ Inferencia:")
    print(f"   Tamaño de entrada: {ModelsConfig.INPUT_SIZE}x{ModelsConfig.INPUT_SIZE}")
    print(f"   Umbral de confianza: {ModelsConfig.CONFIDENCE_THRESHOLD}")
    print(f"   Máximo detecciones: {ModelsConfig.MAX_DETECTIONS}")
    
    # Mostrar directorios
    print("\n📁 Directorios:")
    print(f"   Salida: {FileConfig.OUTPUT_DIR}")
    print(f"   Modelos: {ModelsConfig.MODELS_DIR}")
    
    input("\nPresiona ENTER para continuar...")


def procesar_comando_robustez(sistema):
    """Maneja la configuración de robustez."""
    print("\n🔧 CONFIGURACIÓN DE ROBUSTEZ")
    print("="*50)
    
    while True:
        print("\nOpciones de robustez:")
        print("  1. Configuración Original (conf=0.55, iou=0.35)")
        print("  2. Configuración Moderada (conf=0.3, iou=0.2) - RECOMENDADA")
        print("  3. Configuración Permisiva (conf=0.1, iou=0.1)")
        print("  4. Configuración Ultra Permisiva (conf=0.01, iou=0.01)")
        print("  5. Configuración Automática (basada en iluminación)")
        print("  6. Ver configuración actual")
        print("  7. Volver al menú principal")
        
        opcion = input("\nSelecciona una opción (1-7): ").strip()
        
        if opcion == "1":
            print("\n🔧 Aplicando configuración original...")
            sistema.sistema_integrado.aplicar_configuracion_robustez("original")
            print("✅ Configuración original aplicada")
            
        elif opcion == "2":
            print("\n🔧 Aplicando configuración moderada...")
            sistema.sistema_integrado.aplicar_configuracion_robustez("moderada")
            print("✅ Configuración moderada aplicada")
            
        elif opcion == "3":
            print("\n🔧 Aplicando configuración permisiva...")
            sistema.sistema_integrado.aplicar_configuracion_robustez("permisiva")
            print("✅ Configuración permisiva aplicada")
            
        elif opcion == "4":
            print("\n🔧 Aplicando configuración ultra permisiva...")
            sistema.sistema_integrado.aplicar_configuracion_robustez("ultra_permisiva")
            print("✅ Configuración ultra permisiva aplicada")
            
        elif opcion == "5":
            print("\n🔧 Configurando robustez automáticamente...")
            sistema.sistema_integrado.configurar_robustez_automatica()
            print("✅ Configuración automática aplicada")
            
        elif opcion == "6":
            print("\n📊 Configuración actual de robustez:")
            if sistema.sistema_integrado.detector_piezas:
                print(f"   Detector de Piezas:")
                print(f"     Confianza mínima: {sistema.sistema_integrado.detector_piezas.confianza_min}")
                print(f"     IoU threshold: {sistema.sistema_integrado.detector_piezas.decoder.iou_threshold}")
            if sistema.sistema_integrado.detector_defectos:
                print(f"   Detector de Defectos:")
                print(f"     Confianza mínima: {sistema.sistema_integrado.detector_defectos.confianza_min}")
                print(f"     IoU threshold: {sistema.sistema_integrado.detector_defectos.decoder.iou_threshold}")
            
        elif opcion == "7":
            break
            
        else:
            print("❌ Opción no válida")
        
        input("\nPresiona ENTER para continuar...")


def procesar_comando_fusion(sistema):
    """Maneja la configuración de fusión de máscaras."""
    print("\n🔗 CONFIGURACIÓN DE FUSIÓN DE MÁSCARAS")
    print("="*50)
    
    while True:
        print("\nOpciones de fusión:")
        print("  1. Configuración Conservadora (dist=20px, overlap=20%)")
        print("  2. Configuración Moderada (dist=30px, overlap=10%) - RECOMENDADA")
        print("  3. Configuración Agresiva (dist=50px, overlap=5%)")
        print("  4. Configuración Personalizada")
        print("  5. Ver configuración actual")
        print("  6. Probar fusión con datos de ejemplo")
        print("  7. Volver al menú principal")
        
        opcion = input("\nSelecciona una opción (1-7): ").strip()
        
        if opcion == "1":
            print("\n🔧 Aplicando configuración conservadora...")
            if hasattr(sistema, 'procesador_segmentacion_piezas') and sistema.procesador_segmentacion_piezas:
                sistema.procesador_segmentacion_piezas.fusionador.configurar_parametros(
                    distancia_maxima=20, overlap_minimo=0.2, area_minima_fusion=200
                )
                print("✅ Configuración conservadora aplicada")
            else:
                print("❌ Procesador de segmentación no disponible")
            
        elif opcion == "2":
            print("\n🔧 Aplicando configuración moderada...")
            if hasattr(sistema, 'procesador_segmentacion_piezas') and sistema.procesador_segmentacion_piezas:
                sistema.procesador_segmentacion_piezas.fusionador.configurar_parametros(
                    distancia_maxima=30, overlap_minimo=0.1, area_minima_fusion=100
                )
                print("✅ Configuración moderada aplicada")
            else:
                print("❌ Procesador de segmentación no disponible")
            
        elif opcion == "3":
            print("\n🔧 Aplicando configuración agresiva...")
            if hasattr(sistema, 'procesador_segmentacion_piezas') and sistema.procesador_segmentacion_piezas:
                sistema.procesador_segmentacion_piezas.fusionador.configurar_parametros(
                    distancia_maxima=50, overlap_minimo=0.05, area_minima_fusion=50
                )
                print("✅ Configuración agresiva aplicada")
            else:
                print("❌ Procesador de segmentación no disponible")
            
        elif opcion == "4":
            print("\n🔧 Configuración personalizada:")
            try:
                dist = float(input("   Distancia máxima (píxeles): "))
                overlap = float(input("   Overlap mínimo (0.0-1.0): "))
                area = int(input("   Área mínima de fusión (píxeles): "))
                
                if hasattr(sistema, 'procesador_segmentacion_piezas') and sistema.procesador_segmentacion_piezas:
                    sistema.procesador_segmentacion_piezas.fusionador.configurar_parametros(
                        distancia_maxima=dist, overlap_minimo=overlap, area_minima_fusion=area
                    )
                    print("✅ Configuración personalizada aplicada")
                else:
                    print("❌ Procesador de segmentación no disponible")
            except ValueError:
                print("❌ Valores inválidos")
            
        elif opcion == "5":
            print("\n📊 Configuración actual de fusión:")
            if hasattr(sistema, 'procesador_segmentacion_piezas') and sistema.procesador_segmentacion_piezas:
                stats = sistema.procesador_segmentacion_piezas.fusionador.obtener_estadisticas()
                print(f"   Distancia máxima: {stats['distancia_maxima']}px")
                print(f"   Overlap mínimo: {stats['overlap_minimo']:.2%}")
                print(f"   Área mínima de fusión: {stats['area_minima_fusion']}px")
            else:
                print("❌ Procesador de segmentación no disponible")
            
        elif opcion == "6":
            print("\n🧪 Ejecutando prueba de fusión...")
            try:
                import subprocess
                result = subprocess.run(['python', 'test_fusion_simple.py'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print("✅ Prueba de fusión completada exitosamente")
                    print("📁 Revisa las imágenes generadas: test_mascaras_*.jpg")
                else:
                    print(f"❌ Error en prueba: {result.stderr}")
            except Exception as e:
                print(f"❌ Error ejecutando prueba: {e}")
            
        elif opcion == "7":
            break
            
        else:
            print("❌ Opción no válida")
        
        input("\nPresiona ENTER para continuar...")


if __name__ == "__main__":
    main()
