#!/usr/bin/env python3
"""
Script para optimizar logs del proyecto
Reemplaza logs verbosos con logs más limpios
"""

import os
import re
import glob

def optimizar_archivo(archivo_path):
    """Optimiza los logs de un archivo específico"""
    print(f"🔧 Optimizando: {archivo_path}")
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Patrones de reemplazo
        reemplazos = [
            # Logs de debug verbosos
            (r'print\(f"🔍 Debug.*?\)', ''),
            (r'print\(f"🔍 DEBUG.*?\)', ''),
            (r'print\(f"🔍 .*?\)', ''),
            
            # Logs de información excesiva
            (r'print\(f"   .*?\)', ''),
            (r'print\(f"📊 .*?\)', ''),
            
            # Logs de éxito con emoji
            (r'print\(f"✅ ([^"]+)"\)', r'log_success("\1")'),
            (r'print\(f"❌ ([^"]+)"\)', r'log_error("\1")'),
            (r'print\(f"⚠️ ([^"]+)"\)', r'log_warning("\1")'),
            (r'print\(f"🎯 ([^"]+)"\)', r'log_info("\1")'),
            (r'print\(f"📷 ([^"]+)"\)', r'log_info("\1")'),
            (r'print\(f"🧠 ([^"]+)"\)', r'log_info("\1")'),
            (r'print\(f"🔧 ([^"]+)"\)', r'log_info("\1")'),
            (r'print\(f"📁 ([^"]+)"\)', r'log_info("\1")'),
            (r'print\(f"📸 ([^"]+)"\)', r'log_info("\1")'),
            (r'print\(f"🎨 ([^"]+)"\)', r'log_info("\1")'),
            (r'print\(f"💾 ([^"]+)"\)', r'log_info("\1")'),
            (r'print\(f"🔗 ([^"]+)"\)', r'log_info("\1")'),
            
            # Logs simples sin emoji
            (r'print\(f"([^"]+)"\)', r'log_info("\1")'),
        ]
        
        # Aplicar reemplazos
        contenido_original = contenido
        for patron, reemplazo in reemplazos:
            contenido = re.sub(patron, reemplazo, contenido, flags=re.MULTILINE)
        
        # Limpiar líneas vacías múltiples
        contenido = re.sub(r'\n\s*\n\s*\n', '\n\n', contenido)
        
        # Agregar import de logging si no existe
        if 'log_success' in contenido and 'from modules.logging_config import' not in contenido:
            # Buscar la línea de imports
            import_match = re.search(r'(from config import.*?\n)', contenido)
            if import_match:
                contenido = contenido.replace(
                    import_match.group(1),
                    import_match.group(1) + 'from modules.logging_config import log_info, log_warning, log_error, log_success\n'
                )
        
        # Solo escribir si hubo cambios
        if contenido != contenido_original:
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print(f"✅ Optimizado: {archivo_path}")
            return True
        else:
            print(f"ℹ️  Sin cambios: {archivo_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error optimizando {archivo_path}: {e}")
        return False

def optimizar_proyecto():
    """Optimiza todos los archivos del proyecto"""
    print("🚀 OPTIMIZANDO LOGS DEL PROYECTO")
    print("="*50)
    
    # Archivos a optimizar
    patrones_archivos = [
        "modules/**/*.py",
        "main.py"
    ]
    
    archivos_optimizados = 0
    archivos_procesados = 0
    
    for patron in patrones_archivos:
        archivos = glob.glob(patron, recursive=True)
        for archivo in archivos:
            # Saltar archivos de configuración y logging
            if any(skip in archivo for skip in ['__pycache__', 'logging_config.py', 'metadata_standard.py']):
                continue
                
            archivos_procesados += 1
            if optimizar_archivo(archivo):
                archivos_optimizados += 1
    
    print(f"\n📊 RESUMEN DE OPTIMIZACIÓN:")
    print(f"   📁 Archivos procesados: {archivos_procesados}")
    print(f"   ✅ Archivos optimizados: {archivos_optimizados}")
    print(f"   ℹ️  Sin cambios: {archivos_procesados - archivos_optimizados}")

def crear_configuracion_logging():
    """Crea configuración de logging para el proyecto"""
    print("\n🔧 CREANDO CONFIGURACIÓN DE LOGGING")
    print("="*50)
    
    config_content = '''# Configuración de logging para el sistema
# Niveles disponibles: DEBUG, INFO, WARNING, ERROR

# Nivel por defecto para producción
LOGGING_LEVEL = "INFO"

# Nivel para desarrollo/debug
# LOGGING_LEVEL = "DEBUG"

# Configuración de archivos de log
LOG_TO_FILE = False
LOG_FILE_PATH = "logs/sistema.log"

# Configuración de formato
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"
'''
    
    with open('logging_config.env', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Configuración de logging creada: logging_config.env")

def main():
    """Función principal"""
    print("🧹 OPTIMIZACIÓN DE LOGS DEL PROYECTO")
    print("="*70)
    
    optimizar_proyecto()
    crear_configuracion_logging()
    
    print("\n" + "="*70)
    print("🎉 OPTIMIZACIÓN COMPLETADA")
    print("✅ Logs optimizados para producción")
    print("📝 Ruido reducido en consola")
    print("🔧 Sistema de logging centralizado")
    print("="*70)

if __name__ == "__main__":
    main()
