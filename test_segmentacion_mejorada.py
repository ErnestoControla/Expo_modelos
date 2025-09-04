#!/usr/bin/env python3
"""
Script para probar la segmentación de piezas mejorada con debugging
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from modules.segmentation.segmentation_piezas_engine import SegmentadorPiezasCoples
from modules.capture import CamaraTiempoOptimizada
import cv2
import numpy as np
import time

def test_segmentacion_mejorada():
    """Prueba la segmentación de piezas con mejoras implementadas"""
    
    print("🔧 PROBANDO SEGMENTACIÓN DE PIEZAS MEJORADA")
    print("=" * 60)
    
    # Inicializar cámara
    print("📷 Inicializando cámara...")
    camara = CamaraTiempoOptimizada()
    if not camara.configurar_camara():
        print("❌ Error configurando cámara")
        return
    
    # Inicializar segmentador
    print("🧠 Inicializando segmentador de piezas...")
    segmentador = SegmentadorPiezasCoples()
    
    if not segmentador.stats['inicializado']:
        print("❌ Error inicializando segmentador")
        return
    
    # Configurar modo debug extremo
    print("🔧 Configurando modo DEBUG EXTREMO...")
    segmentador.modo_debug_extremo()
    
    # Capturar imagen de prueba
    print("📷 Capturando imagen de prueba...")
    frame = camara.capturar_frame()
    if frame is None:
        print("❌ Error capturando imagen")
        return
    
    print(f"✅ Imagen capturada: {frame.shape}")
    
    # Realizar segmentación
    print("🎨 Realizando segmentación con mejoras...")
    inicio = time.time()
    
    segmentaciones = segmentador.segmentar(frame)
    
    tiempo_total = (time.time() - inicio) * 1000
    
    # Mostrar resultados
    print(f"\n🎯 RESULTADOS DE SEGMENTACIÓN MEJORADA:")
    print(f"   Tiempo total: {tiempo_total:.2f} ms")
    print(f"   Segmentaciones encontradas: {len(segmentaciones)}")
    
    for i, seg in enumerate(segmentaciones):
        bbox = seg['bbox']
        centroide = seg['centroide']
        print(f"   Segmentación #{i+1}: {seg['clase']} - {seg['confianza']:.2%}")
        print(f"     BBox: ({bbox['x1']}, {bbox['y1']}) a ({bbox['x2']}, {bbox['y2']})")
        print(f"     Centroide: ({centroide['x']}, {centroide['y']})")
        print(f"     Área: {seg['area']}")
        print(f"     Área máscara: {seg['area_mascara']}")
        print(f"     Dimensiones máscara: {seg['ancho_mascara']}x{seg['alto_mascara']}")
    
    # Guardar imagen con segmentaciones
    if len(segmentaciones) > 0:
        print("\n💾 Guardando imagen con segmentaciones...")
        
        # Crear visualización
        imagen_vis = frame.copy()
        
        for i, seg in enumerate(segmentaciones):
            bbox = seg['bbox']
            mascara = seg['mascara']
            
            # Dibujar bbox
            cv2.rectangle(imagen_vis, (bbox['x1'], bbox['y1']), (bbox['x2'], bbox['y2']), (0, 255, 0), 2)
            
            # Dibujar máscara con transparencia
            if mascara is not None:
                # Crear overlay de color
                overlay = imagen_vis.copy()
                color = (0, 255, 255)  # Amarillo
                
                # Aplicar máscara
                mask_3ch = cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR)
                overlay = overlay * (1 - mask_3ch) + np.array(color) * mask_3ch
                
                # Combinar con imagen original
                imagen_vis = cv2.addWeighted(imagen_vis, 0.7, overlay.astype(np.uint8), 0.3, 0)
            
            # Etiqueta
            label = f"{seg['clase']}: {seg['confianza']:.2%}"
            cv2.putText(imagen_vis, label, (bbox['x1'], bbox['y1']-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Guardar imagen
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_segmentacion_mejorada_{timestamp}.jpg"
        cv2.imwrite(filename, imagen_vis)
        print(f"✅ Imagen guardada: {filename}")
    
    # Limpiar recursos
    print("\n🧹 Limpiando recursos...")
    segmentador.liberar()
    camara.liberar_recursos()
    
    print("✅ Prueba completada")

if __name__ == "__main__":
    test_segmentacion_mejorada()
