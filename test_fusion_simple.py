#!/usr/bin/env python3
"""
Script simple para probar la fusión de máscaras
"""

import sys
import os
import numpy as np
import cv2

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.postprocessing.mask_fusion import FusionadorMascaras

def crear_mascaras_prueba():
    """Crea máscaras de prueba para simular objetos pegados"""
    
    # Crear imagen base
    imagen = np.zeros((640, 640), dtype=np.float32)
    
    # Crear dos círculos que se tocan (objetos pegados)
    cv2.circle(imagen, (200, 200), 50, 1.0, -1)  # Círculo 1
    cv2.circle(imagen, (250, 200), 50, 1.0, -1)  # Círculo 2 (pegado al primero)
    
    # Crear un círculo separado
    cv2.circle(imagen, (400, 400), 60, 1.0, -1)  # Círculo 3 (separado)
    
    # Crear máscaras individuales
    mascara1 = np.zeros((640, 640), dtype=np.float32)
    cv2.circle(mascara1, (200, 200), 50, 1.0, -1)
    
    mascara2 = np.zeros((640, 640), dtype=np.float32)
    cv2.circle(mascara2, (250, 200), 50, 1.0, -1)
    
    mascara3 = np.zeros((640, 640), dtype=np.float32)
    cv2.circle(mascara3, (400, 400), 60, 1.0, -1)
    
    # Crear segmentaciones de prueba
    segmentaciones = [
        {
            'clase': 'Cople',
            'confianza': 0.8,
            'mascara': mascara1,
            'area_mascara': int(np.sum(mascara1 > 0.5)),
            'bbox': {'x1': 150, 'y1': 150, 'x2': 250, 'y2': 250},
            'centroide': {'x': 200, 'y': 200}
        },
        {
            'clase': 'Cople',
            'confianza': 0.75,
            'mascara': mascara2,
            'area_mascara': int(np.sum(mascara2 > 0.5)),
            'bbox': {'x1': 200, 'y1': 150, 'x2': 300, 'y2': 250},
            'centroide': {'x': 250, 'y': 200}
        },
        {
            'clase': 'Cople',
            'confianza': 0.9,
            'mascara': mascara3,
            'area_mascara': int(np.sum(mascara3 > 0.5)),
            'bbox': {'x1': 340, 'y1': 340, 'x2': 460, 'y2': 460},
            'centroide': {'x': 400, 'y': 400}
        }
    ]
    
    return segmentaciones, imagen

def test_fusion_simple():
    """Prueba simple de fusión de máscaras"""
    print("🔗 PRUEBA SIMPLE DE FUSIÓN DE MÁSCARAS")
    print("="*50)
    
    try:
        # Crear máscaras de prueba
        print("📝 Creando máscaras de prueba...")
        segmentaciones, imagen_base = crear_mascaras_prueba()
        
        print(f"✅ Creadas {len(segmentaciones)} segmentaciones de prueba")
        for i, seg in enumerate(segmentaciones):
            print(f"   {i+1}. {seg['clase']} - Conf: {seg['confianza']:.2f} - Área: {seg['area_mascara']}px")
        
        # Inicializar fusionador
        print("\n🔧 Inicializando fusionador...")
        fusionador = FusionadorMascaras()
        
        # Configurar parámetros moderados
        fusionador.configurar_parametros(
            distancia_maxima=30,
            overlap_minimo=0.1,
            area_minima_fusion=100
        )
        
        print("✅ Fusionador inicializado")
        
        # Procesar segmentaciones
        print("\n🔗 Procesando segmentaciones...")
        segmentaciones_procesadas = fusionador.procesar_segmentaciones(segmentaciones)
        
        # Mostrar resultados
        print(f"\n📊 RESULTADOS:")
        print(f"   Segmentaciones originales: {len(segmentaciones)}")
        print(f"   Segmentaciones procesadas: {len(segmentaciones_procesadas)}")
        
        print(f"\n📋 DETALLE DE SEGMENTACIONES PROCESADAS:")
        for i, seg in enumerate(segmentaciones_procesadas):
            fusionada = seg.get('fusionada', False)
            objetos_fusionados = seg.get('objetos_fusionados', 1)
            print(f"   {i+1}. {seg['clase']} - Conf: {seg['confianza']:.2f} - Área: {seg['area_mascara']}px")
            if fusionada:
                print(f"      🔗 FUSIONADA ({objetos_fusionados} objetos originales)")
            else:
                print(f"      ✅ Sin fusionar")
        
        # Crear visualización
        print("\n🎨 Creando visualización...")
        imagen_visualizacion = np.zeros((640, 640, 3), dtype=np.uint8)
        
        # Dibujar máscaras originales en rojo
        for seg in segmentaciones:
            mascara = seg['mascara']
            imagen_visualizacion[mascara > 0.5] = [0, 0, 255]  # Rojo
        
        # Dibujar máscaras procesadas en verde
        imagen_procesada = np.zeros((640, 640, 3), dtype=np.uint8)
        for seg in segmentaciones_procesadas:
            mascara = seg['mascara']
            if seg.get('fusionada', False):
                imagen_procesada[mascara > 0.5] = [0, 255, 0]  # Verde para fusionadas
            else:
                imagen_procesada[mascara > 0.5] = [255, 0, 0]  # Azul para no fusionadas
        
        # Guardar imágenes
        cv2.imwrite('test_mascaras_originales.jpg', imagen_visualizacion)
        cv2.imwrite('test_mascaras_procesadas.jpg', imagen_procesada)
        
        print("✅ Imágenes guardadas:")
        print("   - test_mascaras_originales.jpg (rojo)")
        print("   - test_mascaras_procesadas.jpg (verde=fusionadas, azul=no fusionadas)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_diferentes_configuraciones():
    """Prueba diferentes configuraciones de fusión"""
    print("\n🔧 PRUEBA DE DIFERENTES CONFIGURACIONES")
    print("="*50)
    
    # Crear máscaras de prueba
    segmentaciones, _ = crear_mascaras_prueba()
    
    configuraciones = [
        ('Conservadora', 20, 0.2, 200),
        ('Moderada', 30, 0.1, 100),
        ('Agresiva', 50, 0.05, 50)
    ]
    
    for nombre, dist, overlap, area in configuraciones:
        print(f"\n🔧 Configuración: {nombre}")
        print(f"   Distancia: {dist}px, Overlap: {overlap:.1%}, Área mín: {area}px")
        
        fusionador = FusionadorMascaras()
        fusionador.configurar_parametros(dist, overlap, area)
        
        segmentaciones_procesadas = fusionador.procesar_segmentaciones(segmentaciones)
        
        fusionadas = sum(1 for seg in segmentaciones_procesadas if seg.get('fusionada', False))
        print(f"   Resultado: {len(segmentaciones)} → {len(segmentaciones_procesadas)} segmentaciones")
        print(f"   Fusionadas: {fusionadas}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS SIMPLES DE FUSIÓN")
    print("="*60)
    
    # Prueba principal
    exito = test_fusion_simple()
    
    # Prueba de configuraciones
    test_diferentes_configuraciones()
    
    if exito:
        print("\n🎉 PRUEBAS COMPLETADAS EXITOSAMENTE")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
    
    print("\n" + "="*60)
