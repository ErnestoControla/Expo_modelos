"""
Sistema de Análisis de Coples - Aplicación Principal
Integra módulos de captura y clasificación para análisis automático de coples
"""

import cv2
import time
import os
import numpy as np

# Importar módulos propios
from config import GlobalConfig, FileConfig
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
        
        return self.camara.obtener_frame_instantaneo()
    
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
    print("🎯 ANÁLISIS DISPONIBLE:")
    print("="*60)
    print("  1. Análisis Completo (Clasificación + Detección de Piezas + Defectos)")
    print("  2. Solo Clasificación")
    print("  3. Solo Detección de Piezas")
    print("  4. Solo Detección de Defectos")
    print("  5. Solo Ver Frame")
    print("  6. Estadísticas del Sistema")
    print("  7. Configuración")
    print("  8. Salir del Sistema")
    print("="*60)
    print("  ENTER - Opción 1 (Análisis Completo)")
    print("  '2'   - Solo Clasificación")
    print("  '3'   - Solo Detección de Piezas")
    print("  '4'   - Solo Detección de Defectos")
    print("  'v'   - Solo Ver Frame")
    print("  's'   - Estadísticas")
    print("  'c'   - Configuración")
    print("  'q'   - Salir")
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
    
    # Mostrar tiempos
    if "tiempos" in resultados:
        tiempos = resultados["tiempos"]
        print(f"\n⏱️  TIEMPOS:")
        print(f"   Captura:      {tiempos.get('captura_ms', 0):.2f} ms")
        print(f"   Clasificación: {tiempos.get('clasificacion_ms', 0):.2f} ms")
        print(f"   Detección Piezas: {tiempos.get('deteccion_piezas_ms', 0):.2f} ms")
        print(f"   Detección Defectos: {tiempos.get('deteccion_defectos_ms', 0):.2f} ms")
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
    if "detecciones" in resultados:
        detecciones = resultados["detecciones"]
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
    if "frame" in resultados and "detecciones" in resultados:
        frame = resultados["frame"]
        detecciones = resultados["detecciones"]
        
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
        
        # Mostrar frame
        cv2.imshow(ventana_cv, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
    else:
        print("⚠️ No hay frames disponibles")
    
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
                sistema.mostrar_configuracion()
            
            elif entrada == 't':
                procesar_comando_umbral(sistema)
            
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
            
            elif entrada == 'help' or entrada == 'h':
                mostrar_menu()
            
            else:
                print("❓ Comando no reconocido. Escribe 'help' para ver opciones.")
    
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


if __name__ == "__main__":
    main()
