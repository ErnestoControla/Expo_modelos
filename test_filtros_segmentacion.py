#!/usr/bin/env python3
"""
Script de prueba para demostrar los filtros de calidad de segmentación de piezas
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from modules.segmentation.segmentation_piezas_engine import SegmentadorPiezasCoples

def mostrar_filtros_actuales(segmentador):
    """Muestra los filtros actuales del segmentador"""
    print("\n🔧 FILTROS ACTUALES:")
    print("=" * 50)
    filtros = segmentador.obtener_filtros_actuales()
    for nombre, valor in filtros.items():
        print(f"   {nombre}: {valor}")
    print("=" * 50)

def probar_configuracion_estricta(segmentador):
    """Prueba configuración estricta para piezas grandes"""
    print("\n🎯 CONFIGURACIÓN ESTRICTA (Piezas Grandes):")
    print("-" * 50)
    
    segmentador.configurar_filtros(
        min_area_mascara=5000,      # Mínimo 5000 píxeles
        min_ancho_mascara=50,       # Mínimo 50 píxeles de ancho
        min_alto_mascara=50,        # Mínimo 50 píxeles de alto
        min_area_bbox=1000,         # Mínimo 1000 píxeles en BBox
        min_cobertura_bbox=0.5,     # Mínimo 50% de cobertura
        min_densidad_mascara=0.2,   # Mínimo 20% de densidad
        max_ratio_aspecto=5.0       # Máximo ratio 5:1
    )

def probar_configuracion_permisiva(segmentador):
    """Prueba configuración permisiva para piezas pequeñas"""
    print("\n🎯 CONFIGURACIÓN PERMISIVA (Piezas Pequeñas):")
    print("-" * 50)
    
    segmentador.configurar_filtros(
        min_area_mascara=500,       # Mínimo 500 píxeles
        min_ancho_mascara=15,       # Mínimo 15 píxeles de ancho
        min_alto_mascara=15,        # Mínimo 15 píxeles de alto
        min_area_bbox=200,          # Mínimo 200 píxeles en BBox
        min_cobertura_bbox=0.2,     # Mínimo 20% de cobertura
        min_densidad_mascara=0.05,  # Mínimo 5% de densidad
        max_ratio_aspecto=15.0      # Máximo ratio 15:1
    )

def probar_configuracion_defectos(segmentador):
    """Prueba configuración para detectar defectos pequeños"""
    print("\n🎯 CONFIGURACIÓN PARA DEFECTOS:")
    print("-" * 50)
    
    segmentador.configurar_filtros(
        min_area_mascara=100,       # Mínimo 100 píxeles
        min_ancho_mascara=10,       # Mínimo 10 píxeles de ancho
        min_alto_mascara=10,        # Mínimo 10 píxeles de alto
        min_area_bbox=50,           # Mínimo 50 píxeles en BBox
        min_cobertura_bbox=0.1,     # Mínimo 10% de cobertura
        min_densidad_mascara=0.02,  # Mínimo 2% de densidad
        max_ratio_aspecto=20.0      # Máximo ratio 20:1
    )

def main():
    """Función principal de prueba"""
    print("🧪 PRUEBA DE FILTROS DE SEGMENTACIÓN DE PIEZAS")
    print("=" * 60)
    
    try:
        # Crear segmentador
        print("🚀 Inicializando segmentador...")
        segmentador = SegmentadorPiezasCoples()
        
        if not segmentador.stats['inicializado']:
            print("❌ Error: Segmentador no inicializado")
            return
        
        # Mostrar configuración inicial
        mostrar_filtros_actuales(segmentador)
        
        # Probar diferentes configuraciones
        probar_configuracion_estricta(segmentador)
        mostrar_filtros_actuales(segmentador)
        
        probar_configuracion_permisiva(segmentador)
        mostrar_filtros_actuales(segmentador)
        
        probar_configuracion_defectos(segmentador)
        mostrar_filtros_actuales(segmentador)
        
        # Restaurar configuración por defecto
        print("\n🔄 RESTAURANDO CONFIGURACIÓN POR DEFECTO:")
        print("-" * 50)
        segmentador.configurar_filtros(
            min_area_mascara=2000,
            min_ancho_mascara=30,
            min_alto_mascara=30,
            min_area_bbox=500,
            min_cobertura_bbox=0.4,
            min_densidad_mascara=0.1,
            max_ratio_aspecto=10.0
        )
        mostrar_filtros_actuales(segmentador)
        
        print("\n✅ Prueba de filtros completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
    
    finally:
        # Liberar recursos
        if 'segmentador' in locals():
            segmentador.liberar()

if __name__ == "__main__":
    main()
