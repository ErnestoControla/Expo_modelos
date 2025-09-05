#!/usr/bin/env python3
"""
Script interactivo para probar configuraciones de robustez
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.analysis_system import SistemaAnalisisIntegrado
import numpy as np
import cv2
import time

class PruebaInteractivaRobustez:
    """
    Prueba interactiva de configuraciones de robustez
    """
    
    def __init__(self):
        self.sistema = None
        self.imagen_actual = None
        
    def inicializar(self):
        """Inicializa el sistema"""
        print("🚀 Inicializando sistema...")
        self.sistema = SistemaAnalisisIntegrado()
        
        if not self.sistema.inicializar():
            print("❌ Error inicializando sistema")
            return False
        
        print("✅ Sistema inicializado correctamente")
        return True
    
    def capturar_nueva_imagen(self):
        """Captura una nueva imagen"""
        print("📸 Capturando nueva imagen...")
        self.imagen_actual = self.sistema.camara.capturar_frame()
        
        if self.imagen_actual is None:
            print("❌ Error capturando imagen")
            return False
        
        print(f"✅ Imagen capturada: {self.imagen_actual.shape}")
        
        # Analizar iluminación
        gray = cv2.cvtColor(self.imagen_actual, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        print(f"📊 Condiciones de iluminación:")
        print(f"   Brillo: {brightness:.1f}")
        print(f"   Contraste: {contrast:.1f}")
        
        return True
    
    def probar_configuracion(self, confianza_min: float, iou_threshold: float = 0.35, usar_preprocesamiento: bool = False):
        """Prueba una configuración específica"""
        if self.imagen_actual is None:
            print("❌ No hay imagen capturada. Usa 'c' para capturar una nueva imagen.")
            return
        
        print(f"\n🔧 Probando configuración:")
        print(f"   Confianza mínima: {confianza_min}")
        print(f"   IoU threshold: {iou_threshold}")
        print(f"   Preprocesamiento: {'Sí' if usar_preprocesamiento else 'No'}")
        
        try:
            # Aplicar configuración
            self.sistema.detector_piezas.actualizar_umbrales(
                confianza_min=confianza_min,
                iou_threshold=iou_threshold
            )
            
            # Aplicar preprocesamiento si se solicita
            if usar_preprocesamiento:
                imagen_procesada, metrics = self.sistema.preprocesar_imagen_robusta(self.imagen_actual)
                print(f"   📊 Métricas post-procesamiento: Brillo={metrics.get('brightness', 0):.1f}, Contraste={metrics.get('contrast', 0):.1f}")
            else:
                imagen_procesada = self.imagen_actual
            
            # Realizar detección
            tiempo_inicio = time.time()
            detecciones = self.sistema.detector_piezas.detectar_piezas(imagen_procesada)
            tiempo_deteccion = (time.time() - tiempo_inicio) * 1000  # ms
            
            # Mostrar resultados
            print(f"\n✅ Resultados:")
            print(f"   Detecciones encontradas: {len(detecciones)}")
            print(f"   Tiempo de detección: {tiempo_deteccion:.1f}ms")
            
            if detecciones:
                confianzas = [det.get('confianza', 0) for det in detecciones]
                areas = [det.get('area', 0) for det in detecciones]
                
                print(f"   Confianza promedio: {np.mean(confianzas):.3f}")
                print(f"   Confianza mínima: {np.min(confianzas):.3f}")
                print(f"   Confianza máxima: {np.max(confianzas):.3f}")
                print(f"   Área promedio: {np.mean(areas):.0f} píxeles")
                
                print(f"\n   Detalles de detecciones:")
                for i, det in enumerate(detecciones):
                    print(f"      {i+1}. {det.get('clase', 'N/A')} - Conf: {det.get('confianza', 0):.3f} - BBox: {det.get('bbox', {})}")
            else:
                print("   ⚠️ No se encontraron detecciones")
                
        except Exception as e:
            print(f"❌ Error en la prueba: {e}")
    
    def mostrar_menu(self):
        """Muestra el menú de opciones"""
        print("\n" + "="*50)
        print("🧪 PRUEBA INTERACTIVA DE ROBUSTEZ")
        print("="*50)
        print("Opciones:")
        print("  c - Capturar nueva imagen")
        print("  1 - Configuración Original (conf=0.55, iou=0.35)")
        print("  2 - Configuración Moderada (conf=0.3, iou=0.2)")
        print("  3 - Configuración Permisiva (conf=0.1, iou=0.1)")
        print("  4 - Configuración Ultra Permisiva (conf=0.01, iou=0.01)")
        print("  5 - Moderada + Preprocesamiento")
        print("  6 - Permisiva + Preprocesamiento")
        print("  7 - Ultra Permisiva + Preprocesamiento")
        print("  p - Configuración personalizada")
        print("  m - Mostrar menú")
        print("  q - Salir")
        print("="*50)
    
    def configuracion_personalizada(self):
        """Permite configurar parámetros personalizados"""
        try:
            print("\n🔧 Configuración personalizada:")
            
            confianza = float(input("   Confianza mínima (0.0-1.0): "))
            iou = float(input("   IoU threshold (0.0-1.0): "))
            
            usar_prep = input("   ¿Usar preprocesamiento? (s/n): ").lower().startswith('s')
            
            self.probar_configuracion(confianza, iou, usar_prep)
            
        except ValueError:
            print("❌ Error: Ingresa valores numéricos válidos")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def ejecutar(self):
        """Ejecuta la prueba interactiva"""
        if not self.inicializar():
            return
        
        self.mostrar_menu()
        
        while True:
            try:
                opcion = input("\n🎯 Selecciona una opción: ").lower().strip()
                
                if opcion == 'q':
                    print("👋 Saliendo...")
                    break
                elif opcion == 'c':
                    self.capturar_nueva_imagen()
                elif opcion == '1':
                    self.probar_configuracion(0.55, 0.35, False)
                elif opcion == '2':
                    self.probar_configuracion(0.3, 0.2, False)
                elif opcion == '3':
                    self.probar_configuracion(0.1, 0.1, False)
                elif opcion == '4':
                    self.probar_configuracion(0.01, 0.01, False)
                elif opcion == '5':
                    self.probar_configuracion(0.3, 0.2, True)
                elif opcion == '6':
                    self.probar_configuracion(0.1, 0.1, True)
                elif opcion == '7':
                    self.probar_configuracion(0.01, 0.01, True)
                elif opcion == 'p':
                    self.configuracion_personalizada()
                elif opcion == 'm':
                    self.mostrar_menu()
                else:
                    print("❌ Opción no válida. Usa 'm' para ver el menú.")
                    
            except KeyboardInterrupt:
                print("\n👋 Saliendo...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Liberar recursos
        self.sistema.liberar()
        print("✅ Recursos liberados")

def main():
    """Función principal"""
    prueba = PruebaInteractivaRobustez()
    prueba.ejecutar()

if __name__ == "__main__":
    main()
