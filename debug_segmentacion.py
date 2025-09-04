#!/usr/bin/env python3
"""
Script de debugging para segmentación de piezas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.segmentation.segmentation_piezas_engine import SegmentadorPiezasCoples
from modules.camera.camera_engine import CamaraTiempoOptimizada
import numpy as np

def main():
    print("🔍 DEBUGGING SEGMENTACIÓN DE PIEZAS")
    print("=" * 50)
    
    try:
        # Inicializar cámara
        print("📷 Inicializando cámara...")
        camara = CamaraTiempoOptimizada()
        camara.inicializar()
        
        # Inicializar segmentador
        print("🧠 Inicializando segmentador...")
        segmentador = SegmentadorPiezasCoples()
        
        # Configurar filtros permisivos
        print("🔧 Configurando filtros permisivos...")
        segmentador.modo_debug_extremo()
        
        # Capturar imagen
        print("📸 Capturando imagen...")
        frame = camara.capturar_frame()
        if frame is None:
            print("❌ Error capturando imagen")
            return
        
        print(f"✅ Imagen capturada: {frame.shape}")
        
        # Realizar segmentación
        print("🎯 Realizando segmentación...")
        segmentaciones = segmentador.segmentar(frame)
        
        print(f"✅ Segmentación completada: {len(segmentaciones)} resultados")
        
        # Mostrar resultados
        for i, seg in enumerate(segmentaciones):
            print(f"\n📊 Segmentación {i+1}:")
            print(f"   Clase: {seg['clase']}")
            print(f"   Confianza: {seg['confianza']:.3f}")
            print(f"   BBox: {seg['bbox']}")
            print(f"   Área máscara: {seg['area_mascara']}")
            print(f"   Dimensiones: {seg['ancho_mascara']}x{seg['alto_mascara']}")
            print(f"   Centroide: {seg['centroide']}")
        
        # Liberar recursos
        camara.liberar()
        print("✅ Recursos liberados")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
