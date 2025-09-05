#!/usr/bin/env python3
"""
Script de prueba con umbrales extremadamente permisivos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.analysis_system import SistemaAnalisisIntegrado
import numpy as np
import cv2
import time

def main():
    print("🔍 PRUEBA CON UMBRALES EXTREMADAMENTE PERMISIVOS")
    print("=" * 60)
    
    try:
        # Inicializar sistema
        print("🚀 Inicializando sistema...")
        sistema = SistemaAnalisisIntegrado()
        
        if not sistema.inicializar():
            print("❌ Error inicializando sistema")
            return
        
        print("✅ Sistema inicializado correctamente")
        
        # Configurar umbrales extremadamente permisivos
        print("\n🔧 Configurando umbrales extremos...")
        sistema.detector_piezas.confianza_min = 0.1  # Muy permisivo
        sistema.detector_piezas.iou_threshold = 0.1  # Muy permisivo
        
        # Realizar captura
        print("\n📸 Capturando imagen...")
        frame = sistema.camara.capturar_frame()
        if frame is None:
            print("❌ Error capturando imagen")
            return
        
        print(f"✅ Imagen capturada: {frame.shape}")
        
        # Aplicar preprocesamiento robusto
        frame_robusto, metrics = sistema.preprocesar_imagen_robusta(frame)
        
        # Mostrar métricas
        print(f"\n📊 Métricas de iluminación:")
        print(f"   Brillo: {metrics.get('brightness', 0):.1f}")
        print(f"   Contraste: {metrics.get('contrast', 0):.1f}")
        print(f"   Rango dinámico: {metrics.get('dynamic_range', 0):.1f}")
        print(f"   Entropía: {metrics.get('entropy', 0):.3f}")
        
        # Realizar detección con umbrales extremos
        print("\n🎯 Realizando detección con umbrales extremos...")
        print(f"   Confianza mínima: {sistema.detector_piezas.confianza_min}")
        print(f"   IoU threshold: {sistema.detector_piezas.iou_threshold}")
        
        detecciones = sistema.detector_piezas.detectar_piezas(frame_robusto)
        
        print(f"\n✅ Detecciones encontradas: {len(detecciones)}")
        
        if detecciones:
            for i, det in enumerate(detecciones):
                print(f"   Detección {i+1}:")
                print(f"      Clase: {det.get('clase', 'N/A')}")
                print(f"      Confianza: {det.get('confianza', 0):.4f}")
                print(f"      BBox: {det.get('bbox', {})}")
        else:
            print("   ⚠️ No se encontraron detecciones")
            
            # Intentar con umbrales aún más extremos
            print("\n🔧 Probando con umbrales ULTRA extremos...")
            sistema.detector_piezas.confianza_min = 0.01  # Ultra permisivo
            sistema.detector_piezas.iou_threshold = 0.01  # Ultra permisivo
            
            detecciones_ultra = sistema.detector_piezas.detectar_piezas(frame_robusto)
            print(f"   Detecciones ultra: {len(detecciones_ultra)}")
            
            if detecciones_ultra:
                for i, det in enumerate(detecciones_ultra):
                    print(f"      Ultra {i+1}: conf={det.get('confianza', 0):.4f}")
        
        # Liberar recursos
        sistema.liberar()
        print("\n✅ Prueba completada")
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
