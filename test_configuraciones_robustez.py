#!/usr/bin/env python3
"""
Script para probar diferentes configuraciones de robustez
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
from typing import Dict, List, Any

class EvaluadorConfiguraciones:
    """
    Evaluador de diferentes configuraciones de robustez
    """
    
    def __init__(self):
        self.resultados = []
        self.sistema = None
        
    def inicializar_sistema(self):
        """Inicializa el sistema de análisis"""
        print("🚀 Inicializando sistema...")
        self.sistema = SistemaAnalisisIntegrado()
        
        if not self.sistema.inicializar():
            print("❌ Error inicializando sistema")
            return False
        
        print("✅ Sistema inicializado correctamente")
        return True
    
    def capturar_imagen(self) -> np.ndarray:
        """Captura una imagen para las pruebas"""
        print("📸 Capturando imagen de prueba...")
        frame = self.sistema.camara.capturar_frame()
        if frame is None:
            print("❌ Error capturando imagen")
            return None
        
        print(f"✅ Imagen capturada: {frame.shape}")
        return frame
    
    def analizar_iluminacion(self, imagen: np.ndarray) -> Dict[str, float]:
        """Analiza las condiciones de iluminación"""
        gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Calcular histograma
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        total_pixels = gray.shape[0] * gray.shape[1]
        p5 = np.percentile(hist, 5)
        p95 = np.percentile(hist, 95)
        dynamic_range = p95 - p5
        
        # Calcular entropía
        hist_norm = hist / total_pixels
        entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-10))
        
        return {
            'brightness': float(brightness),
            'contrast': float(contrast),
            'dynamic_range': float(dynamic_range),
            'entropy': float(entropy),
            'p5': float(p5),
            'p95': float(p95)
        }
    
    def probar_configuracion(self, nombre: str, config: Dict[str, Any], imagen: np.ndarray) -> Dict[str, Any]:
        """
        Prueba una configuración específica
        
        Args:
            nombre: Nombre de la configuración
            config: Parámetros de la configuración
            imagen: Imagen de prueba
            
        Returns:
            Resultados de la prueba
        """
        print(f"\n🔧 Probando configuración: {nombre}")
        print(f"   Parámetros: {config}")
        
        try:
            # Aplicar configuración
            if 'confianza_min' in config:
                self.sistema.detector_piezas.actualizar_umbrales(
                    confianza_min=config['confianza_min'],
                    iou_threshold=config.get('iou_threshold', 0.35)
                )
            
            # Aplicar preprocesamiento si está configurado
            if config.get('aplicar_preprocesamiento', False):
                imagen_procesada, metrics = self.sistema.preprocesar_imagen_robusta(imagen)
                print(f"   📊 Métricas de iluminación: Brillo={metrics.get('brightness', 0):.1f}, Contraste={metrics.get('contrast', 0):.1f}")
            else:
                imagen_procesada = imagen
                metrics = self.analizar_iluminacion(imagen)
            
            # Realizar detección
            tiempo_inicio = time.time()
            detecciones = self.sistema.detector_piezas.detectar_piezas(imagen_procesada)
            tiempo_deteccion = (time.time() - tiempo_inicio) * 1000  # ms
            
            # Analizar resultados
            num_detecciones = len(detecciones)
            confianzas = [det.get('confianza', 0) for det in detecciones]
            areas = [det.get('area', 0) for det in detecciones]
            
            resultado = {
                'nombre': nombre,
                'configuracion': config,
                'metricas_iluminacion': metrics,
                'num_detecciones': num_detecciones,
                'tiempo_deteccion_ms': tiempo_deteccion,
                'confianza_promedio': np.mean(confianzas) if confianzas else 0,
                'confianza_minima': np.min(confianzas) if confianzas else 0,
                'confianza_maxima': np.max(confianzas) if confianzas else 0,
                'area_promedio': np.mean(areas) if areas else 0,
                'detecciones': detecciones,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"   ✅ Resultados: {num_detecciones} detecciones, tiempo: {tiempo_deteccion:.1f}ms")
            if confianzas:
                print(f"   📊 Confianzas: min={np.min(confianzas):.3f}, max={np.max(confianzas):.3f}, prom={np.mean(confianzas):.3f}")
            
            return resultado
            
        except Exception as e:
            print(f"   ❌ Error en configuración {nombre}: {e}")
            return {
                'nombre': nombre,
                'configuracion': config,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def ejecutar_pruebas_completas(self):
        """Ejecuta todas las pruebas de configuración"""
        print("🧪 INICIANDO PRUEBAS DE CONFIGURACIONES DE ROBUSTEZ")
        print("=" * 60)
        
        # Inicializar sistema
        if not self.inicializar_sistema():
            return
        
        # Capturar imagen de prueba
        imagen = self.capturar_imagen()
        if imagen is None:
            return
        
        # Analizar condiciones de iluminación
        metrics_iniciales = self.analizar_iluminacion(imagen)
        print(f"\n📊 Condiciones de iluminación:")
        print(f"   Brillo: {metrics_iniciales['brightness']:.1f}")
        print(f"   Contraste: {metrics_iniciales['contrast']:.1f}")
        print(f"   Rango dinámico: {metrics_iniciales['dynamic_range']:.1f}")
        print(f"   Entropía: {metrics_iniciales['entropy']:.3f}")
        
        # Definir configuraciones a probar
        configuraciones = [
            {
                'nombre': 'Configuración Original',
                'config': {
                    'confianza_min': 0.55,
                    'iou_threshold': 0.35,
                    'aplicar_preprocesamiento': False
                }
            },
            {
                'nombre': 'Configuración Moderada',
                'config': {
                    'confianza_min': 0.3,
                    'iou_threshold': 0.2,
                    'aplicar_preprocesamiento': False
                }
            },
            {
                'nombre': 'Configuración Permisiva',
                'config': {
                    'confianza_min': 0.1,
                    'iou_threshold': 0.1,
                    'aplicar_preprocesamiento': False
                }
            },
            {
                'nombre': 'Configuración Ultra Permisiva',
                'config': {
                    'confianza_min': 0.01,
                    'iou_threshold': 0.01,
                    'aplicar_preprocesamiento': False
                }
            },
            {
                'nombre': 'Moderada + Preprocesamiento',
                'config': {
                    'confianza_min': 0.3,
                    'iou_threshold': 0.2,
                    'aplicar_preprocesamiento': True
                }
            },
            {
                'nombre': 'Permisiva + Preprocesamiento',
                'config': {
                    'confianza_min': 0.1,
                    'iou_threshold': 0.1,
                    'aplicar_preprocesamiento': True
                }
            },
            {
                'nombre': 'Ultra Permisiva + Preprocesamiento',
                'config': {
                    'confianza_min': 0.01,
                    'iou_threshold': 0.01,
                    'aplicar_preprocesamiento': True
                }
            }
        ]
        
        # Ejecutar pruebas
        print(f"\n🎯 Ejecutando {len(configuraciones)} configuraciones...")
        
        for config_test in configuraciones:
            resultado = self.probar_configuracion(
                config_test['nombre'], 
                config_test['config'], 
                imagen
            )
            self.resultados.append(resultado)
        
        # Mostrar resumen
        self.mostrar_resumen()
        
        # Guardar resultados
        self.guardar_resultados()
        
        # Liberar recursos
        self.sistema.liberar()
        print("\n✅ Pruebas completadas")
    
    def mostrar_resumen(self):
        """Muestra un resumen de los resultados"""
        print("\n📊 RESUMEN DE RESULTADOS")
        print("=" * 50)
        
        for resultado in self.resultados:
            if 'error' in resultado:
                print(f"❌ {resultado['nombre']}: ERROR - {resultado['error']}")
            else:
                print(f"✅ {resultado['nombre']}:")
                print(f"   Detecciones: {resultado['num_detecciones']}")
                print(f"   Tiempo: {resultado['tiempo_deteccion_ms']:.1f}ms")
                if resultado['num_detecciones'] > 0:
                    print(f"   Confianza: {resultado['confianza_promedio']:.3f} (min: {resultado['confianza_minima']:.3f}, max: {resultado['confianza_maxima']:.3f})")
                    print(f"   Área promedio: {resultado['area_promedio']:.0f} píxeles")
                print()
    
    def guardar_resultados(self):
        """Guarda los resultados en un archivo JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resultados_configuraciones_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.resultados, f, indent=2, ensure_ascii=False)
            print(f"💾 Resultados guardados en: {filename}")
        except Exception as e:
            print(f"❌ Error guardando resultados: {e}")
    
    def recomendar_configuracion(self) -> str:
        """Recomienda la mejor configuración basándose en los resultados"""
        if not self.resultados:
            return "No hay resultados para analizar"
        
        # Filtrar resultados exitosos
        resultados_exitosos = [r for r in self.resultados if 'error' not in r and r['num_detecciones'] > 0]
        
        if not resultados_exitosos:
            return "Ninguna configuración produjo detecciones"
        
        # Criterios de evaluación
        mejor_config = None
        mejor_puntuacion = -1
        
        for resultado in resultados_exitosos:
            # Puntuación basada en: detecciones, confianza, tiempo
            puntuacion = (
                resultado['num_detecciones'] * 10 +  # Priorizar detecciones
                resultado['confianza_promedio'] * 100 +  # Priorizar confianza
                (1000 - resultado['tiempo_deteccion_ms']) / 10  # Priorizar velocidad
            )
            
            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_config = resultado
        
        if mejor_config:
            return f"Mejor configuración: {mejor_config['nombre']} (puntuación: {mejor_puntuacion:.1f})"
        else:
            return "No se pudo determinar la mejor configuración"

def main():
    """Función principal"""
    evaluador = EvaluadorConfiguraciones()
    evaluador.ejecutar_pruebas_completas()
    
    # Mostrar recomendación
    recomendacion = evaluador.recomendar_configuracion()
    print(f"\n🎯 RECOMENDACIÓN: {recomendacion}")

if __name__ == "__main__":
    main()
