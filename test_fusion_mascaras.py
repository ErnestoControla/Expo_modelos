#!/usr/bin/env python3
"""
Script de prueba para el sistema de fusión de máscaras
"""

import sys
import os
import time
import signal
from typing import Dict, List

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.analysis_system import SistemaAnalisisIntegrado
from modules.postprocessing.mask_fusion import FusionadorMascaras

def timeout_handler(signum, frame):
    """Maneja el timeout del script"""
    print("\n⏰ Timeout alcanzado, terminando script...")
    sys.exit(0)

def test_fusion_mascaras():
    """Prueba el sistema de fusión de máscaras"""
    print("🔗 PRUEBA DE FUSIÓN DE MÁSCARAS")
    print("="*50)
    
    # Configurar timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(120)  # 2 minutos timeout
    
    try:
        # Inicializar sistema
        print("🚀 Inicializando sistema...")
        sistema = SistemaAnalisisIntegrado()
        
        if not sistema.inicializar():
            print("❌ Error inicializando sistema")
            return False
        
        print("✅ Sistema inicializado correctamente")
        
        # Configurar robustez moderada
        print("\n🔧 Configurando robustez moderada...")
        sistema.aplicar_configuracion_robustez("moderada")
        
        # Realizar capturas de prueba
        print("\n📸 Realizando capturas de prueba...")
        
        for i in range(3):
            print(f"\n--- CAPTURA {i+1}/3 ---")
            
            # Capturar imagen
            resultado = sistema.capturar_imagen_unica()
            if resultado.get('error'):
                print(f"❌ Error capturando imagen: {resultado['error']}")
                continue
            
            imagen = resultado.get('imagen')
            if imagen is None:
                print("❌ No se pudo obtener la imagen del resultado")
                continue
            print(f"✅ Imagen capturada: {imagen.shape}")
            
            # Realizar segmentación de piezas
            print("🎯 Realizando segmentación de piezas...")
            resultado_seg = sistema.ejecutar_segmentacion_piezas(imagen)
            
            if resultado_seg.get('error'):
                print(f"❌ Error en segmentación: {resultado_seg['error']}")
                continue
            
            segmentaciones = resultado_seg.get('segmentaciones', [])
            print(f"✅ Segmentaciones encontradas: {len(segmentaciones)}")
            
            # Mostrar información de segmentaciones
            for j, seg in enumerate(segmentaciones):
                print(f"   {j+1}. {seg.get('clase', 'N/A')} - Conf: {seg.get('confianza', 0):.3f}")
                if 'mascara' in seg and seg['mascara'] is not None:
                    area = int(seg.get('area_mascara', 0))
                    print(f"      Área: {area}px")
            
            # Probar fusión de máscaras manualmente
            if len(segmentaciones) > 1:
                print("\n🔗 Probando fusión de máscaras...")
                fusionador = FusionadorMascaras()
                
                # Configurar parámetros más agresivos para la prueba
                fusionador.configurar_parametros(
                    distancia_maxima=30,  # Más cercano
                    overlap_minimo=0.05,  # Más permisivo
                    area_minima_fusion=50  # Más pequeño
                )
                
                segmentaciones_fusionadas = fusionador.procesar_segmentaciones(segmentaciones)
                
                print(f"   📊 Resultado: {len(segmentaciones)} → {len(segmentaciones_fusionadas)} segmentaciones")
                
                # Mostrar información de segmentaciones fusionadas
                for j, seg in enumerate(segmentaciones_fusionadas):
                    fusionada = seg.get('fusionada', False)
                    objetos_fusionados = seg.get('objetos_fusionados', 1)
                    print(f"   {j+1}. {seg.get('clase', 'N/A')} - Conf: {seg.get('confianza', 0):.3f}")
                    if fusionada:
                        print(f"      🔗 FUSIONADA ({objetos_fusionados} objetos)")
                    if 'mascara' in seg and seg['mascara'] is not None:
                        area = int(seg.get('area_mascara', 0))
                        print(f"      Área: {area}px")
            else:
                print("   ℹ️ Solo una segmentación, no se requiere fusión")
            
            time.sleep(1)  # Pausa entre capturas
        
        print("\n✅ Prueba de fusión de máscaras completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False
    
    finally:
        # Liberar recursos
        try:
            print("\n🧹 Liberando recursos...")
            sistema.liberar_recursos()
            print("✅ Recursos liberados")
        except:
            pass
        
        # Cancelar timeout
        signal.alarm(0)

def test_configuraciones_fusion():
    """Prueba diferentes configuraciones de fusión"""
    print("\n🔧 PRUEBA DE CONFIGURACIONES DE FUSIÓN")
    print("="*50)
    
    fusionador = FusionadorMascaras()
    
    # Configuraciones a probar
    configuraciones = [
        {
            'nombre': 'Conservadora',
            'distancia_maxima': 20,
            'overlap_minimo': 0.2,
            'area_minima_fusion': 200
        },
        {
            'nombre': 'Moderada',
            'distancia_maxima': 30,
            'overlap_minimo': 0.1,
            'area_minima_fusion': 100
        },
        {
            'nombre': 'Agresiva',
            'distancia_maxima': 50,
            'overlap_minimo': 0.05,
            'area_minima_fusion': 50
        }
    ]
    
    for config in configuraciones:
        print(f"\n🔧 Configuración: {config['nombre']}")
        fusionador.configurar_parametros(
            distancia_maxima=config['distancia_maxima'],
            overlap_minimo=config['overlap_minimo'],
            area_minima_fusion=config['area_minima_fusion']
        )
        
        stats = fusionador.obtener_estadisticas()
        print(f"   Distancia máxima: {stats['distancia_maxima']}px")
        print(f"   Overlap mínimo: {stats['overlap_minimo']:.2%}")
        print(f"   Área mínima: {stats['area_minima_fusion']}px")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE FUSIÓN DE MÁSCARAS")
    print("="*60)
    
    # Prueba de configuraciones
    test_configuraciones_fusion()
    
    # Prueba principal
    exito = test_fusion_mascaras()
    
    if exito:
        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
    
    print("\n" + "="*60)
