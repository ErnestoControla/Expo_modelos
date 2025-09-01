"""
Script de prueba para verificar el funcionamiento del sistema
"""

import sys
import os

def test_imports():
    """Prueba que todos los módulos se pueden importar correctamente."""
    print("🧪 Probando importaciones...")
    
    try:
        # Importar configuración
        from config import CameraConfig, ModelsConfig, GlobalConfig
        print("✅ Configuración importada correctamente")
        
        # Importar utilidades
        from utils import verificar_dependencias, mostrar_info_sistema
        print("✅ Utilidades importadas correctamente")
        
        # Importar módulos de captura
        from modules.capture import CamaraTiempoOptimizada
        print("✅ Módulo de captura importado correctamente")
        
        # Importar módulos de clasificación
        from modules.classification import ClasificadorCoplesONNX, ProcesadorImagenClasificacion
        print("✅ Módulos de clasificación importados correctamente")
        
        print("✅ Todas las importaciones exitosas!")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_configuration():
    """Prueba que la configuración se puede cargar correctamente."""
    print("\n🔧 Probando configuración...")
    
    try:
        from config import CameraConfig, ModelsConfig, GlobalConfig
        
        # Verificar configuración de cámara
        print(f"   📷 IP Cámara: {CameraConfig.DEFAULT_IP}")
        print(f"   📷 Resolución: {CameraConfig.ROI_WIDTH}x{CameraConfig.ROI_HEIGHT}")
        print(f"   📷 Framerate: {CameraConfig.FRAMERATE}")
        
        # Verificar configuración de modelos
        print(f"   🧠 Directorio modelos: {ModelsConfig.MODELS_DIR}")
        print(f"   🧠 Modelo clasificación: {ModelsConfig.CLASSIFICATION_MODEL}")
        
        # Verificar configuración global
        print(f"   🌐 Directorio salida: {GlobalConfig.ensure_output_dir()}")
        
        print("✅ Configuración cargada correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_model_files():
    """Prueba que los archivos del modelo existen."""
    print("\n📁 Probando archivos del modelo...")
    
    try:
        from config import ModelsConfig
        
        # Verificar directorio de modelos
        if not os.path.exists(ModelsConfig.MODELS_DIR):
            print(f"❌ Directorio de modelos no existe: {ModelsConfig.MODELS_DIR}")
            return False
        
        # Verificar modelo de clasificación
        model_path = os.path.join(ModelsConfig.MODELS_DIR, ModelsConfig.CLASSIFICATION_MODEL)
        if not os.path.exists(model_path):
            print(f"❌ Modelo de clasificación no encontrado: {model_path}")
            return False
        
        # Verificar archivo de clases
        classes_path = os.path.join(ModelsConfig.MODELS_DIR, ModelsConfig.CLASSIFICATION_CLASSES)
        if not os.path.exists(classes_path):
            print(f"❌ Archivo de clases no encontrado: {classes_path}")
            return False
        
        # Mostrar información del modelo
        model_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
        print(f"   🧠 Modelo: {ModelsConfig.CLASSIFICATION_MODEL}")
        print(f"   📏 Tamaño: {model_size:.1f} MB")
        print(f"   📝 Clases: {classes_path}")
        
        print("✅ Archivos del modelo verificados!")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando archivos: {e}")
        return False

def test_dependencies():
    """Prueba que las dependencias están disponibles."""
    print("\n📦 Probando dependencias...")
    
    try:
        from utils import verificar_dependencias
        
        if verificar_dependencias():
            print("✅ Todas las dependencias están disponibles!")
            return True
        else:
            print("⚠️ Algunas dependencias no están disponibles")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando dependencias: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA")
    print("=" * 50)
    
    tests = [
        ("Importaciones", test_imports),
        ("Configuración", test_configuration),
        ("Archivos del modelo", test_model_files),
        ("Dependencias", test_dependencies)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        if test_func():
            passed += 1
        print()
    
    # Resumen final
    print("=" * 50)
    print(f"📊 RESUMEN DE PRUEBAS:")
    print(f"   ✅ Exitosas: {passed}")
    print(f"   ❌ Fallidas: {total - passed}")
    print(f"   📈 Porcentaje: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está listo para usar.")
        print("\n💡 Para ejecutar el sistema completo:")
        print("   python main.py")
    else:
        print(f"\n⚠️ {total - passed} prueba(s) fallaron. Revisa los errores antes de continuar.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
