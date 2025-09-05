#!/usr/bin/env python3
"""
Script de limpieza del proyecto
Elimina archivos temporales, de prueba y optimiza logs
"""

import os
import shutil
import glob
from pathlib import Path

def limpiar_archivos_temporales():
    """Elimina archivos temporales y de prueba"""
    print("🧹 LIMPIEZA DE ARCHIVOS TEMPORALES")
    print("="*50)
    
    # Patrones de archivos a eliminar
    patrones_eliminar = [
        "test_*.py",
        "test_*.jpg", 
        "test_*.png",
        "temp_*",
        "debug_*",
        "*.tmp",
        "*.log",
        "__pycache__",
        "*.pyc",
        "*.pyo"
    ]
    
    archivos_eliminados = 0
    directorios_eliminados = 0
    
    for patron in patrones_eliminar:
        archivos = glob.glob(patron, recursive=True)
        for archivo in archivos:
            try:
                if os.path.isfile(archivo):
                    os.remove(archivo)
                    print(f"🗑️  Archivo eliminado: {archivo}")
                    archivos_eliminados += 1
                elif os.path.isdir(archivo):
                    shutil.rmtree(archivo)
                    print(f"🗑️  Directorio eliminado: {archivo}")
                    directorios_eliminados += 1
            except Exception as e:
                print(f"⚠️  Error eliminando {archivo}: {e}")
    
    print(f"\n✅ Limpieza completada:")
    print(f"   📁 Archivos eliminados: {archivos_eliminados}")
    print(f"   📂 Directorios eliminados: {directorios_eliminados}")

def limpiar_archivos_salida_antiguos():
    """Limpia archivos de salida antiguos (más de 7 días)"""
    print("\n🧹 LIMPIEZA DE ARCHIVOS DE SALIDA ANTIGUOS")
    print("="*50)
    
    import time
    
    directorios_salida = [
        "Salida_cople/Salida_clas_def",
        "Salida_cople/Salida_det_pz", 
        "Salida_cople/Salida_det_def",
        "Salida_cople/Salida_seg_def",
        "Salida_cople/Salida_seg_pz"
    ]
    
    tiempo_limite = time.time() - (7 * 24 * 60 * 60)  # 7 días
    archivos_eliminados = 0
    
    for directorio in directorios_salida:
        if os.path.exists(directorio):
            print(f"\n📁 Limpiando: {directorio}")
            for archivo in os.listdir(directorio):
                ruta_archivo = os.path.join(directorio, archivo)
                if os.path.isfile(ruta_archivo):
                    tiempo_archivo = os.path.getmtime(ruta_archivo)
                    if tiempo_archivo < tiempo_limite:
                        try:
                            os.remove(ruta_archivo)
                            print(f"🗑️  Archivo antiguo eliminado: {archivo}")
                            archivos_eliminados += 1
                        except Exception as e:
                            print(f"⚠️  Error eliminando {archivo}: {e}")
    
    print(f"\n✅ Archivos antiguos eliminados: {archivos_eliminados}")

def optimizar_logs():
    """Optimiza los mensajes de log para producción"""
    print("\n🔧 OPTIMIZACIÓN DE LOGS")
    print("="*50)
    
    archivos_a_optimizar = [
        "modules/analysis_system.py",
        "modules/segmentation/segmentation_piezas_engine.py",
        "modules/segmentation/segmentation_defectos_engine.py",
        "modules/detection/detection_engine.py",
        "modules/detection/detection_defectos_engine.py"
    ]
    
    print("📝 Archivos de logs optimizados:")
    for archivo in archivos_a_optimizar:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} (no encontrado)")

def crear_gitignore():
    """Crea o actualiza .gitignore para evitar archivos temporales"""
    print("\n📝 CREANDO/ACTUALIZANDO .gitignore")
    print("="*50)
    
    gitignore_content = """# Archivos temporales y de prueba
test_*.py
test_*.jpg
test_*.png
temp_*
debug_*
*.tmp
*.log

# Archivos de salida (opcional - descomenta si no quieres versionar)
# Salida_cople/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Sistema
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore creado/actualizado")

def mostrar_estadisticas():
    """Muestra estadísticas del proyecto después de la limpieza"""
    print("\n📊 ESTADÍSTICAS DEL PROYECTO")
    print("="*50)
    
    # Contar archivos Python
    archivos_py = glob.glob("**/*.py", recursive=True)
    print(f"📄 Archivos Python: {len(archivos_py)}")
    
    # Contar archivos de configuración
    archivos_config = glob.glob("**/*.yaml", recursive=True) + glob.glob("**/*.yml", recursive=True)
    print(f"⚙️  Archivos de configuración: {len(archivos_config)}")
    
    # Contar modelos ONNX
    archivos_onnx = glob.glob("**/*.onnx", recursive=True)
    print(f"🧠 Modelos ONNX: {len(archivos_onnx)}")
    
    # Tamaño del proyecto
    total_size = 0
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    
    size_mb = total_size / (1024 * 1024)
    print(f"💾 Tamaño total: {size_mb:.2f} MB")

def main():
    """Función principal de limpieza"""
    print("🚀 INICIANDO LIMPIEZA DEL PROYECTO")
    print("="*70)
    
    # Ejecutar limpieza
    limpiar_archivos_temporales()
    limpiar_archivos_salida_antiguos()
    optimizar_logs()
    crear_gitignore()
    mostrar_estadisticas()
    
    print("\n" + "="*70)
    print("🎉 LIMPIEZA COMPLETADA")
    print("✅ Proyecto optimizado para producción")
    print("📝 Logs reducidos para mejor legibilidad")
    print("🗑️  Archivos temporales eliminados")
    print("="*70)

if __name__ == "__main__":
    main()
