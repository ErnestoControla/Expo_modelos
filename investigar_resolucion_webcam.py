#!/usr/bin/env python3
"""
Script para investigar la resolución nativa real de la webcam
"""

import cv2
import numpy as np

def investigar_resoluciones_webcam():
    """Investiga todas las resoluciones disponibles en la webcam"""
    print("🔍 INVESTIGANDO RESOLUCIONES NATIVAS DE WEBCAM")
    print("=" * 60)
    
    # Detectar webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ No se pudo abrir la webcam")
        return
    
    print("📷 Webcam detectada en dispositivo 0")
    
    # Resoluciones comunes a probar
    resoluciones_comunes = [
        (320, 240, "QVGA"),
        (640, 480, "VGA"),
        (800, 600, "SVGA"),
        (1024, 768, "XGA"),
        (1280, 720, "HD 720p"),
        (1280, 960, "SXGA"),
        (1600, 1200, "UXGA"),
        (1920, 1080, "Full HD 1080p"),
        (2560, 1440, "QHD"),
        (3840, 2160, "4K UHD")
    ]
    
    print("\n🧪 PROBANDO RESOLUCIONES COMUNES:")
    print("-" * 50)
    
    resoluciones_funcionando = []
    
    for width, height, nombre in resoluciones_comunes:
        print(f"🔧 Probando {nombre} ({width}x{height}):")
        
        # Intentar configurar la resolución
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Leer un frame para verificar
        ret, frame = cap.read()
        
        if ret and frame is not None:
            # Obtener resolución real
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"   ✅ Funciona: {actual_width}x{actual_height}")
            resoluciones_funcionando.append((actual_width, actual_height, nombre))
            
            # Guardar imagen de prueba para las resoluciones más altas
            if actual_width >= 1280:
                filename = f"test_resolucion_{actual_width}x{actual_height}.jpg"
                cv2.imwrite(filename, frame)
                print(f"   💾 Imagen guardada: {filename}")
        else:
            print(f"   ❌ No funciona")
    
    cap.release()
    
    print(f"\n📊 RESUMEN DE RESOLUCIONES FUNCIONANDO:")
    print("-" * 50)
    for width, height, nombre in resoluciones_funcionando:
        print(f"   ✅ {nombre}: {width}x{height}")
    
    if resoluciones_funcionando:
        # Encontrar la resolución más alta
        max_res = max(resoluciones_funcionando, key=lambda x: x[0] * x[1])
        print(f"\n🎯 RESOLUCIÓN MÁS ALTA DISPONIBLE:")
        print(f"   📐 {max_res[2]}: {max_res[0]}x{max_res[1]}")
        print(f"   📊 Píxeles totales: {max_res[0] * max_res[1]:,}")
        
        return max_res
    else:
        print("\n❌ No se encontraron resoluciones funcionando")
        return None

def probar_capabilities_webcam():
    """Prueba las capacidades específicas de la webcam"""
    print("\n🔧 INVESTIGANDO CAPACIDADES DE LA WEBCAM")
    print("=" * 60)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ No se pudo abrir la webcam")
        return
    
    # Información básica
    print("📷 INFORMACIÓN BÁSICA:")
    print(f"   Backend: {cap.getBackendName()}")
    print(f"   API: {cap.get(cv2.CAP_PROP_BACKEND)}")
    
    # Propiedades de resolución
    print("\n📐 PROPIEDADES DE RESOLUCIÓN:")
    propiedades_resolucion = [
        (cv2.CAP_PROP_FRAME_WIDTH, "Ancho"),
        (cv2.CAP_PROP_FRAME_HEIGHT, "Alto"),
        (cv2.CAP_PROP_FRAME_COUNT, "Frames totales"),
        (cv2.CAP_PROP_FPS, "FPS"),
        (cv2.CAP_PROP_FOURCC, "Codec"),
        (cv2.CAP_PROP_FORMAT, "Formato"),
        (cv2.CAP_PROP_MODE, "Modo"),
        (cv2.CAP_PROP_BRIGHTNESS, "Brillo"),
        (cv2.CAP_PROP_CONTRAST, "Contraste"),
        (cv2.CAP_PROP_SATURATION, "Saturación"),
        (cv2.CAP_PROP_HUE, "Tono"),
        (cv2.CAP_PROP_GAIN, "Ganancia"),
        (cv2.CAP_PROP_EXPOSURE, "Exposición"),
        (cv2.CAP_PROP_AUTO_EXPOSURE, "Auto exposición"),
        (cv2.CAP_PROP_AUTOFOCUS, "Auto enfoque"),
        (cv2.CAP_PROP_FOCUS, "Enfoque"),
        (cv2.CAP_PROP_ZOOM, "Zoom"),
        (cv2.CAP_PROP_PAN, "Pan"),
        (cv2.CAP_PROP_TILT, "Tilt"),
        (cv2.CAP_PROP_ROLL, "Roll"),
        (cv2.CAP_PROP_IRIS, "Iris"),
        (cv2.CAP_PROP_SETTINGS, "Configuración")
    ]
    
    for prop, nombre in propiedades_resolucion:
        try:
            valor = cap.get(prop)
            if valor != -1:  # -1 indica que la propiedad no está soportada
                print(f"   {nombre}: {valor}")
        except:
            pass
    
    cap.release()

def probar_resoluciones_especificas():
    """Prueba resoluciones específicas paso a paso"""
    print("\n🎯 PROBANDO RESOLUCIONES ESPECÍFICAS")
    print("=" * 60)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ No se pudo abrir la webcam")
        return
    
    # Configurar a la resolución más alta posible
    print("🔧 Configurando a resolución máxima...")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # Leer varios frames para estabilizar
    for i in range(5):
        ret, frame = cap.read()
        if not ret:
            print(f"❌ Error en frame {i+1}")
            break
    
    if ret and frame is not None:
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✅ Resolución establecida: {actual_width}x{actual_height}")
        print(f"📊 Dimensiones del frame: {frame.shape}")
        
        # Guardar imagen de alta resolución
        filename = f"webcam_alta_resolucion_{actual_width}x{actual_height}.jpg"
        cv2.imwrite(filename, frame)
        print(f"💾 Imagen guardada: {filename}")
        
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
        
        # Verificar si la imagen está muy oscura o borrosa
        if mean_brightness < 50:
            print("   ⚠️ Imagen muy oscura")
        elif mean_brightness > 200:
            print("   ⚠️ Imagen muy brillante")
        else:
            print("   ✅ Brillo normal")
            
        if std_brightness < 20:
            print("   ⚠️ Imagen posiblemente borrosa (baja variación)")
        else:
            print("   ✅ Variación normal")
    
    cap.release()

def main():
    """Función principal"""
    print("🚀 INVESTIGACIÓN COMPLETA DE RESOLUCIÓN DE WEBCAM")
    print("=" * 70)
    
    # 1. Investigar resoluciones comunes
    max_res = investigar_resoluciones_webcam()
    
    # 2. Probar capacidades de la webcam
    probar_capabilities_webcam()
    
    # 3. Probar resoluciones específicas
    probar_resoluciones_especificas()
    
    print("\n🏁 INVESTIGACIÓN COMPLETADA")
    if max_res:
        print(f"🎯 RECOMENDACIÓN: Usar resolución {max_res[0]}x{max_res[1]} ({max_res[2]})")
        print(f"   Esta es la resolución más alta disponible en tu webcam")
    else:
        print("❌ No se pudo determinar la resolución óptima")

if __name__ == "__main__":
    main()
