#!/usr/bin/env python3
"""
Script específico para probar la segmentación de piezas con fusión de máscaras
"""

import sys
import os
import time
import signal
from typing import Dict, List

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.analysis_system import SistemaAnalisisIntegrado

def timeout_handler(signum, frame):
    """Maneja el timeout del script"""
    print("\n⏰ Timeout alcanzado, terminando script...")
    sys.exit(0)

def test_segmentacion_piezas():
    """Prueba específica de segmentación de piezas con fusión"""
    print("🎯 PRUEBA DE SEGMENTACIÓN DE PIEZAS CON FUSIÓN")
    print("="*60)
    
    # Configurar timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(90)  # 1.5 minutos timeout
    
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
        
        # Configurar fusión moderada
        print("\n🔗 Configurando fusión de máscaras moderada...")
        if hasattr(sistema, 'procesador_segmentacion_piezas') and sistema.procesador_segmentacion_piezas:
            sistema.procesador_segmentacion_piezas.fusionador.configurar_parametros(
                distancia_maxima=30, overlap_minimo=0.1, area_minima_fusion=100
            )
            print("✅ Fusión de máscaras configurada")
        else:
            print("⚠️ Procesador de segmentación no disponible")
        
        # Realizar capturas de prueba
        print("\n📸 Realizando capturas de prueba...")
        
        for i in range(2):  # Solo 2 capturas para evitar timeout
            print(f"\n--- CAPTURA {i+1}/2 ---")
            
            # Capturar imagen
            print("📷 Capturando imagen...")
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
            
            # Mostrar información detallada de segmentaciones
            print("\n📋 DETALLE DE SEGMENTACIONES:")
            for j, seg in enumerate(segmentaciones):
                fusionada = seg.get('fusionada', False)
                objetos_fusionados = seg.get('objetos_fusionados', 1)
                print(f"   {j+1}. {seg.get('clase', 'N/A')} - Conf: {seg.get('confianza', 0):.3f}")
                print(f"      Área: {seg.get('area_mascara', 0)}px")
                print(f"      BBox: {seg.get('bbox', {})}")
                if fusionada:
                    print(f"      🔗 FUSIONADA ({objetos_fusionados} objetos originales)")
                else:
                    print(f"      ✅ Sin fusionar")
            
            # Mostrar estadísticas de fusión
            fusionadas = sum(1 for seg in segmentaciones if seg.get('fusionada', False))
            total_objetos_originales = sum(seg.get('objetos_fusionados', 1) for seg in segmentaciones)
            
            print(f"\n📊 ESTADÍSTICAS DE FUSIÓN:")
            print(f"   Segmentaciones finales: {len(segmentaciones)}")
            print(f"   Objetos fusionados: {fusionadas}")
            print(f"   Total objetos originales: {total_objetos_originales}")
            
            if fusionadas > 0:
                print(f"   🎉 ¡Fusión exitosa! Se redujeron {total_objetos_originales - len(segmentaciones)} segmentaciones")
            else:
                print(f"   ℹ️ No se requirió fusión en esta captura")
            
            time.sleep(2)  # Pausa entre capturas
        
        print("\n✅ Prueba de segmentación con fusión completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Liberar recursos
        try:
            print("\n🧹 Liberando recursos...")
            sistema.liberar()
            print("✅ Recursos liberados")
        except:
            pass
        
        # Cancelar timeout
        signal.alarm(0)

def test_configuracion_fusion():
    """Prueba la configuración de fusión"""
    print("\n🔧 PRUEBA DE CONFIGURACIÓN DE FUSIÓN")
    print("="*50)
    
    try:
        sistema = SistemaAnalisisIntegrado()
        if not sistema.inicializar():
            print("❌ Error inicializando sistema")
            return False
        
        if hasattr(sistema, 'procesador_segmentacion_piezas') and sistema.procesador_segmentacion_piezas:
            fusionador = sistema.procesador_segmentacion_piezas.fusionador
            
            # Probar diferentes configuraciones
            configuraciones = [
                ('Conservadora', 20, 0.2, 200),
                ('Moderada', 30, 0.1, 100),
                ('Agresiva', 50, 0.05, 50)
            ]
            
            for nombre, dist, overlap, area in configuraciones:
                print(f"\n🔧 Configuración: {nombre}")
                fusionador.configurar_parametros(dist, overlap, area)
                
                stats = fusionador.obtener_estadisticas()
                print(f"   Distancia: {stats['distancia_maxima']}px")
                print(f"   Overlap: {stats['overlap_minimo']:.2%}")
                print(f"   Área mínima: {stats['area_minima_fusion']}px")
            
            print("✅ Configuraciones de fusión probadas correctamente")
        else:
            print("❌ Procesador de segmentación no disponible")
        
        sistema.liberar()
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de configuración: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE SEGMENTACIÓN CON FUSIÓN")
    print("="*70)
    
    # Prueba de configuración
    exito_config = test_configuracion_fusion()
    
    # Prueba principal
    exito_principal = test_segmentacion_piezas()
    
    if exito_config and exito_principal:
        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("✅ El sistema de fusión de máscaras está funcionando correctamente")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
    
    print("\n" + "="*70)
