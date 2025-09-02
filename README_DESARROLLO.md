# README de Desarrollo - Sistema de Análisis de Coples

## 🏗️ Arquitectura del Sistema

### Estructura del Proyecto
```
Expo_modelos/
├── main.py                 # Punto de entrada principal del sistema
├── config.py               # Configuración centralizada del sistema
├── utils.py                # Utilidades comunes y funciones auxiliares
├── requirements.txt        # Dependencias del proyecto
├── modules/                # Módulos del sistema
│   ├── capture/            # Módulo de captura de imágenes
│   │   └── camera_controller.py  # Controlador de cámara GigE
│   ├── classification/     # Módulo de clasificación
│   │   ├── inference_engine.py   # Motor de inferencia ONNX
│   │   └── image_processor.py    # Procesamiento de imágenes
│   ├── detection/          # Módulo de detección (futuro)
│   │   └── __init__.py
│   └── segmentation/       # Módulo de segmentación (futuro)
│       └── __init__.py
├── Modelos/                # Modelos ONNX y archivos de clases
│   ├── CopleClasDef2C1V.onnx     # Modelo de clasificación
│   ├── clases_CopleClasDef2C1V.txt
│   └── [otros modelos futuros...]
├── gigev_common/           # Biblioteca común para GigE (en directorio padre)
└── Salida_cople/           # Directorio de salida de resultados
```

## 🔧 Implementación Técnica

### Base del Sistema
El sistema está **basado en la implementación probada** del proyecto `Coples-Gigev`, adaptado para:
- **ROI 640×640** (en lugar de 1280×1024)
- **Resolución nativa 4112×2176** de la cámara Teledyne DALSA
- **Formato de pixel Bayer RG8** para captura de imágenes

### Módulo de Captura (`modules/capture/`)

#### `camera_controller.py`
- **Clase**: `CamaraTiempoOptimizada`
- **Implementación**: Copiada del proyecto `Coples-Gigev`
- **Características**:
  - Captura asíncrona continua con doble buffer
  - Optimizado para resolución 640×640
  - Procesamiento en tiempo real con mínima latencia
  - Gestión automática de memoria
  - Estadísticas de rendimiento en tiempo real

#### Configuración de Cámara
```python
# Parámetros de captura optimizados
EXPOSURE_TIME = 20000      # 20ms - tiempo de exposición optimizado
FRAMERATE = 10.0          # 10 FPS - reducido para menor carga CPU
PACKET_SIZE = 9000        # Tamaño de paquete jumbo
NUM_BUFFERS = 2           # Solo 2 buffers para minimizar memoria
GAIN = 2.0               # Ganancia mínima para mejor calidad

# Configuración del ROI
ROI_WIDTH = 640
ROI_HEIGHT = 640
ROI_OFFSET_X = 1736      # Centrado en imagen 4112×2176
ROI_OFFSET_Y = 768       # Centrado en imagen 4112×2176
```

#### Sistema de Buffers
- **Doble buffer asíncrono** para captura continua
- **Payload size**: Calculado automáticamente por la cámara
- **Buffer margin**: 8192 bytes extra para estabilidad
- **Gestión de memoria**: Automática con cleanup

### Módulo de Clasificación (`modules/classification/`)

#### `inference_engine.py`
- **Motor ONNX**: Carga y ejecuta modelos de clasificación
- **Preprocesamiento**: Resize a 640×640, normalización, transposición HWC→CHW
- **Postprocesamiento**: Softmax para obtener probabilidades de clase
- **Optimización**: CPU execution provider con configuración de threads

#### `image_processor.py`
- **Anotaciones visuales**: Etiquetas de clase con colores
- **Información de tiempo**: Captura, inferencia y total
- **Formato de salida**: JPG con anotaciones superpuestas

## 📊 Configuración del Sistema

### Archivo `config.py`
Configuración centralizada en clases:

#### `CameraConfig`
```python
class CameraConfig:
    DEFAULT_IP = "172.16.1.21"
    MAX_CAMERAS = 16
    EXPOSURE_TIME = 20000
    FRAMERATE = 10.0
    PACKET_SIZE = 9000
    NUM_BUFFERS = 2
    GAIN = 2.0
    ROI_WIDTH = 640
    ROI_HEIGHT = 640
    ROI_OFFSET_X = 1736
    ROI_OFFSET_Y = 768
    FRAME_TIMEOUT = 0.1
    STARTUP_TIMEOUT = 5.0
    SHUTDOWN_TIMEOUT = 2.0
```

#### `ModelsConfig`
```python
class ModelsConfig:
    MODELS_DIR = "Modelos"
    CLASSIFICATION_MODEL = "CopleClasDef2C1V.onnx"
    CLASSIFICATION_CLASSES = "clases_CopleClasDef2C1V.txt"
    INPUT_SIZE = 640
    CONFIDENCE_THRESHOLD = 0.3
    MAX_DETECTIONS = 10
    INTRA_OP_THREADS = 2
    INTER_OP_THREADS = 2
    PROVIDERS = ['CPUExecutionProvider']
```

#### `GlobalConfig`
```python
class GlobalConfig:
    GIGEV_COMMON_PATH = "../gigev_common"
    BUFFER_MARGIN = 8192  # Margen extra para buffers
    DEBUG_MODE = True
    SAVE_ORIGINAL_IMAGES = True
```

## 🚀 Flujo de Ejecución

### 1. Inicialización del Sistema
```python
# main.py
def inicializar_sistema():
    # 1. Cargar clases de clasificación
    # 2. Configurar cámara GigE
    # 3. Inicializar motor de clasificación
    # 4. Iniciar captura continua
```

### 2. Captura de Imágenes
```python
# camera_controller.py
def _thread_captura_continua():
    # 1. Iniciar transferencia GigE
    # 2. Esperar frames con timeout
    # 3. Procesar frames asíncronamente
    # 4. Rotar buffers
```

### 3. Procesamiento de Frames
```python
def _procesar_frame_async(gevbufPtr):
    # 1. Extraer datos del buffer GigE
    # 2. Reshape a 640×640
    # 3. Conversión Bayer RG8 → RGB
    # 4. Almacenar en buffer de escritura
```

### 4. Clasificación
```python
# inference_engine.py
def clasificar_imagen(imagen):
    # 1. Preprocesar imagen (resize, normalizar, transponer)
    # 2. Ejecutar inferencia ONNX
    # 3. Postprocesar resultados (softmax)
    # 4. Retornar clase y confianza
```

### 5. Guardado de Resultados
```python
# image_processor.py
def guardar_resultado(imagen, resultado, timestamp):
    # 1. Anotar imagen con etiquetas
    # 2. Guardar imagen JPG
    # 3. Crear JSON con metadatos
    # 4. Guardar ambos archivos
```

## 🔍 Debug y Monitoreo

### Estadísticas del Sistema
- **FPS real**: Frames por segundo de captura
- **Tiempos de captura**: Promedio, min, max, std
- **Tiempos de procesamiento**: Promedio, min, max, std
- **Buffers listos**: Estado de los buffers de captura

### Comandos de Debug
```bash
# Ver frame sin clasificar
v

# Mostrar estadísticas
s

# Mostrar configuración
c

# Cambiar umbral de confianza
t
```

### Logs del Sistema
- **Configuración de cámara**: Parámetros aplicados
- **Estado de buffers**: Asignación y tamaño
- **Procesamiento de frames**: Conversión Bayer y reshape
- **Errores y warnings**: Manejo de excepciones

## 🚧 Módulos Futuros

### Estructura Preparada
```
modules/
├── detection/
│   ├── __init__.py
│   ├── detection_engine.py      # Futuro
│   └── bbox_processor.py        # Futuro
└── segmentation/
    ├── __init__.py
    ├── segmentation_engine.py   # Futuro
    └── mask_processor.py        # Futuro
```

### Modelos Futuros
1. **`CopleDetDef1C2V.onnx`** - Detección de defectos
2. **`CopleDetPZ1C1V.onnx`** - Detección de piezas
3. **`CopleSegDef1C8V.onnx`** - Segmentación de defectos
4. **`CopleSegPz1C1V.onnx`** - Segmentación de piezas

## 🐛 Solución de Problemas

### Problemas Comunes

#### 1. Imagen con Ruido
**Síntoma**: Imagen de salida es ruido colorido
**Causa**: Implementación incorrecta del procesamiento de buffer
**Solución**: Usar la implementación del proyecto `Coples-Gigev`

#### 2. Error de Buffer
**Síntoma**: `BUFFER_MARGIN not found`
**Causa**: Constante faltante en `config.py`
**Solución**: Agregar `BUFFER_MARGIN = 8192`

#### 3. ROI Incorrecto
**Síntoma**: Imagen parcialmente negra
**Causa**: Offset del ROI mal calculado
**Solución**: Usar offsets centrados (1736, 768)

#### 4. Error de Cámara Ocupada
**Síntoma**: `GevStartTransfer status = -20`
**Causa**: Cámara no liberada correctamente
**Solución**: Esperar 3 segundos después de liberar recursos

### Debug del Sistema
```python
# Agregar en camera_controller.py
print(f"🔍 Debug buffer: status={gevbuf.status}, recv_size={gevbuf.recv_size}")
print(f"🔍 Debug datos: shape={raw_data.shape}, dtype={raw_data.dtype}")
print(f"🔍 Debug imagen: shape={frame_rgb.shape}, dtype={frame_rgb.dtype}")
```

## 📈 Optimización y Rendimiento

### Configuración de Cámara
- **Framerate**: 10 FPS (balance entre calidad y rendimiento)
- **Exposición**: 20ms (optimizado para iluminación)
- **Buffers**: 2 buffers (mínimo para estabilidad)
- **Packet size**: 9000 bytes (jumbo frames)

### Configuración ONNX
- **Threads**: 2 intra-op, 2 inter-op
- **Provider**: CPUExecutionProvider
- **Input size**: 640×640 (fijo para el modelo)

### Monitoreo de Memoria
- **Cleanup automático**: Liberación de buffers
- **Gestión de memoria**: Control de arrays NumPy
- **Estadísticas**: Uso de memoria en tiempo real

## 🔄 Mantenimiento y Actualizaciones

### Actualización de Modelos
1. **Reemplazar archivo .onnx** en `Modelos/`
2. **Actualizar archivo de clases** correspondiente
3. **Modificar `config.py`** si cambia el input size
4. **Probar clasificación** con nuevas imágenes

### Actualización de Configuración
1. **Modificar parámetros** en `config.py`
2. **Reiniciar sistema** para aplicar cambios
3. **Verificar funcionamiento** con comandos de debug
4. **Documentar cambios** en este README

### Backup y Versionado
- **Git**: Control de versiones del código
- **Modelos**: Backup de archivos .onnx
- **Configuración**: Backup de `config.py`
- **Documentación**: Sincronización con implementación

---

**Desarrollado por**: Equipo de Desarrollo  
**Versión**: 1.0.0  
**Última actualización**: Septiembre 2025  
**Base del proyecto**: Coples-Gigev (implementación probada)
