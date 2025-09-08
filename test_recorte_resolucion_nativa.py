#!/usr/bin/env python3
"""
Script de prueba para el sistema de recorte con resolución nativa real
"""

import sys
import os
import cv2
import numpy as np

# Agregar path para imports
sys.path.append(os.path.dirname(__file__))

from modules.capture.webcam_fallback import WebcamFallback, detectar_mejor_webcam

def probar_recorte_con_resolucion_nativa():
    """Prueba el recorte con la resolución nativa real"""
    print("🧪 PROBANDO RECORTE CON RESOLUCIÓN NATIVA REAL")
    print("=" * 60)
    
    # Detectar webcam
    webcam_id = detectar_mejor_webcam()
    if webcam_id is None:
        print("❌ No se encontraron webcams disponibles")
        return
    
    print(f"📷 Usando webcam en dispositivo {webcam_id}")
    
    # Probar con recorte habilitado
    print("\n🔧 PROBANDO CON RECORTE HABILITADO:")
    print("-" * 40)
    webcam_crop = WebcamFallback(device_id=webcam_id, use_crop=True)
    if webcam_crop.inicializar():
        print("✅ Webcam con recorte inicializada")
        
        # Mostrar estadísticas
        stats = webcam_crop.obtener_estadisticas()
        print(f"📊 Estadísticas:")
        print(f"   Resolución nativa: {stats['resolucion_nativa']}")
        print(f"   Resolución objetivo: {stats['resolucion_objetivo']}")
        print(f"   Método: {stats['metodo_procesamiento']}")
        
        if stats['parametros_recorte']:
            params = stats['parametros_recorte']
            print(f"   Recorte: {params['width']}x{params['height']} desde ({params['x']}, {params['y']})")
        
        # Capturar frame
        frame, tiempo, timestamp = webcam_crop.obtener_frame_sincrono()
        if frame is not None:
            print(f"✅ Frame capturado: {frame.shape}, tiempo: {tiempo:.2f}ms")
            
            # Guardar imagen de prueba
            cv2.imwrite("test_recorte_nativo.jpg", frame)
            print("💾 Imagen guardada como 'test_recorte_nativo.jpg'")
            
            # Analizar calidad de la imagen
            print(f"\n📈 ANÁLISIS DE CALIDAD:")
            print(f"   Dimensiones: {frame.shape[1]}x{frame.shape[0]}x{frame.shape[2]}")
            print(f"   Tipo de datos: {frame.dtype}")
            print(f"   Rango de valores: {frame.min()}-{frame.max()}")
            
            # Calcular estadísticas de la imagen
            mean_brightness = np.mean(frame)
            std_brightness = np.std(frame)
            print(f"   Brillo promedio: {mean_brightness:.2f}")
            print(f"   Desviación estándar: {std_brightness:.2f}")
            
            # Verificar calidad
            if mean_brightness < 50:
                print("   ⚠️ Imagen muy oscura")
            elif mean_brightness > 200:
                print("   ⚠️ Imagen muy brillante")
            else:
                print("   ✅ Brillo normal")
                
            if std_brightness < 20:
                print("   ⚠️ Imagen posiblemente borrosa (baja variación)")
            else:
                print("   ✅ Variación normal - buena calidad")
        else:
            print("❌ Error capturando frame con recorte")
        
        webcam_crop.liberar_recursos()
    else:
        print("❌ Error inicializando webcam con recorte")

def probar_diferentes_resoluciones_objetivo():
    """Prueba diferentes resoluciones objetivo con la resolución nativa real"""
    print("\n🧪 PROBANDO DIFERENTES RESOLUCIONES OBJETIVO")
    print("=" * 60)
    
    webcam_id = detectar_mejor_webcam()
    if webcam_id is None:
        print("❌ No se encontraron webcams disponibles")
        return
    
    # Resoluciones objetivo que deberían funcionar bien con recorte
    resoluciones_objetivo = [
        (320, 320, "320x320"),
        (480, 480, "480x480"),
        (640, 640, "640x640"),
        (720, 720, "720x720"),
        (800, 600, "800x600"),
        (1024, 576, "1024x576"),  # 16:9 ratio
        (1280, 720, "1280x720")   # Resolución nativa completa
    ]
    
    for width, height, nombre in resoluciones_objetivo:
        print(f"\n🔧 Probando resolución objetivo {nombre}:")
        print("-" * 30)
        
        webcam = WebcamFallback(device_id=webcam_id, width=width, height=height, use_crop=True)
        if webcam.inicializar():
            stats = webcam.obtener_estadisticas()
            print(f"   Resolución nativa: {stats['resolucion_nativa']}")
            print(f"   Resolución objetivo: {stats['resolucion_objetivo']}")
            print(f"   Método: {stats['metodo_procesamiento']}")
            
            if stats['parametros_recorte']:
                params = stats['parametros_recorte']
                print(f"   Recorte: {params['width']}x{params['height']} desde ({params['x']}, {params['y']})")
            
            # Capturar frame
            frame, tiempo, timestamp = webcam.obtener_frame_sincrono()
            if frame is not None:
                print(f"   ✅ Frame: {frame.shape}, tiempo: {tiempo:.2f}ms")
                
                # Guardar imagen para resoluciones importantes
                if width >= 640:
                    filename = f"test_resolucion_{nombre.replace('x', 'x')}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"   💾 Imagen guardada: {filename}")
            else:
                print(f"   ❌ Error capturando frame")
            
            webcam.liberar_recursos()
        else:
            print(f"   ❌ Error inicializando webcam")

def probar_sistema_integrado_mejorado():
    """Prueba el sistema integrado con la resolución nativa mejorada"""
    print("\n🧪 PROBANDO SISTEMA INTEGRADO MEJORADO")
    print("=" * 60)
    
    try:
        from modules.analysis_system import SistemaAnalisisIntegrado
        
        sistema = SistemaAnalisisIntegrado()
        
        print("🚀 Inicializando sistema...")
        if sistema.inicializar():
            print("✅ Sistema inicializado correctamente")
            
            # Verificar tipo de cámara y resolución
            if sistema.usando_webcam:
                print("📷 Sistema usando webcam como fallback")
                
                # Mostrar estadísticas de webcam
                stats = sistema.obtener_estadisticas()
                if stats['camara']:
                    cam_stats = stats['camara']
                    print(f"   Resolución nativa: {cam_stats.get('resolucion_nativa', 'N/A')}")
                    print(f"   Resolución objetivo: {cam_stats.get('resolucion_objetivo', 'N/A')}")
                    print(f"   Método: {cam_stats.get('metodo_procesamiento', 'N/A')}")
                    
                    parametros_recorte = cam_stats.get('parametros_recorte')
                    if parametros_recorte:
                        print(f"   Recorte: {parametros_recorte['width']}x{parametros_recorte['height']} desde ({parametros_recorte['x']}, {parametros_recorte['y']})")
            else:
                print("📷 Sistema usando cámara GigE")
            
            # Probar captura
            print("📸 Probando captura...")
            resultado = sistema.capturar_imagen_unica()
            
            if "error" not in resultado:
                print("✅ Captura exitosa")
                frame = resultado["frame"]
                print(f"   Dimensiones: {frame.shape}")
                print(f"   Tiempo captura: {resultado['tiempos']['captura_ms']:.2f}ms")
                
                # Guardar imagen de prueba
                cv2.imwrite("test_sistema_mejorado.jpg", frame)
                print("💾 Imagen guardada como 'test_sistema_mejorado.jpg'")
                
                # Analizar calidad
                mean_brightness = np.mean(frame)
                std_brightness = np.std(frame)
                print(f"   Brillo promedio: {mean_brightness:.2f}")
                print(f"   Desviación estándar: {std_brightness:.2f}")
                
                if std_brightness > 20:
                    print("   ✅ Buena calidad de imagen")
                else:
                    print("   ⚠️ Imagen posiblemente borrosa")
            else:
                print(f"❌ Error en captura: {resultado['error']}")
            
            # Liberar recursos
            sistema.liberar()
            print("✅ Recursos liberados")
            
            return True
        else:
            print("❌ Error inicializando sistema")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba del sistema: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 PRUEBA DEL SISTEMA DE RECORTE CON RESOLUCIÓN NATIVA REAL")
    print("=" * 70)
    
    # 1. Probar recorte con resolución nativa
    probar_recorte_con_resolucion_nativa()
    
    # 2. Probar diferentes resoluciones objetivo
    probar_diferentes_resoluciones_objetivo()
    
    # 3. Probar sistema integrado mejorado
    probar_sistema_integrado_mejorado()
    
    print("\n🏁 PRUEBAS COMPLETADAS")
    print("📁 Imágenes de prueba guardadas:")
    print("   - test_recorte_nativo.jpg (recorte con resolución nativa)")
    print("   - test_resolucion_*.jpg (diferentes resoluciones objetivo)")
    print("   - test_sistema_mejorado.jpg (sistema completo mejorado)")

if __name__ == "__main__":
    main()
