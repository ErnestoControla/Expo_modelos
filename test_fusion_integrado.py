#!/usr/bin/env python3
"""
Script para probar la fusión de máscaras integrada en el procesador
"""

import sys
import os
import numpy as np
import cv2

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.segmentation.piezas_segmentation_processor import ProcesadorSegmentacionPiezas
from modules.postprocessing.mask_fusion import FusionadorMascaras

def crear_segmentaciones_prueba():
    """Crea segmentaciones de prueba que simulan objetos pegados"""
    
    # Crear imagen base
    imagen = np.zeros((640, 640, 3), dtype=np.uint8)
    
    # Crear máscaras de prueba
    mascara1 = np.zeros((640, 640), dtype=np.float32)
    cv2.circle(mascara1, (200, 200), 50, 1.0, -1)  # Círculo 1
    
    mascara2 = np.zeros((640, 640), dtype=np.float32)
    cv2.circle(mascara2, (250, 200), 50, 1.0, -1)  # Círculo 2 (pegado al primero)
    
    mascara3 = np.zeros((640, 640), dtype=np.float32)
    cv2.circle(mascara3, (400, 400), 60, 1.0, -1)  # Círculo 3 (separado)
    
    # Crear segmentaciones
    segmentaciones = [
        {
            'clase': 'Cople',
            'confianza': 0.8,
            'mascara': mascara1,
            'area_mascara': int(np.sum(mascara1 > 0.5)),
            'bbox': {'x1': 150, 'y1': 150, 'x2': 250, 'y2': 250},
            'centroide': {'x': 200, 'y': 200},
            'ancho_mascara': 100,
            'alto_mascara': 100
        },
        {
            'clase': 'Cople',
            'confianza': 0.75,
            'mascara': mascara2,
            'area_mascara': int(np.sum(mascara2 > 0.5)),
            'bbox': {'x1': 200, 'y1': 150, 'x2': 300, 'y2': 250},
            'centroide': {'x': 250, 'y': 200},
            'ancho_mascara': 100,
            'alto_mascara': 100
        },
        {
            'clase': 'Cople',
            'confianza': 0.9,
            'mascara': mascara3,
            'area_mascara': int(np.sum(mascara3 > 0.5)),
            'bbox': {'x1': 340, 'y1': 340, 'x2': 460, 'y2': 460},
            'centroide': {'x': 400, 'y': 400},
            'ancho_mascara': 120,
            'alto_mascara': 120
        }
    ]
    
    return segmentaciones, imagen

def test_procesador_integrado():
    """Prueba el procesador con fusión integrada"""
    print("🔗 PRUEBA DEL PROCESADOR CON FUSIÓN INTEGRADA")
    print("="*60)
    
    try:
        # Crear segmentaciones de prueba
        print("📝 Creando segmentaciones de prueba...")
        segmentaciones, imagen = crear_segmentaciones_prueba()
        
        print(f"✅ Creadas {len(segmentaciones)} segmentaciones de prueba")
        for i, seg in enumerate(segmentaciones):
            print(f"   {i+1}. {seg['clase']} - Conf: {seg['confianza']:.2f} - Área: {seg['area_mascara']}px")
        
        # Inicializar procesador
        print("\n🔧 Inicializando procesador de segmentación...")
        procesador = ProcesadorSegmentacionPiezas()
        
        # Verificar que el fusionador esté disponible
        if hasattr(procesador, 'fusionador'):
            print("✅ Fusionador de máscaras disponible")
            
            # Configurar fusión moderada
            procesador.fusionador.configurar_parametros(
                distancia_maxima=30, overlap_minimo=0.1, area_minima_fusion=100
            )
            print("✅ Configuración de fusión aplicada")
        else:
            print("❌ Fusionador de máscaras no disponible")
            return False
        
        # Procesar segmentaciones
        print("\n🔗 Procesando segmentaciones con fusión integrada...")
        resultado = procesador.procesar_segmentaciones(imagen, segmentaciones)
        
        if resultado.get('error'):
            print(f"❌ Error en procesamiento: {resultado['error']}")
            return False
        
        print("✅ Procesamiento completado exitosamente")
        print(f"📁 Archivos generados:")
        print(f"   - Imagen: {resultado.get('imagen', 'N/A')}")
        print(f"   - JSON: {resultado.get('json', 'N/A')}")
        print(f"   - Heatmap: {resultado.get('heatmap', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fusionador_directo():
    """Prueba el fusionador directamente"""
    print("\n🔧 PRUEBA DIRECTA DEL FUSIONADOR")
    print("="*50)
    
    try:
        # Crear segmentaciones de prueba
        segmentaciones, _ = crear_segmentaciones_prueba()
        
        # Inicializar fusionador
        fusionador = FusionadorMascaras()
        
        # Probar diferentes configuraciones
        configuraciones = [
            ('Conservadora', 20, 0.2, 200),
            ('Moderada', 30, 0.1, 100),
            ('Agresiva', 50, 0.05, 50)
        ]
        
        for nombre, dist, overlap, area in configuraciones:
            print(f"\n🔧 Configuración: {nombre}")
            fusionador.configurar_parametros(dist, overlap, area)
            
            segmentaciones_procesadas = fusionador.procesar_segmentaciones(segmentaciones)
            
            fusionadas = sum(1 for seg in segmentaciones_procesadas if seg.get('fusionada', False))
            total_originales = sum(seg.get('objetos_fusionados', 1) for seg in segmentaciones_procesadas)
            
            print(f"   Resultado: {len(segmentaciones)} → {len(segmentaciones_procesadas)} segmentaciones")
            print(f"   Fusionadas: {fusionadas}")
            print(f"   Total objetos originales: {total_originales}")
            
            if fusionadas > 0:
                print(f"   🎉 ¡Fusión exitosa! Se redujeron {total_originales - len(segmentaciones_procesadas)} segmentaciones")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba directa: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE FUSIÓN INTEGRADA")
    print("="*70)
    
    # Prueba directa del fusionador
    exito_directo = test_fusionador_directo()
    
    # Prueba del procesador integrado
    exito_integrado = test_procesador_integrado()
    
    if exito_directo and exito_integrado:
        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("✅ El sistema de fusión de máscaras está completamente integrado")
        print("✅ El procesador de segmentación funciona correctamente con fusión")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
    
    print("\n" + "="*70)
