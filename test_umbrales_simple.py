#!/usr/bin/env python3
"""
Script de prueba simple con umbrales extremos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.analysis_system import SistemaAnalisisIntegrado
import numpy as np
import cv2
import time

def main():
    print("🔍 PRUEBA SIMPLE CON UMBRALES EXTREMOS")
    print("=" * 50)
    
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
        sistema.detector_piezas.actualizar_umbrales(confianza_min=0.01, iou_threshold=0.01)
        
        # Realizar captura
        print("\n📸 Capturando imagen...")
        frame = sistema.camara.capturar_frame()
        if frame is None:
            print("❌ Error capturando imagen")
            return
        
        print(f"✅ Imagen capturada: {frame.shape}")
        
        # Analizar iluminación simple
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        print(f"\n📊 Métricas de iluminación:")
        print(f"   Brillo: {brightness:.1f}")
        print(f"   Contraste: {contrast:.1f}")
        
        # Realizar detección con umbrales extremos
        print("\n🎯 Realizando detección con umbrales extremos...")
        print(f"   Confianza mínima: {sistema.detector_piezas.confianza_min}")
        print(f"   IoU threshold: {sistema.detector_piezas.decoder.iou_threshold}")
        
        detecciones = sistema.detector_piezas.detectar_piezas(frame)
        
        print(f"\n✅ Detecciones encontradas: {len(detecciones)}")
        
        if detecciones:
            for i, det in enumerate(detecciones):
                print(f"   Detección {i+1}:")
                print(f"      Clase: {det.get('clase', 'N/A')}")
                print(f"      Confianza: {det.get('confianza', 0):.4f}")
                print(f"      BBox: {det.get('bbox', {})}")
        else:
            print("   ⚠️ No se encontraron detecciones")
            
            # Mostrar información del decoder
            print("\n🔍 Información del decoder:")
            print(f"   Confianza mínima configurada: {sistema.detector_piezas.decoder.confianza_min}")
            print(f"   IoU threshold configurado: {sistema.detector_piezas.decoder.iou_threshold}")
        
        # Liberar recursos
        sistema.liberar()
        print("\n✅ Prueba completada")
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
