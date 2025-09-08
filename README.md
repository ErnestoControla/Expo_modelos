# Sistema de Análisis de Coples

Sistema modular completo para análisis automático de coples utilizando modelos de machine learning ONNX, captura de imágenes con cámara GigE y fallback automático a webcam.

## 🎯 Características Principales

- **📷 Captura de imágenes** con cámara GigE optimizada para alta resolución
- **🔄 Fallback automático** a webcam cuando no hay cámara GigE disponible
- **🧠 Clasificación automática** de coples (Aceptado/Rechazado)
- **🎯 Detección de piezas** con localización precisa
- **🔍 Detección de defectos** con análisis detallado
- **🎨 Segmentación de defectos** con máscaras precisas
- **📐 Segmentación de piezas** con análisis dimensional
- **⚡ Procesamiento en tiempo real** con mínima latencia
- **🛡️ Sistema robusto** con configuración adaptativa
- **🔧 Sistema modular** completamente expandible
- **💾 Guardado automático** de imágenes y metadatos estandarizados

## 🏗️ Arquitectura del Sistema

```
Expo_modelos/
├── main.py                           # Punto de entrada principal
├── config.py                         # Configuración del sistema
├── utils.py                          # Utilidades comunes
├── requirements.txt                  # Dependencias del proyecto
├── modules/                          # Módulos del sistema
│   ├── capture/                      # Módulo de captura
│   │   ├── camera_controller.py      # Controlador cámara GigE
│   │   └── webcam_fallback.py        # Fallback a webcam
│   ├── classification/               # Módulo de clasificación
│   │   ├── inference_engine.py       # Motor de inferencia
│   │   └── image_processor.py        # Procesador de imágenes
│   ├── detection/                    # Módulo de detección
│   │   ├── detection_engine.py       # Motor detección piezas
│   │   ├── detection_defectos_engine.py # Motor detección defectos
│   │   ├── piezas_processor.py       # Procesador piezas
│   │   └── defectos_processor.py     # Procesador defectos
│   ├── segmentation/                 # Módulo de segmentación
│   │   ├── segmentation_defectos_engine.py # Motor segmentación defectos
│   │   ├── segmentation_piezas_engine.py   # Motor segmentación piezas
│   │   ├── defectos_segmentation_processor.py # Procesador segmentación defectos
│   │   └── piezas_segmentation_processor.py   # Procesador segmentación piezas
│   ├── preprocessing/                # Módulo de preprocesamiento
│   │   └── illumination_robust.py    # Robustez a iluminación
│   ├── postprocessing/               # Módulo de postprocesamiento
│   │   └── mask_fusion.py           # Fusión de máscaras
│   ├── adaptive_thresholds.py        # Umbrales adaptativos
│   ├── metadata_standard.py          # Estándar de metadatos
│   └── analysis_system.py            # Sistema integrado
├── Modelos/                          # Modelos ONNX
│   ├── CopleClasDef2C1V.onnx         # Clasificación
│   ├── clases_CopleClasDef2C1V.txt   # Clases clasificación
│   ├── CopleDetPz1C1V.onnx           # Detección piezas
│   ├── clases_CopleDetPz1C1V.txt     # Clases detección piezas
│   ├── CopleDetDef1C2V.onnx          # Detección defectos
│   ├── clases_CopleDetDef1C2V.txt    # Clases detección defectos
│   ├── CopleSegDef1C8V.onnx          # Segmentación defectos
│   ├── clases_CopleSegDef1C8V.txt    # Clases segmentación defectos
│   ├── CopleSegPZ1C1V.onnx           # Segmentación piezas
│   └── clases_CopleSegPZ1C1V.txt     # Clases segmentación piezas
└── Salida_cople/                     # Directorio de salida
    ├── Salida_clas_def/              # Clasificación
    ├── Salida_det_pz/                # Detección piezas
    ├── Salida_det_def/               # Detección defectos
    ├── Salida_seg_def/               # Segmentación defectos
    └── Salida_seg_pz/                # Segmentación piezas
```

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
cd /ruta/a/tu/proyecto
git clone <url-del-repositorio>
cd Expo_modelos
```

### 2. Crear entorno virtual (Recomendado)
```bash
conda create -n sapera python=3.10
conda activate sapera
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Verificar modelos
Asegúrate de que todos los archivos del modelo estén en el directorio `Modelos/`:

**Modelos de Clasificación:**
- `CopleClasDef2C1V.onnx` - Modelo de clasificación
- `clases_CopleClasDef2C1V.txt` - Archivo de clases

**Modelos de Detección:**
- `CopleDetPz1C1V.onnx` - Detección de piezas
- `clases_CopleDetPz1C1V.txt` - Clases de piezas
- `CopleDetDef1C2V.onnx` - Detección de defectos
- `clases_CopleDetDef1C2V.txt` - Clases de defectos

**Modelos de Segmentación:**
- `CopleSegDef1C8V.onnx` - Segmentación de defectos
- `clases_CopleSegDef1C8V.txt` - Clases de segmentación defectos
- `CopleSegPZ1C1V.onnx` - Segmentación de piezas
- `clases_CopleSegPZ1C1V.txt` - Clases de segmentación piezas

## 📷 Configuración de Cámara

### Cámara GigE (Recomendado)
El sistema está configurado para usar cámaras GigE con la siguiente configuración por defecto:
- **IP**: 172.16.1.21
- **Resolución nativa**: 4112x2176
- **ROI activo**: 640x640 (centrado)
- **Framerate**: 10 FPS
- **Exposición**: 20ms
- **Ganancia**: 2.0

### Fallback Automático a Webcam
Si no hay cámara GigE disponible, el sistema automáticamente:
1. **🔍 Detecta webcams** disponibles en el sistema
2. **📷 Inicializa la mejor** webcam encontrada
3. **🔄 Cambia transparentemente** al modo webcam
4. **✅ Mantiene toda la funcionalidad** del sistema

**Configuración de Webcam:**
- **Resolución**: 640x640 (redimensionado automáticamente)
- **FPS**: 30
- **Detección automática** de dispositivos (0-9)
- **Fallback habilitado** por defecto

Para cambiar la configuración, edita `config.py` en las secciones `CameraConfig` y `WebcamConfig`.

## 🎮 Uso del Sistema

### Ejecutar el sistema
```bash
conda activate sapera
python main.py
```

### Comandos disponibles

#### 📋 OPCIONES PRINCIPALES:
- **ENTER** - Análisis Completo (Recomendado)
- **'1'** - Análisis Completo
- **'2'** - Solo Clasificación
- **'3'** - Solo Detección de Piezas
- **'4'** - Solo Detección de Defectos
- **'5'** - Solo Segmentación de Defectos
- **'6'** - Solo Segmentación de Piezas

#### 🔧 OPCIONES AVANZADAS:
- **'v'** - Ver Frame Actual
- **'s'** - Estadísticas del Sistema
- **'c'** - Configuración
- **'r'** - Configuración de Robustez
- **'f'** - Configuración de Fusión de Máscaras
- **'q'** - Salir del Sistema

### Flujo de trabajo completo
1. **Inicialización**: El sistema configura la cámara (GigE o webcam) y carga todos los modelos
2. **Captura**: Se obtiene una imagen de la cámara
3. **Análisis completo**:
   - **Clasificación**: Determina si el cople es Aceptado/Rechazado
   - **Detección de piezas**: Localiza y cuenta piezas individuales
   - **Detección de defectos**: Identifica defectos específicos
   - **Segmentación de defectos**: Crea máscaras precisas de defectos
   - **Segmentación de piezas**: Analiza dimensiones y forma de piezas
4. **Resultado**: Se muestran todas las predicciones con confianza
5. **Guardado**: Se guardan imágenes anotadas y archivos JSON con metadatos estandarizados

## 📊 Salida del Sistema

### Imágenes
- **Formato**: JPG
- **Ubicación**: `Salida_cople/[módulo]/`
- **Anotaciones**: 
  - Etiquetas de clase con colores (Verde=Aceptado, Rojo=Rechazado)
  - Bounding boxes para detecciones
  - Máscaras de segmentación superpuestas
  - Información de confianza y tiempos

### Metadatos JSON Estandarizados
```json
{
  "archivo_imagen": "cople_analisis_20250905_181025_#1.jpg",
  "timestamp": "2025-09-05T18:10:25.123456",
  "resolucion": {
    "ancho": 640,
    "alto": 640,
    "canales": 3
  },
  "clasificacion": {
    "clase_predicha": "Aceptado",
    "confianza": 0.95,
    "tiempo_inferencia_ms": 45.8
  },
  "deteccion_piezas": {
    "numero_detecciones": 2,
    "detecciones": [
      {
        "clase": "Cople",
        "confianza": 0.92,
        "bbox": [100, 150, 200, 250],
        "area": 10000
      }
    ]
  },
  "deteccion_defectos": {
    "numero_detecciones": 1,
    "detecciones": [
      {
        "clase": "Defecto",
        "confianza": 0.88,
        "bbox": [300, 400, 350, 450],
        "area": 2500
      }
    ]
  },
  "segmentacion_defectos": {
    "numero_segmentaciones": 1,
    "segmentaciones": [
      {
        "clase": "Defecto",
        "confianza": 0.85,
        "bbox": [300, 400, 350, 450],
        "area_mascara": 2200,
        "coeficientes_mascara": [0.1, 0.2, ...]
      }
    ]
  },
  "segmentacion_piezas": {
    "numero_segmentaciones": 2,
    "segmentaciones": [
      {
        "clase": "Cople",
        "confianza": 0.91,
        "bbox": [100, 150, 200, 250],
        "area_mascara": 9500,
        "ancho_mascara": 100,
        "alto_mascara": 95,
        "coeficientes_mascara": [0.1, 0.2, ...]
      }
    ]
  },
  "tiempos": {
    "captura_ms": 15.2,
    "clasificacion_ms": 45.8,
    "deteccion_piezas_ms": 32.1,
    "deteccion_defectos_ms": 28.5,
    "segmentacion_defectos_ms": 156.3,
    "segmentacion_piezas_ms": 142.7,
    "total_ms": 420.6
  },
  "modelos": {
    "clasificacion": "CopleClasDef2C1V.onnx",
    "deteccion_piezas": "CopleDetPz1C1V.onnx",
    "deteccion_defectos": "CopleDetDef1C2V.onnx",
    "segmentacion_defectos": "CopleSegDef1C8V.onnx",
    "segmentacion_piezas": "CopleSegPZ1C1V.onnx"
  }
}
```

## 🔧 Configuración Avanzada

### Parámetros del modelo
Edita `config.py` para ajustar:
- **Umbrales de confianza** por módulo
- **Umbrales de IoU** para NMS
- **Tamaño de entrada** del modelo (640×640)
- **Proveedores ONNX** (CPU/GPU)
- **Configuración de threads**

### Configuración de robustez
El sistema incluye configuración adaptativa para diferentes condiciones:

**Configuraciones disponibles:**
- **Conservadora**: Confianza 0.5, IoU 0.35 (máxima precisión)
- **Moderada**: Confianza 0.3, IoU 0.2 (balanceada) - **Por defecto**
- **Agresiva**: Confianza 0.2, IoU 0.15 (máxima sensibilidad)
- **Extrema**: Confianza 0.1, IoU 0.1 (condiciones muy difíciles)

### Configuración de fusión de máscaras
Para manejar máscaras superpuestas:
- **Distancia máxima**: 50 píxeles
- **Overlap mínimo**: 0.3
- **Método de fusión**: Promedio ponderado

### Parámetros de cámara
- **Tiempo de exposición**
- **Framerate**
- **Tamaño de ROI**
- **Configuración de buffers**
- **Ganancia**

### Configuración del ROI
El sistema utiliza un ROI (Region of Interest) de 640×640 píxeles centrado en la imagen nativa de 4112×2176:
- **Resolución nativa**: 4112×2176 píxeles
- **ROI activo**: 640×640 píxeles
- **Offset X**: 1736 píxeles (centrado horizontalmente)
- **Offset Y**: 768 píxeles (centrado verticalmente)
- **Área de captura**: Centro de la imagen para máxima calidad
- **Formato de pixel**: Bayer RG8 (8 bits por canal)

## 🛡️ Características de Robustez

### Robustez a Iluminación
- **Normalización adaptativa** de imágenes
- **CLAHE** (Contrast Limited Adaptive Histogram Equalization)
- **Corrección gamma** automática
- **Mejora de contraste** adaptativa
- **Análisis de iluminación** en tiempo real

### Umbrales Adaptativos
- **Ajuste dinámico** basado en condiciones ambientales
- **Factor de brillo** y contraste
- **Historial de detecciones** para optimización
- **Configuración híbrida** automática

### Fusión de Máscaras
- **Detección automática** de objetos pegados
- **Cálculo de distancia** entre máscaras
- **Fusión inteligente** de máscaras superpuestas
- **Preservación de calidad** de segmentación

## 📈 Monitoreo y Estadísticas

El sistema proporciona estadísticas detalladas en tiempo real:

### Estadísticas de Cámara
- **Tipo de cámara** (GigE o Webcam Fallback)
- **FPS de cámara** y promedio
- **Frames capturados** totales
- **Tiempos de captura** (promedio y desviación)
- **Estado de buffers**

### Estadísticas de Modelos
- **Tiempos de inferencia** por módulo
- **Número de detecciones** por clase
- **Confianza promedio** de predicciones
- **Uso de memoria** por modelo

### Estadísticas del Sistema
- **Resultados procesados** totales
- **Tiempo total** de procesamiento
- **Estado de inicialización** de módulos
- **Configuración activa** de robustez

## 🐛 Solución de Problemas

### Error: "ONNX Runtime no disponible"
```bash
pip install onnxruntime
```

### Error: "No se encontró cámara en IP"
- Verifica la conexión de red
- Confirma la IP de la cámara
- Revisa la configuración en `config.py`
- El sistema automáticamente usará webcam como fallback

### Error: "Modelo no encontrado"
- Verifica que todos los archivos `.onnx` estén en `Modelos/`
- Confirma que los archivos de clases existen
- Revisa permisos de archivo

### Error: "No hay frames disponibles"
- Verifica que la cámara esté conectada
- Revisa la configuración de la cámara
- El sistema automáticamente detectará y usará webcam

### Rendimiento lento
- Ajusta la configuración de robustez (usa "Conservadora")
- Reduce la resolución de entrada (actualmente 640×640)
- Ajusta el framerate de la cámara
- Optimiza la configuración de threads ONNX
- Verifica la configuración de buffers

### Problemas con segmentación
- Ajusta los filtros de calidad en `segmentation_piezas_engine.py`
- Configura la fusión de máscaras para objetos pegados
- Revisa los umbrales de confianza para segmentación

## 🚀 Características Avanzadas

### Sistema de Fallback Inteligente
- **Detección automática** de cámaras disponibles
- **Selección inteligente** de la mejor webcam
- **Transición transparente** entre tipos de cámara
- **Mantenimiento de funcionalidad** completa

### Metadatos Estandarizados
- **Estructura JSON** consistente
- **Información completa** de todos los módulos
- **Tiempos detallados** de procesamiento
- **Metadatos de modelos** utilizados

### Configuración Adaptativa
- **Umbrales dinámicos** basados en condiciones
- **Configuración de robustez** automática
- **Fusión de máscaras** inteligente
- **Optimización continua** de rendimiento

## 📋 Requisitos del Sistema

### Hardware Mínimo
- **CPU**: Intel i5 o equivalente
- **RAM**: 8GB (recomendado 16GB)
- **Almacenamiento**: 2GB libres
- **Cámara**: GigE o webcam USB

### Software
- **Python**: 3.10+
- **OpenCV**: 4.12.0+
- **ONNX Runtime**: 1.22.1+
- **NumPy**: 2.2.6+

### Dependencias Principales
```
opencv-python>=4.12.0
onnxruntime>=1.22.1
numpy>=2.2.6
```

## 🎯 Casos de Uso

### Desarrollo y Pruebas
- **Uso con webcam** para desarrollo sin hardware industrial
- **Pruebas de modelos** individuales
- **Validación de algoritmos** de procesamiento

### Producción Industrial
- **Análisis completo** de coples en línea
- **Control de calidad** automatizado
- **Detección de defectos** en tiempo real
- **Análisis dimensional** de piezas

### Investigación y Desarrollo
- **Análisis de segmentación** detallado
- **Estudio de robustez** a condiciones variables
- **Optimización de modelos** de machine learning

---

**Desarrollado por**: Ernesto Sánchez Céspedes/Controla  
**Versión**: 2.0.0  
**Última actualización**: Septiembre 2025  
**Estado**: ✅ **COMPLETAMENTE FUNCIONAL**