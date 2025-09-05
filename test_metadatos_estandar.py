#!/usr/bin/env python3
"""
Script para probar la estructura estándar de metadatos
"""

import sys
import os
import json
import numpy as np
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.metadata_standard import MetadataStandard

def crear_datos_prueba():
    """Crea datos de prueba para diferentes tipos de análisis"""
    
    # Datos de clasificación
    clasificacion = {
        "clase": "Aceptado",
        "confianza": 0.95,
        "tiempo_inferencia": 45.2
    }
    
    # Datos de detección
    detecciones_piezas = [
        {
            "clase": "Cople",
            "confianza": 0.87,
            "bbox": {"x1": 100, "y1": 50, "x2": 300, "y2": 250},
            "centroide": {"x": 200, "y": 150},
            "area": 40000
        },
        {
            "clase": "Cople", 
            "confianza": 0.92,
            "bbox": {"x1": 350, "y1": 100, "x2": 550, "y2": 300},
            "centroide": {"x": 450, "y": 200},
            "area": 40000
        }
    ]
    
    detecciones_defectos = [
        {
            "clase": "Defecto",
            "confianza": 0.78,
            "bbox": {"x1": 150, "y1": 120, "x2": 200, "y2": 170},
            "centroide": {"x": 175, "y": 145},
            "area": 2500
        }
    ]
    
    # Datos de segmentación
    segmentaciones_defectos = [
        {
            "clase": "Defecto",
            "confianza": 0.82,
            "bbox": {"x1": 150, "y1": 120, "x2": 200, "y2": 170},
            "centroide": {"x": 175, "y": 145},
            "area": 2500,
            "area_mascara": 2200,
            "ancho_mascara": 50,
            "alto_mascara": 50,
            "mascara": np.random.rand(640, 640).astype(np.float32),
            "coeficientes_mascara": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
    ]
    
    segmentaciones_piezas = [
        {
            "clase": "Cople",
            "confianza": 0.89,
            "bbox": {"x1": 100, "y1": 50, "x2": 300, "y2": 250},
            "centroide": {"x": 200, "y": 150},
            "area": 40000,
            "area_mascara": 38000,
            "ancho_mascara": 200,
            "alto_mascara": 200,
            "mascara": np.random.rand(640, 640).astype(np.float32),
            "fusionada": True,
            "objetos_fusionados": 2
        }
    ]
    
    # Tiempos de ejemplo
    tiempos = {
        "captura_ms": 15.2,
        "clasificacion_ms": 45.2,
        "deteccion_piezas_ms": 78.5,
        "deteccion_defectos_ms": 65.3,
        "segmentacion_defectos_ms": 120.8,
        "segmentacion_piezas_ms": 95.4,
        "total_ms": 420.4
    }
    
    return {
        "clasificacion": clasificacion,
        "detecciones_piezas": detecciones_piezas,
        "detecciones_defectos": detecciones_defectos,
        "segmentaciones_defectos": segmentaciones_defectos,
        "segmentaciones_piezas": segmentaciones_piezas,
        "tiempos": tiempos
    }

def test_metadatos_clasificacion():
    """Prueba metadatos de clasificación"""
    print("🧪 PRUEBA: Metadatos de Clasificación")
    print("="*50)
    
    datos = crear_datos_prueba()
    
    metadatos = MetadataStandard.crear_metadatos_completos(
        tipo_analisis="clasificacion",
        archivo_imagen="test_clasificacion.jpg",
        resultados=datos["clasificacion"],
        tiempos=datos["tiempos"],
        timestamp_captura="20250905_120000"
    )
    
    # Validar estructura
    campos_requeridos = [
        "archivo_imagen", "timestamp_procesamiento", "timestamp_captura",
        "tipo_analisis", "version_metadatos", "modelo", "imagen", "sistema",
        "resultados", "tiempos", "estadisticas"
    ]
    
    for campo in campos_requeridos:
        if campo not in metadatos:
            print(f"❌ Campo faltante: {campo}")
            return False
        else:
            print(f"✅ Campo presente: {campo}")
    
    # Validar subcampos específicos
    if "clasificacion" not in metadatos["resultados"]:
        print("❌ Subcampo 'clasificacion' faltante en resultados")
        return False
    
    print("✅ Estructura de clasificación válida")
    return True

def test_metadatos_deteccion():
    """Prueba metadatos de detección"""
    print("\n🧪 PRUEBA: Metadatos de Detección")
    print("="*50)
    
    datos = crear_datos_prueba()
    
    # Probar detección de piezas
    metadatos_piezas = MetadataStandard.crear_metadatos_completos(
        tipo_analisis="deteccion_piezas",
        archivo_imagen="test_deteccion_piezas.jpg",
        resultados=datos["detecciones_piezas"],
        tiempos=datos["tiempos"]
    )
    
    # Probar detección de defectos
    metadatos_defectos = MetadataStandard.crear_metadatos_completos(
        tipo_analisis="deteccion_defectos",
        archivo_imagen="test_deteccion_defectos.jpg",
        resultados=datos["detecciones_defectos"],
        tiempos=datos["tiempos"]
    )
    
    # Validar estructura común
    for nombre, metadatos in [("piezas", metadatos_piezas), ("defectos", metadatos_defectos)]:
        print(f"\n📋 Validando detección de {nombre}:")
        
        if f"{nombre}_detectadas" not in metadatos["resultados"]:
            print(f"❌ Subcampo '{nombre}_detectadas' faltante")
            return False
        
        detecciones = metadatos["resultados"][f"{nombre}_detectadas"]
        if len(detecciones) == 0:
            print(f"❌ No hay detecciones de {nombre}")
            return False
        
        # Validar estructura de cada detección
        deteccion = detecciones[0]
        campos_deteccion = ["id", "clase", "confianza", "bbox", "centroide", "area"]
        
        for campo in campos_deteccion:
            if campo not in deteccion:
                print(f"❌ Campo '{campo}' faltante en detección")
                return False
        
        print(f"✅ Estructura de detección de {nombre} válida")
    
    return True

def test_metadatos_segmentacion():
    """Prueba metadatos de segmentación"""
    print("\n🧪 PRUEBA: Metadatos de Segmentación")
    print("="*50)
    
    datos = crear_datos_prueba()
    
    # Probar segmentación de defectos
    metadatos_defectos = MetadataStandard.crear_metadatos_completos(
        tipo_analisis="segmentacion_defectos",
        archivo_imagen="test_segmentacion_defectos.jpg",
        resultados=datos["segmentaciones_defectos"],
        tiempos=datos["tiempos"]
    )
    
    # Probar segmentación de piezas
    metadatos_piezas = MetadataStandard.crear_metadatos_completos(
        tipo_analisis="segmentacion_piezas",
        archivo_imagen="test_segmentacion_piezas.jpg",
        resultados=datos["segmentaciones_piezas"],
        tiempos=datos["tiempos"]
    )
    
    # Validar estructura común
    for nombre, metadatos in [("defectos", metadatos_defectos), ("piezas", metadatos_piezas)]:
        print(f"\n📋 Validando segmentación de {nombre}:")
        
        if f"{nombre}_segmentadas" not in metadatos["resultados"]:
            print(f"❌ Subcampo '{nombre}_segmentadas' faltante")
            return False
        
        segmentaciones = metadatos["resultados"][f"{nombre}_segmentadas"]
        if len(segmentaciones) == 0:
            print(f"❌ No hay segmentaciones de {nombre}")
            return False
        
        # Validar estructura de cada segmentación
        segmentacion = segmentaciones[0]
        campos_segmentacion = [
            "id", "clase", "confianza", "bbox", "centroide", 
            "area_bbox", "area_mascara", "dimensiones_mascara", "tiene_mascara"
        ]
        
        for campo in campos_segmentacion:
            if campo not in segmentacion:
                print(f"❌ Campo '{campo}' faltante en segmentación")
                return False
        
        # Validar campos específicos de segmentación
        if "info_mascara" not in segmentacion:
            print(f"❌ Campo 'info_mascara' faltante en segmentación")
            return False
        
        print(f"✅ Estructura de segmentación de {nombre} válida")
    
    return True

def test_guardado_archivos():
    """Prueba el guardado de archivos JSON"""
    print("\n🧪 PRUEBA: Guardado de Archivos")
    print("="*50)
    
    datos = crear_datos_prueba()
    
    # Crear directorio de prueba
    directorio_prueba = "test_metadatos"
    if not os.path.exists(directorio_prueba):
        os.makedirs(directorio_prueba)
    
    # Probar guardado de diferentes tipos
    tipos_prueba = [
        ("clasificacion", datos["clasificacion"]),
        ("deteccion_piezas", datos["detecciones_piezas"]),
        ("deteccion_defectos", datos["detecciones_defectos"]),
        ("segmentacion_defectos", datos["segmentaciones_defectos"]),
        ("segmentacion_piezas", datos["segmentaciones_piezas"])
    ]
    
    archivos_creados = []
    
    for tipo, resultados in tipos_prueba:
        print(f"\n📁 Probando guardado de {tipo}...")
        
        # Crear metadatos
        metadatos = MetadataStandard.crear_metadatos_completos(
            tipo_analisis=tipo,
            archivo_imagen=f"test_{tipo}.jpg",
            resultados=resultados,
            tiempos=datos["tiempos"]
        )
        
        # Guardar archivo
        archivo_json = os.path.join(directorio_prueba, f"test_{tipo}.json")
        exito = MetadataStandard.guardar_metadatos(metadatos, archivo_json)
        
        if exito and os.path.exists(archivo_json):
            print(f"✅ Archivo guardado: {archivo_json}")
            archivos_creados.append(archivo_json)
            
            # Verificar que el archivo es JSON válido
            try:
                with open(archivo_json, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"✅ JSON válido: {archivo_json}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON inválido: {e}")
                return False
        else:
            print(f"❌ Error guardando: {archivo_json}")
            return False
    
    print(f"\n✅ Todos los archivos guardados correctamente ({len(archivos_creados)} archivos)")
    return True

def test_consistencia_estructura():
    """Prueba la consistencia de la estructura entre diferentes tipos"""
    print("\n🧪 PRUEBA: Consistencia de Estructura")
    print("="*50)
    
    datos = crear_datos_prueba()
    
    # Crear metadatos para todos los tipos
    metadatos_todos = {}
    tipos = ["clasificacion", "deteccion_piezas", "deteccion_defectos", 
             "segmentacion_defectos", "segmentacion_piezas"]
    
    for tipo in tipos:
        resultados = datos.get(tipo, [])
        metadatos_todos[tipo] = MetadataStandard.crear_metadatos_completos(
            tipo_analisis=tipo,
            archivo_imagen=f"test_{tipo}.jpg",
            resultados=resultados,
            tiempos=datos["tiempos"]
        )
    
    # Verificar campos comunes
    campos_comunes = [
        "archivo_imagen", "timestamp_procesamiento", "timestamp_captura",
        "tipo_analisis", "version_metadatos", "modelo", "imagen", "sistema",
        "resultados", "tiempos", "estadisticas"
    ]
    
    print("🔍 Verificando campos comunes...")
    for campo in campos_comunes:
        presente_en_todos = all(campo in metadatos for metadatos in metadatos_todos.values())
        if presente_en_todos:
            print(f"✅ Campo común: {campo}")
        else:
            print(f"❌ Campo faltante: {campo}")
            return False
    
    # Verificar estructura del modelo
    print("\n🔍 Verificando estructura del modelo...")
    for tipo, metadatos in metadatos_todos.items():
        modelo = metadatos["modelo"]
        if "nombre" not in modelo or "tipo" not in modelo or "clases_disponibles" not in modelo:
            print(f"❌ Estructura de modelo incompleta en {tipo}")
            return False
        print(f"✅ Modelo {tipo}: {modelo['nombre']}")
    
    # Verificar estructura de imagen
    print("\n🔍 Verificando estructura de imagen...")
    for tipo, metadatos in metadatos_todos.items():
        imagen = metadatos["imagen"]
        if "resolucion" not in imagen or "formato" not in imagen or "tipo" not in imagen:
            print(f"❌ Estructura de imagen incompleta en {tipo}")
            return False
        print(f"✅ Imagen {tipo}: {imagen['resolucion']}")
    
    print("\n✅ Estructura consistente entre todos los tipos")
    return True

def main():
    """Función principal de prueba"""
    print("🚀 INICIANDO PRUEBAS DE METADATOS ESTÁNDAR")
    print("="*70)
    
    pruebas = [
        ("Metadatos de Clasificación", test_metadatos_clasificacion),
        ("Metadatos de Detección", test_metadatos_deteccion),
        ("Metadatos de Segmentación", test_metadatos_segmentacion),
        ("Guardado de Archivos", test_guardado_archivos),
        ("Consistencia de Estructura", test_consistencia_estructura)
    ]
    
    resultados = []
    
    for nombre, funcion in pruebas:
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen de resultados
    print("\n" + "="*70)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*70)
    
    exitosos = 0
    for nombre, resultado in resultados:
        estado = "✅ EXITOSO" if resultado else "❌ FALLIDO"
        print(f"{estado}: {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\n🎯 Resultado: {exitosos}/{len(resultados)} pruebas exitosas")
    
    if exitosos == len(resultados):
        print("🎉 ¡TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        print("✅ La estructura estándar de metadatos está funcionando correctamente")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisar la implementación de la estructura estándar")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
