# Changelog - Sistema de Análisis de Coples

## [2.0.0] - 2025-09-05

### 🎉 Nuevas Funcionalidades Implementadas

#### 📷 Sistema de Fallback a Webcam
- **Detección automática** de webcams disponibles
- **Fallback transparente** cuando no hay cámara GigE
- **Configuración flexible** de webcam (resolución, FPS)
- **Mantenimiento de funcionalidad** completa del sistema

#### 🎯 Módulos de Detección Completos
- **Detección de piezas** (`CopleDetPz1C1V.onnx`)
- **Detección de defectos** (`CopleDetDef1C2V.onnx`)
- **Procesamiento de resultados** con bounding boxes
- **Metadatos detallados** de detecciones

#### 🎨 Módulos de Segmentación Completos
- **Segmentación de defectos** (`CopleSegDef1C8V.onnx`)
- **Segmentación de piezas** (`CopleSegPZ1C1V.onnx`)
- **Generación de máscaras** precisas
- **Análisis dimensional** de piezas (ancho/alto de máscara)

#### 🛡️ Sistema de Robustez Avanzado
- **Robustez a iluminación** con normalización adaptativa
- **Umbrales adaptativos** basados en condiciones ambientales
- **Configuraciones predefinidas** (Conservadora, Moderada, Agresiva, Extrema)
- **Ajuste dinámico** de parámetros

#### 🔧 Fusión de Máscaras
- **Detección automática** de objetos pegados
- **Fusión inteligente** de máscaras superpuestas
- **Configuración personalizable** de distancias y overlaps
- **Preservación de calidad** de segmentación

#### 📊 Metadatos Estandarizados
- **Estructura JSON** consistente para todos los módulos
- **Información completa** de clasificación, detección y segmentación
- **Tiempos detallados** de procesamiento por módulo
- **Metadatos de modelos** utilizados

#### 🎮 Interfaz de Usuario Mejorada
- **Menú simplificado** y más intuitivo
- **Opciones principales** y avanzadas organizadas
- **Comandos específicos** para cada módulo
- **Configuración interactiva** de robustez y fusión

### 🔧 Mejoras Técnicas

#### Arquitectura Modular
- **Sistema completamente modular** con independencia entre módulos
- **Motor de análisis integrado** que orquesta todos los componentes
- **Gestión de recursos** optimizada
- **Liberación automática** de memoria y recursos

#### Rendimiento Optimizado
- **Timeouts agresivos** para evitar colgadas
- **Procesamiento en paralelo** cuando es posible
- **Gestión eficiente** de memoria
- **Logging optimizado** para producción

#### Configuración Flexible
- **Configuración centralizada** en `config.py`
- **Parámetros adaptativos** por condiciones
- **Configuraciones predefinidas** para diferentes escenarios
- **Fácil personalización** de umbrales y parámetros

### 🐛 Correcciones de Errores

#### Estabilidad del Sistema
- **Corrección de timeouts** en inferencia ONNX
- **Manejo robusto** de errores de captura
- **Prevención de colgadas** en procesamiento complejo
- **Validación de entrada** mejorada

#### Visualización
- **Corrección de la opción 'v'** para ver frame actual
- **Mejora en visualización** de máscaras de segmentación
- **Información detallada** del frame capturado
- **Control de usuario** mejorado

#### Procesamiento de Imágenes
- **Corrección de dimensiones** de máscaras
- **Validación de coordenadas** en detecciones
- **Manejo de errores** en redimensionado
- **Optimización de preprocesamiento**

### 📁 Estructura de Archivos Actualizada

#### Nuevos Módulos
```
modules/
├── capture/
│   └── webcam_fallback.py          # Fallback a webcam
├── detection/
│   ├── detection_engine.py         # Motor detección piezas
│   ├── detection_defectos_engine.py # Motor detección defectos
│   ├── piezas_processor.py         # Procesador piezas
│   └── defectos_processor.py       # Procesador defectos
├── segmentation/
│   ├── segmentation_defectos_engine.py # Motor segmentación defectos
│   ├── segmentation_piezas_engine.py   # Motor segmentación piezas
│   ├── defectos_segmentation_processor.py # Procesador segmentación defectos
│   └── piezas_segmentation_processor.py   # Procesador segmentación piezas
├── preprocessing/
│   └── illumination_robust.py      # Robustez a iluminación
├── postprocessing/
│   └── mask_fusion.py              # Fusión de máscaras
├── adaptive_thresholds.py          # Umbrales adaptativos
├── metadata_standard.py            # Estándar de metadatos
└── analysis_system.py              # Sistema integrado
```

#### Nuevos Modelos
```
Modelos/
├── CopleDetPz1C1V.onnx             # Detección piezas
├── clases_CopleDetPz1C1V.txt       # Clases detección piezas
├── CopleDetDef1C2V.onnx            # Detección defectos
├── clases_CopleDetDef1C2V.txt      # Clases detección defectos
├── CopleSegDef1C8V.onnx            # Segmentación defectos
├── clases_CopleSegDef1C8V.txt      # Clases segmentación defectos
├── CopleSegPZ1C1V.onnx             # Segmentación piezas
└── clases_CopleSegPZ1C1V.txt       # Clases segmentación piezas
```

### 🎯 Configuraciones Disponibles

#### Configuración de Robustez
```python
# Configuraciones predefinidas
CONSERVADORA = RobustezConfig(confianza_min=0.5, iou_threshold=0.35)
MODERADA = RobustezConfig(confianza_min=0.3, iou_threshold=0.2)  # Por defecto
AGRESIVA = RobustezConfig(confianza_min=0.2, iou_threshold=0.15)
EXTREMA = RobustezConfig(confianza_min=0.1, iou_threshold=0.1)
```

#### Configuración de Fusión
```python
# Parámetros de fusión de máscaras
FUSION_DISTANCIA_MAX = 50      # píxeles
FUSION_OVERLAP_MIN = 0.3       # ratio
FUSION_METODO = "promedio"     # método de fusión
```

#### Configuración de Webcam
```python
# Fallback automático
ENABLE_FALLBACK = True         # Habilitar fallback
DEFAULT_DEVICE_ID = 0          # ID dispositivo por defecto
WIDTH = 640                    # Ancho de imagen
HEIGHT = 640                   # Alto de imagen
FPS = 30                       # Frames por segundo
```

### 📊 Estadísticas y Monitoreo

#### Nuevas Métricas
- **Tipo de cámara** en uso (GigE o Webcam)
- **Tiempos de procesamiento** por módulo
- **Número de detecciones** por clase
- **Calidad de segmentación** (área, dimensiones)
- **Configuración activa** de robustez

#### Información Detallada
- **Estado de inicialización** de todos los módulos
- **Rendimiento de cámara** (FPS, buffers)
- **Uso de memoria** por modelo
- **Historial de procesamiento**

### 🚀 Casos de Uso Soportados

#### Desarrollo y Pruebas
- ✅ **Análisis con webcam** para desarrollo
- ✅ **Pruebas de módulos** individuales
- ✅ **Validación de algoritmos** de procesamiento
- ✅ **Debugging visual** de resultados

#### Producción Industrial
- ✅ **Análisis completo** de coples en línea
- ✅ **Control de calidad** automatizado
- ✅ **Detección de defectos** en tiempo real
- ✅ **Análisis dimensional** de piezas

#### Investigación
- ✅ **Análisis de segmentación** detallado
- ✅ **Estudio de robustez** a condiciones variables
- ✅ **Optimización de modelos** de machine learning
- ✅ **Análisis de rendimiento** del sistema

### 🔄 Migración desde Versión 1.0

#### Cambios de Configuración
- **Nuevos parámetros** en `config.py`
- **Configuraciones de robustez** agregadas
- **Configuración de webcam** incluida
- **Parámetros de fusión** de máscaras

#### Cambios de Uso
- **Nuevos comandos** en el menú principal
- **Opciones de configuración** adicionales
- **Estadísticas mejoradas** del sistema
- **Metadatos expandidos** en JSON

#### Compatibilidad
- ✅ **Retrocompatible** con configuraciones existentes
- ✅ **Modelos existentes** siguen funcionando
- ✅ **Estructura de salida** expandida pero compatible
- ✅ **APIs existentes** mantenidas

---

## [1.0.0] - 2024-12-01

### 🎉 Lanzamiento Inicial
- **Sistema básico** de clasificación de coples
- **Captura con cámara GigE** optimizada
- **Modelo de clasificación** ONNX
- **Interfaz de línea de comandos** básica
- **Guardado de resultados** en JSON

---

**Desarrollado por**: Ernesto Sánchez Céspedes/Controla  
**Versión actual**: 2.0.0  
**Última actualización**: Septiembre 2025
