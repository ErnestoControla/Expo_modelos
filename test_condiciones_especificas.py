#!/usr/bin/env python3
"""
Script para probar configuraciones en condiciones específicas de iluminación
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.analysis_system import SistemaAnalisisIntegrado
import numpy as np
import cv2
import time
import json
from datetime import datetime

class PruebaCondicionesEspecificas:
    """
    Prueba configuraciones en diferentes condiciones de iluminación
    """
    
    def __init__(self):
        self.sistema = None
        self.resultados = []
        
    def inicializar(self):
        """Inicializa el sistema"""
        print("🚀 Inicializando sistema...")
        self.sistema = SistemaAnalisisIntegrado()
        
        if not self.sistema.inicializar():
            print("❌ Error inicializando sistema")
            return False
        
        print("✅ Sistema inicializado correctamente")
        return True
    
    def clasificar_condiciones(self, brightness: float, contrast: float) -> str:
        """Clasifica las condiciones de iluminación"""
        if brightness < 60:
            return "Muy Oscuro"
        elif brightness < 100:
            return "Oscuro"
        elif brightness < 150:
            return "Normal"
        elif brightness < 200:
            return "Brillante"
        else:
            return "Muy Brillante"
    
    def obtener_configuracion_recomendada(self, brightness: float, contrast: float) -> dict:
        """Obtiene configuración recomendada basándose en las condiciones"""
        condiciones = self.clasificar_condiciones(brightness, contrast)
        
        configuraciones = {
            "Muy Oscuro": {
                "confianza_min": 0.01,
                "iou_threshold": 0.01,
                "usar_preprocesamiento": True,
                "descripcion": "Condiciones muy oscuras - umbrales ultra permisivos"
            },
            "Oscuro": {
                "confianza_min": 0.1,
                "iou_threshold": 0.05,
                "usar_preprocesamiento": True,
                "descripcion": "Condiciones oscuras - umbrales permisivos"
            },
            "Normal": {
                "confianza_min": 0.3,
                "iou_threshold": 0.2,
                "usar_preprocesamiento": False,
                "descripcion": "Condiciones normales - umbrales moderados"
            },
            "Brillante": {
                "confianza_min": 0.4,
                "iou_threshold": 0.3,
                "usar_preprocesamiento": False,
                "descripcion": "Condiciones brillantes - umbrales moderados-altos"
            },
            "Muy Brillante": {
                "confianza_min": 0.5,
                "iou_threshold": 0.35,
                "usar_preprocesamiento": False,
                "descripcion": "Condiciones muy brillantes - umbrales altos"
            }
        }
        
        return configuraciones.get(condiciones, configuraciones["Normal"])
    
    def probar_en_condiciones_actuales(self):
        """Prueba en las condiciones actuales de iluminación"""
        print("\n📸 Capturando imagen en condiciones actuales...")
        frame = self.sistema.camara.capturar_frame()
        
        if frame is None:
            print("❌ Error capturando imagen")
            return
        
        # Analizar condiciones
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        condiciones = self.clasificar_condiciones(brightness, contrast)
        config_recomendada = self.obtener_configuracion_recomendada(brightness, contrast)
        
        print(f"\n📊 Condiciones detectadas:")
        print(f"   Brillo: {brightness:.1f}")
        print(f"   Contraste: {contrast:.1f}")
        print(f"   Clasificación: {condiciones}")
        print(f"   Configuración recomendada: {config_recomendada['descripcion']}")
        
        # Probar configuración recomendada
        print(f"\n🔧 Probando configuración recomendada...")
        resultado = self._probar_configuracion(
            "Recomendada para " + condiciones,
            config_recomendada,
            frame
        )
        
        # Probar también configuración original para comparar
        print(f"\n🔧 Probando configuración original para comparar...")
        config_original = {
            "confianza_min": 0.55,
            "iou_threshold": 0.35,
            "usar_preprocesamiento": False,
            "descripcion": "Configuración original"
        }
        resultado_original = self._probar_configuracion(
            "Original",
            config_original,
            frame
        )
        
        # Mostrar comparación
        print(f"\n📊 COMPARACIÓN DE RESULTADOS:")
        print(f"   Configuración recomendada: {resultado['num_detecciones']} detecciones")
        print(f"   Configuración original: {resultado_original['num_detecciones']} detecciones")
        
        if resultado['num_detecciones'] > resultado_original['num_detecciones']:
            print(f"   ✅ La configuración recomendada es MEJOR")
        elif resultado['num_detecciones'] == resultado_original['num_detecciones']:
            print(f"   ⚖️ Ambas configuraciones tienen el mismo rendimiento")
        else:
            print(f"   ⚠️ La configuración original es mejor")
        
        return {
            'condiciones': {
                'brightness': brightness,
                'contrast': contrast,
                'clasificacion': condiciones
            },
            'resultado_recomendado': resultado,
            'resultado_original': resultado_original
        }
    
    def _probar_configuracion(self, nombre: str, config: dict, imagen: np.ndarray) -> dict:
        """Prueba una configuración específica"""
        try:
            # Aplicar configuración
            self.sistema.detector_piezas.actualizar_umbrales(
                confianza_min=config['confianza_min'],
                iou_threshold=config['iou_threshold']
            )
            
            # Aplicar preprocesamiento si se solicita
            if config.get('usar_preprocesamiento', False):
                imagen_procesada, metrics = self.sistema.preprocesar_imagen_robusta(imagen)
            else:
                imagen_procesada = imagen
            
            # Realizar detección
            tiempo_inicio = time.time()
            detecciones = self.sistema.detector_piezas.detectar_piezas(imagen_procesada)
            tiempo_deteccion = (time.time() - tiempo_inicio) * 1000  # ms
            
            # Analizar resultados
            num_detecciones = len(detecciones)
            confianzas = [det.get('confianza', 0) for det in detecciones]
            
            resultado = {
                'nombre': nombre,
                'configuracion': config,
                'num_detecciones': num_detecciones,
                'tiempo_deteccion_ms': tiempo_deteccion,
                'confianza_promedio': np.mean(confianzas) if confianzas else 0,
                'confianza_minima': np.min(confianzas) if confianzas else 0,
                'confianza_maxima': np.max(confianzas) if confianzas else 0,
                'detecciones': detecciones
            }
            
            print(f"   ✅ {nombre}: {num_detecciones} detecciones, tiempo: {tiempo_deteccion:.1f}ms")
            if confianzas:
                print(f"      Confianza: {np.mean(confianzas):.3f} (min: {np.min(confianzas):.3f}, max: {np.max(confianzas):.3f})")
            
            return resultado
            
        except Exception as e:
            print(f"   ❌ Error en {nombre}: {e}")
            return {
                'nombre': nombre,
                'error': str(e),
                'num_detecciones': 0
            }
    
    def probar_multiples_capturas(self, num_capturas: int = 5):
        """Prueba múltiples capturas para evaluar consistencia"""
        print(f"\n🔄 Probando {num_capturas} capturas para evaluar consistencia...")
        
        resultados = []
        
        for i in range(num_capturas):
            print(f"\n--- CAPTURA {i+1}/{num_capturas} ---")
            
            # Capturar imagen
            frame = self.sistema.camara.capturar_frame()
            if frame is None:
                print("❌ Error capturando imagen")
                continue
            
            # Analizar condiciones
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            condiciones = self.clasificar_condiciones(brightness, contrast)
            config_recomendada = self.obtener_configuracion_recomendada(brightness, contrast)
            
            print(f"   Brillo: {brightness:.1f}, Contraste: {contrast:.1f} - {condiciones}")
            
            # Probar configuración recomendada
            resultado = self._probar_configuracion(
                f"Captura {i+1}",
                config_recomendada,
                frame
            )
            
            resultados.append({
                'captura': i+1,
                'condiciones': {
                    'brightness': brightness,
                    'contrast': contrast,
                    'clasificacion': condiciones
                },
                'resultado': resultado
            })
            
            # Esperar un poco entre capturas
            time.sleep(1)
        
        # Analizar consistencia
        detecciones_por_captura = [r['resultado']['num_detecciones'] for r in resultados]
        detecciones_promedio = np.mean(detecciones_por_captura)
        detecciones_std = np.std(detecciones_por_captura)
        
        print(f"\n📊 ANÁLISIS DE CONSISTENCIA:")
        print(f"   Detecciones promedio: {detecciones_promedio:.1f}")
        print(f"   Desviación estándar: {detecciones_std:.1f}")
        print(f"   Rango: {np.min(detecciones_por_captura)} - {np.max(detecciones_por_captura)}")
        
        if detecciones_std < 1.0:
            print(f"   ✅ CONSISTENCIA ALTA - El sistema es estable")
        elif detecciones_std < 2.0:
            print(f"   ⚠️ CONSISTENCIA MEDIA - El sistema es moderadamente estable")
        else:
            print(f"   ❌ CONSISTENCIA BAJA - El sistema es inestable")
        
        return resultados
    
    def ejecutar(self):
        """Ejecuta las pruebas de condiciones específicas"""
        print("🧪 PRUEBAS DE CONDICIONES ESPECÍFICAS DE ILUMINACIÓN")
        print("=" * 60)
        
        if not self.inicializar():
            return
        
        try:
            # Prueba en condiciones actuales
            resultado_actual = self.probar_en_condiciones_actuales()
            
            # Preguntar si hacer múltiples capturas
            respuesta = input("\n¿Quieres probar múltiples capturas para evaluar consistencia? (s/n): ").lower().strip()
            
            if respuesta.startswith('s'):
                num_capturas = int(input("¿Cuántas capturas? (default: 5): ") or "5")
                resultados_multiples = self.probar_multiples_capturas(num_capturas)
                
                # Guardar resultados
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"resultados_condiciones_{timestamp}.json"
                
                datos_completos = {
                    'resultado_actual': resultado_actual,
                    'resultados_multiples': resultados_multiples,
                    'timestamp': timestamp
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(datos_completos, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Resultados guardados en: {filename}")
            
        except KeyboardInterrupt:
            print("\n👋 Pruebas interrumpidas por el usuario")
        except Exception as e:
            print(f"❌ Error en las pruebas: {e}")
        finally:
            # Liberar recursos
            self.sistema.liberar()
            print("✅ Recursos liberados")

def main():
    """Función principal"""
    prueba = PruebaCondicionesEspecificas()
    prueba.ejecutar()

if __name__ == "__main__":
    main()
