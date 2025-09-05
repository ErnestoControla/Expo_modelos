#!/usr/bin/env python3
"""
Script de prueba para robustez ante cambios de iluminación
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.analysis_system import SistemaAnalisisIntegrado
from modules.preprocessing.illumination_robust import RobustezIluminacion
from modules.adaptive_thresholds import UmbralesAdaptativos
import numpy as np
import cv2
import time

def main():
    print("🔍 PRUEBA DE ROBUSTEZ ANTE CAMBIOS DE ILUMINACIÓN")
    print("=" * 60)
    
    try:
        # Inicializar sistema
        print("🚀 Inicializando sistema...")
        sistema = SistemaAnalisisIntegrado()
        
        if not sistema.inicializar():
            print("❌ Error inicializando sistema")
            return
        
        print("✅ Sistema inicializado correctamente")
        
        # Realizar múltiples capturas para probar robustez
        print("\n📸 Realizando capturas de prueba...")
        
        for i in range(5):
            print(f"\n--- CAPTURA {i+1}/5 ---")
            
            # Capturar imagen
            frame = sistema.camara.capturar_frame()
            if frame is None:
                print("❌ Error capturando imagen")
                continue
            
            print(f"✅ Imagen capturada: {frame.shape}")
            
            # Aplicar preprocesamiento robusto
            frame_robusto, metrics = sistema.preprocesar_imagen_robusta(frame)
            
            # Obtener umbrales adaptativos
            umbrales = sistema.obtener_umbrales_adaptativos(metrics)
            
            # Realizar detección con umbrales adaptativos
            print("🎯 Realizando detección con umbrales adaptativos...")
            
            # Configurar umbrales en el detector
            sistema.detector_piezas.confianza_min = umbrales['confianza_min']
            
            # Realizar detección
            detecciones = sistema.detector_piezas.detectar_piezas(frame_robusto)
            
            print(f"✅ Detecciones encontradas: {len(detecciones)}")
            
            # Mostrar métricas de iluminación
            print(f"📊 Métricas de iluminación:")
            print(f"   Brillo: {metrics.get('brightness', 0):.1f}")
            print(f"   Contraste: {metrics.get('contrast', 0):.1f}")
            print(f"   Rango dinámico: {metrics.get('dynamic_range', 0):.1f}")
            print(f"   Entropía: {metrics.get('entropy', 0):.3f}")
            
            # Mostrar umbrales utilizados
            print(f"🎯 Umbrales adaptativos:")
            print(f"   Confianza: {umbrales['confianza_min']:.3f}")
            print(f"   Área mínima: {umbrales['area_minima']:.0f}")
            print(f"   Cobertura mínima: {umbrales['cobertura_minima']:.3f}")
            
            # Esperar un poco entre capturas
            time.sleep(2)
        
        # Mostrar estadísticas finales
        print("\n📊 ESTADÍSTICAS FINALES")
        print("=" * 40)
        
        stats_robustez = sistema.robustez_iluminacion.obtener_estadisticas_iluminacion()
        stats_umbrales = sistema.umbrales_adaptativos.obtener_estadisticas()
        
        print("🔧 Estadísticas de robustez:")
        if stats_robustez:
            print(f"   Brillo promedio: {stats_robustez.get('brightness_mean', 0):.1f}")
            print(f"   Contraste promedio: {stats_robustez.get('contrast_mean', 0):.1f}")
            print(f"   Muestras analizadas: {stats_robustez.get('samples', 0)}")
        
        print("\n🎯 Estadísticas de umbrales:")
        if stats_umbrales:
            print(f"   Historial de detecciones: {stats_umbrales.get('detection_history_size', 0)}")
            print(f"   Historial de iluminación: {stats_umbrales.get('illumination_history_size', 0)}")
        
        # Liberar recursos
        sistema.liberar()
        print("\n✅ Prueba de robustez completada")
        
    except Exception as e:
        print(f"❌ Error en prueba de robustez: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
