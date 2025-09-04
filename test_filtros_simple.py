#!/usr/bin/env python3
"""
Script simplificado para probar diferentes configuraciones de filtros en segmentación de piezas
Usa una imagen estática en lugar de la cámara
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from modules.segmentation.segmentation_piezas_engine import SegmentadorPiezasCoples
import cv2
import numpy as np
import time

def crear_imagen_prueba():
    """Crea una imagen de prueba simple"""
    # Crear imagen de 640x640 con fondo gris
    imagen = np.full((640, 640, 3), 128, dtype=np.uint8)
    
    # Agregar algunos rectángulos que simulen piezas
    cv2.rectangle(imagen, (100, 100), (300, 200), (255, 255, 255), -1)  # Rectángulo blanco
    cv2.rectangle(imagen, (400, 300), (550, 450), (200, 200, 200), -1)  # Rectángulo gris
    
    # Agregar algunos círculos
    cv2.circle(imagen, (200, 400), 50, (180, 180, 180), -1)
    cv2.circle(imagen, (500, 150), 30, (220, 220, 220), -1)
    
    return imagen

def probar_configuracion_filtros():
    """Prueba diferentes configuraciones de filtros para segmentación de piezas"""
    
    print("🔧 PROBANDO DIFERENTES CONFIGURACIONES DE FILTROS")
    print("=" * 60)
    
    # Crear imagen de prueba
    print("🖼️ Creando imagen de prueba...")
    frame = crear_imagen_prueba()
    print(f"✅ Imagen creada: {frame.shape}")
    
    # Guardar imagen de prueba
    cv2.imwrite("imagen_prueba_segmentacion.jpg", frame)
    print("💾 Imagen guardada como 'imagen_prueba_segmentacion.jpg'")
    
    # Configuraciones a probar
    configuraciones = [
        {
            "nombre": "MUY PERMISIVO",
            "confianza_min": 0.3,
            "min_area_mascara": 100,
            "min_ancho_mascara": 10,
            "min_alto_mascara": 10,
            "min_area_bbox": 100,
            "min_cobertura_bbox": 0.1,
            "min_densidad_mascara": 0.01,
            "max_ratio_aspecto": 20.0
        },
        {
            "nombre": "PERMISIVO",
            "confianza_min": 0.4,
            "min_area_mascara": 500,
            "min_ancho_mascara": 20,
            "min_alto_mascara": 20,
            "min_area_bbox": 200,
            "min_cobertura_bbox": 0.2,
            "min_densidad_mascara": 0.05,
            "max_ratio_aspecto": 15.0
        },
        {
            "nombre": "MODERADO",
            "confianza_min": 0.5,
            "min_area_mascara": 1000,
            "min_ancho_mascara": 25,
            "min_alto_mascara": 25,
            "min_area_bbox": 300,
            "min_cobertura_bbox": 0.3,
            "min_densidad_mascara": 0.08,
            "max_ratio_aspecto": 12.0
        },
        {
            "nombre": "ACTUAL (RESTRICTIVO)",
            "confianza_min": 0.6,
            "min_area_mascara": 2000,
            "min_ancho_mascara": 30,
            "min_alto_mascara": 30,
            "min_area_bbox": 500,
            "min_cobertura_bbox": 0.4,
            "min_densidad_mascara": 0.1,
            "max_ratio_aspecto": 10.0
        }
    ]
    
    # Probar cada configuración
    for i, config in enumerate(configuraciones):
        print(f"\n{'='*60}")
        print(f"🧪 CONFIGURACIÓN {i+1}: {config['nombre']}")
        print(f"{'='*60}")
        
        # Mostrar configuración
        print("📋 Parámetros:")
        for key, value in config.items():
            if key != "nombre":
                print(f"   {key}: {value}")
        
        # Inicializar segmentador con nueva configuración
        try:
            segmentador = SegmentadorPiezasCoples(confianza_min=config['confianza_min'])
            
            # Configurar filtros
            filtros = {k: v for k, v in config.items() if k != 'nombre' and k != 'confianza_min'}
            segmentador.configurar_filtros(**filtros)
            
            # Realizar segmentación
            print(f"\n🎨 Ejecutando segmentación...")
            tiempo_inicio = time.time()
            segmentaciones = segmentador.segmentar(frame)
            tiempo_total = (time.time() - tiempo_inicio) * 1000
            
            # Mostrar resultados
            print(f"\n📊 RESULTADOS:")
            print(f"   Tiempo: {tiempo_total:.2f} ms")
            print(f"   Segmentaciones encontradas: {len(segmentaciones)}")
            
            if segmentaciones:
                for j, seg in enumerate(segmentaciones):
                    print(f"   Segmentación #{j+1}:")
                    print(f"     Clase: {seg['clase']}")
                    print(f"     Confianza: {seg['confianza']:.3f}")
                    print(f"     BBox: ({seg['bbox']['x1']}, {seg['bbox']['y1']}) a ({seg['bbox']['x2']}, {seg['bbox']['y2']})")
                    print(f"     Área BBox: {seg['area']}")
                    print(f"     Área Máscara: {seg['area_mascara']}")
                    print(f"     Dimensiones: {seg['ancho_mascara']}x{seg['alto_mascara']}")
                    print(f"     Centroide: ({seg['centroide']['x']}, {seg['centroide']['y']})")
            else:
                print("   ❌ No se encontraron segmentaciones")
            
            # Liberar recursos
            segmentador.liberar()
            
        except Exception as e:
            print(f"❌ Error en configuración {config['nombre']}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Pruebas completadas")

def mostrar_filtros_actuales():
    """Muestra los filtros actuales del segmentador"""
    print("📋 FILTROS ACTUALES DEL SEGMENTADOR DE PIEZAS")
    print("=" * 50)
    
    try:
        segmentador = SegmentadorPiezasCoples()
        filtros = segmentador.obtener_filtros_actuales()
        
        for key, value in filtros.items():
            print(f"   {key}: {value}")
        
        segmentador.liberar()
        
    except Exception as e:
        print(f"❌ Error obteniendo filtros: {e}")

if __name__ == "__main__":
    print("🔧 HERRAMIENTA DE CONFIGURACIÓN DE FILTROS DE SEGMENTACIÓN DE PIEZAS")
    print("=" * 70)
    
    while True:
        print("\nOpciones:")
        print("1. Mostrar filtros actuales")
        print("2. Probar diferentes configuraciones")
        print("3. Salir")
        
        opcion = input("\nSelecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            mostrar_filtros_actuales()
        elif opcion == "2":
            probar_configuracion_filtros()
        elif opcion == "3":
            print("👋 Saliendo...")
            break
        else:
            print("❌ Opción no válida")
