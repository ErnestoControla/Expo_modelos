# Documentación Técnica - Sistema de Análisis de Coples

## 🏗️ Arquitectura del Sistema

### Visión General
El sistema está diseñado con una arquitectura modular que permite la integración de múltiples modelos de machine learning para el análisis completo de coples. Cada módulo es independiente y puede funcionar por separado o en conjunto.

### Componentes Principales

#### 1. Sistema de Captura (`modules/capture/`)
- **`camera_controller.py`**: Controlador de cámara GigE optimizado
- **`webcam_fallback.py`**: Sistema de fallback automático a webcam

#### 2. Sistema de Clasificación (`modules/classification/`)
- **`inference_engine.py`**: Motor de inferencia ONNX para clasificación
- **`image_processor.py`**: Procesador de imágenes para clasificación

#### 3. Sistema de Detección (`modules/detection/`)
- **`detection_engine.py`**: Motor de detección de piezas
- **`detection_defectos_engine.py`**: Motor de detección de defectos
- **`piezas_processor.py`**: Procesador de resultados de piezas
- **`defectos_processor.py`**: Procesador de resultados de defectos

#### 4. Sistema de Segmentación (`modules/segmentation/`)
- **`segmentation_defectos_engine.py`**: Motor de segmentación de defectos
- **`segmentation_piezas_engine.py`**: Motor de segmentación de piezas
- **`defectos_segmentation_processor.py`**: Procesador de segmentación de defectos
- **`piezas_segmentation_processor.py`**: Procesador de segmentación de piezas

#### 5. Sistema de Preprocesamiento (`modules/preprocessing/`)
- **`illumination_robust.py`**: Técnicas de robustez a iluminación

#### 6. Sistema de Postprocesamiento (`modules/postprocessing/`)
- **`mask_fusion.py`**: Fusión de máscaras superpuestas

#### 7. Sistema Integrado (`modules/analysis_system.py`)
- **`SistemaAnalisisIntegrado`**: Orquestador principal del sistema

## 🔧 APIs y Interfaces

### Sistema de Captura

#### CamaraTiempoOptimizada
```python
class CamaraTiempoOptimizada:
    def __init__(self, ip=None)
    def configurar_camara(self) -> bool
    def iniciar_captura_continua(self) -> bool
    def obtener_frame_instantaneo(self) -> Tuple[np.ndarray, float, float]
    def liberar(self)
    def obtener_estadisticas(self) -> dict
```

#### WebcamFallback
```python
class WebcamFallback:
    def __init__(self, device_id=0, width=640, height=640)
    def detectar_webcams_disponibles(self) -> list
    def inicializar(self, device_id=None) -> bool
    def iniciar_captura_continua(self) -> bool
    def obtener_frame_instantaneo(self) -> Tuple[np.ndarray, float, float]
    def obtener_frame_sincrono(self) -> Tuple[np.ndarray, float, float]
    def liberar_recursos(self)
    def obtener_estadisticas(self) -> dict
```

### Sistema de Clasificación

#### ClasificadorCoplesONNX
```python
class ClasificadorCoplesONNX:
    def __init__(self)
    def inicializar(self) -> bool
    def clasificar(self, imagen: np.ndarray) -> Tuple[str, float, float]
    def liberar(self)
```

### Sistema de Detección

#### DetectorPiezasCoples
```python
class DetectorPiezasCoples:
    def __init__(self)
    def detectar(self, imagen: np.ndarray) -> List[Dict]
    def actualizar_umbrales(self, confianza_min: float, iou_threshold: float)
    def liberar(self)
    def obtener_estadisticas(self) -> dict
```

#### DetectorDefectosCoples
```python
class DetectorDefectosCoples:
    def __init__(self)
    def detectar(self, imagen: np.ndarray) -> List[Dict]
    def actualizar_umbrales(self, confianza_min: float, iou_threshold: float)
    def liberar(self)
    def obtener_estadisticas(self) -> dict
```

### Sistema de Segmentación

#### SegmentadorDefectosCoples
```python
class SegmentadorDefectosCoples:
    def __init__(self)
    def segmentar(self, imagen: np.ndarray) -> List[Dict]
    def liberar(self)
    def obtener_estadisticas(self) -> dict
```

#### SegmentadorPiezasCoples
```python
class SegmentadorPiezasCoples:
    def __init__(self)
    def segmentar(self, imagen: np.ndarray) -> List[Dict]
    def configurar_filtros(self, **kwargs)
    def obtener_filtros_actuales(self) -> dict
    def liberar(self)
    def obtener_estadisticas(self) -> dict
```

### Sistema Integrado

#### SistemaAnalisisIntegrado
```python
class SistemaAnalisisIntegrado:
    def __init__(self)
    def inicializar(self) -> bool
    def capturar_imagen_unica(self) -> Dict
    def analisis_completo(self, imagen: np.ndarray) -> Dict
    def solo_clasificacion(self, imagen: np.ndarray) -> Dict
    def solo_deteccion_piezas(self, imagen: np.ndarray) -> Dict
    def solo_deteccion_defectos(self, imagen: np.ndarray) -> Dict
    def solo_segmentacion_defectos(self, imagen: np.ndarray) -> Dict
    def solo_segmentacion_piezas(self, imagen: np.ndarray) -> Dict
    def aplicar_configuracion_robustez(self, configuracion: str)
    def configurar_fusion_mascaras(self, **kwargs)
    def obtener_estadisticas(self) -> Dict
    def liberar(self)
```

## 📊 Estructura de Datos

### Formato de Detección
```python
{
    "clase": str,           # Nombre de la clase detectada
    "confianza": float,     # Confianza de la detección (0.0-1.0)
    "bbox": List[int],      # [x1, y1, x2, y2] coordenadas del bounding box
    "area": int             # Área del bounding box en píxeles
}
```

### Formato de Segmentación
```python
{
    "clase": str,                    # Nombre de la clase segmentada
    "confianza": float,              # Confianza de la segmentación (0.0-1.0)
    "bbox": List[int],               # [x1, y1, x2, y2] coordenadas del bounding box
    "area_mascara": int,             # Área de la máscara en píxeles
    "ancho_mascara": int,            # Ancho de la máscara (solo piezas)
    "alto_mascara": int,             # Alto de la máscara (solo piezas)
    "coeficientes_mascara": List[float]  # Coeficientes de la máscara comprimida
}
```

### Formato de Metadatos Estandarizados
```python
{
    "archivo_imagen": str,           # Nombre del archivo de imagen
    "timestamp": str,                # Timestamp ISO de la captura
    "resolucion": {                  # Información de resolución
        "ancho": int,
        "alto": int,
        "canales": int
    },
    "clasificacion": {               # Resultados de clasificación
        "clase_predicha": str,
        "confianza": float,
        "tiempo_inferencia_ms": float
    },
    "deteccion_piezas": {            # Resultados de detección de piezas
        "numero_detecciones": int,
        "detecciones": List[Dict]
    },
    "deteccion_defectos": {          # Resultados de detección de defectos
        "numero_detecciones": int,
        "detecciones": List[Dict]
    },
    "segmentacion_defectos": {       # Resultados de segmentación de defectos
        "numero_segmentaciones": int,
        "segmentaciones": List[Dict]
    },
    "segmentacion_piezas": {         # Resultados de segmentación de piezas
        "numero_segmentaciones": int,
        "segmentaciones": List[Dict]
    },
    "tiempos": {                     # Tiempos de procesamiento
        "captura_ms": float,
        "clasificacion_ms": float,
        "deteccion_piezas_ms": float,
        "deteccion_defectos_ms": float,
        "segmentacion_defectos_ms": float,
        "segmentacion_piezas_ms": float,
        "total_ms": float
    },
    "modelos": {                     # Información de modelos utilizados
        "clasificacion": str,
        "deteccion_piezas": str,
        "deteccion_defectos": str,
        "segmentacion_defectos": str,
        "segmentacion_piezas": str
    }
}
```

## ⚙️ Configuración Técnica

### Configuración de Cámara GigE
```python
class CameraConfig:
    DEFAULT_IP = "172.16.1.21"
    MAX_CAMERAS = 16
    NATIVE_WIDTH = 4112
    NATIVE_HEIGHT = 2176
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

### Configuración de Webcam
```python
class WebcamConfig:
    ENABLE_FALLBACK = True
    DEFAULT_DEVICE_ID = 0
    WIDTH = 640
    HEIGHT = 640
    FPS = 30
    MAX_DEVICES_TO_CHECK = 10
    DETECTION_TIMEOUT = 3.0
    INIT_TIMEOUT = 5.0
```

### Configuración de Modelos
```python
class ModelsConfig:
    MODELS_DIR = "Modelos"
    CLASSIFICATION_MODEL = "CopleClasDef2C1V.onnx"
    CLASSIFICATION_CLASSES = "clases_CopleClasDef2C1V.txt"
    DETECTION_DEFECTOS_MODEL = "CopleDetDef1C2V.onnx"
    DETECTION_DEFECTOS_CLASSES = "clases_CopleDetDef1C2V.txt"
    DETECTION_PIEZAS_MODEL = "CopleDetPz1C1V.onnx"
    DETECTION_PIEZAS_CLASSES = "clases_CopleDetPz1C1V.txt"
    SEGMENTATION_DEFECTOS_MODEL = "CopleSegDef1C8V.onnx"
    SEGMENTATION_DEFECTOS_CLASSES = "clases_CopleSegDef1C8V.txt"
    SEGMENTATION_PARTS_MODEL = "CopleSegPZ1C1V.onnx"
    SEGMENTATION_PARTS_CLASSES = "clases_CopleSegPZ1C1V.txt"
```

### Configuración de Robustez
```python
class RobustezConfig:
    def __init__(self, confianza_min: float, iou_threshold: float, nombre: str, descripcion: str)

# Configuraciones predefinidas
CONSERVADORA = RobustezConfig(0.5, 0.35, "Conservadora", "máxima precisión")
MODERADA = RobustezConfig(0.3, 0.2, "Moderada", "mejor rendimiento en condiciones difíciles")
AGRESIVA = RobustezConfig(0.2, 0.15, "Agresiva", "máxima sensibilidad")
EXTREMA = RobustezConfig(0.1, 0.1, "Extrema", "condiciones muy difíciles")
```

### Configuración de Fusión
```python
class FusionConfig:
    DISTANCIA_MAX = 50
    OVERLAP_MIN = 0.3
    METODO = "promedio"
    HABILITADO = True
```

## 🔄 Flujo de Procesamiento

### 1. Inicialización del Sistema
```python
sistema = SistemaAnalisisIntegrado()
sistema.inicializar()
```

**Pasos internos:**
1. Inicializar cámara (GigE o webcam fallback)
2. Cargar y inicializar todos los modelos ONNX
3. Configurar procesadores de cada módulo
4. Iniciar captura continua
5. Aplicar configuración de robustez por defecto

### 2. Análisis Completo
```python
resultado = sistema.analisis_completo(imagen)
```

**Pasos internos:**
1. Capturar imagen de la cámara
2. Ejecutar clasificación
3. Ejecutar detección de piezas
4. Ejecutar detección de defectos
5. Ejecutar segmentación de defectos
6. Ejecutar segmentación de piezas
7. Aplicar fusión de máscaras si es necesario
8. Generar metadatos estandarizados
9. Guardar resultados

### 3. Análisis por Módulos Individuales
```python
# Solo clasificación
resultado = sistema.solo_clasificacion(imagen)

# Solo detección de piezas
resultado = sistema.solo_deteccion_piezas(imagen)

# Solo detección de defectos
resultado = sistema.solo_deteccion_defectos(imagen)

# Solo segmentación de defectos
resultado = sistema.solo_segmentacion_defectos(imagen)

# Solo segmentación de piezas
resultado = sistema.solo_segmentacion_piezas(imagen)
```

## 🛡️ Sistema de Robustez

### Robustez a Iluminación
```python
class RobustezIluminacion:
    def normalizar_imagen_adaptativa(self, imagen: np.ndarray) -> np.ndarray
    def aplicar_clahe(self, imagen: np.ndarray) -> np.ndarray
    def aplicar_gamma(self, imagen: np.ndarray, gamma: float) -> np.ndarray
    def mejorar_contraste(self, imagen: np.ndarray) -> np.ndarray
    def analizar_iluminacion(self, imagen: np.ndarray) -> Dict
    def recomendar_ajustes(self, analisis: Dict) -> Dict
    def preprocesar_imagen_robusta(self, imagen: np.ndarray) -> np.ndarray
```

### Umbrales Adaptativos
```python
class UmbralesAdaptativos:
    def obtener_umbrales_hibridos(self, imagen: np.ndarray, historial: List) -> Tuple[float, float]
    def _calcular_factor_brillo(self, imagen: np.ndarray) -> float
    def _calcular_factor_contraste(self, imagen: np.ndarray) -> float
    def _obtener_umbrales_base(self, configuracion: str) -> Tuple[float, float]
```

### Fusión de Máscaras
```python
class FusionadorMascaras:
    def procesar_segmentaciones(self, segmentaciones: List[Dict]) -> List[Dict]
    def _detectar_objetos_pegados(self, segmentaciones: List[Dict]) -> List[List[int]]
    def _calcular_distancia_mascaras(self, seg1: Dict, seg2: Dict) -> float
    def _calcular_overlap_mascaras(self, seg1: Dict, seg2: Dict) -> float
    def _fusionar_mascaras(self, segmentaciones: List[Dict]) -> Dict
```

## 📈 Monitoreo y Debugging

### Estadísticas del Sistema
```python
stats = sistema.obtener_estadisticas()
```

**Información disponible:**
- Estado de inicialización de cada módulo
- Tiempos de procesamiento por módulo
- Número de resultados procesados
- Configuración activa de robustez
- Información de cámara (tipo, FPS, buffers)
- Uso de memoria por modelo

### Logging y Debugging
```python
# Configuración de logging
import logging
logging.basicConfig(level=logging.INFO)

# Logs específicos por módulo
logger = logging.getLogger(__name__)
logger.info("Mensaje de información")
logger.warning("Mensaje de advertencia")
logger.error("Mensaje de error")
```

### Visualización de Resultados
```python
# Mostrar frame actual
frame, tiempo, timestamp = sistema.obtener_frame_simple()
cv2.imshow("Frame Actual", frame)
cv2.waitKey(0)

# Mostrar estadísticas
stats = sistema.obtener_estadisticas()
print(json.dumps(stats, indent=2))
```

## 🔧 Extensibilidad

### Agregar Nuevos Módulos
1. Crear nuevo motor de inferencia en `modules/[categoria]/`
2. Crear procesador correspondiente
3. Agregar configuración en `config.py`
4. Integrar en `SistemaAnalisisIntegrado`
5. Actualizar menú en `main.py`

### Agregar Nuevos Modelos
1. Colocar archivo `.onnx` en `Modelos/`
2. Crear archivo de clases correspondiente
3. Actualizar `ModelsConfig` en `config.py`
4. Crear motor de inferencia específico
5. Integrar en el sistema

### Personalizar Configuraciones
1. Modificar parámetros en `config.py`
2. Crear nuevas configuraciones de robustez
3. Ajustar parámetros de fusión
4. Personalizar umbrales por módulo

## 🚀 Optimización de Rendimiento

### Configuración de ONNX
```python
# Proveedores disponibles
providers = ['CPUExecutionProvider', 'CUDAExecutionProvider']

# Configuración de threads
session_options = onnxruntime.SessionOptions()
session_options.intra_op_num_threads = 4
session_options.inter_op_num_threads = 4
```

### Gestión de Memoria
```python
# Liberación explícita de recursos
sistema.liberar()

# Limpieza de memoria
import gc
gc.collect()
```

### Optimización de Cámara
```python
# Configuración de buffers
NUM_BUFFERS = 2  # Mínimo para reducir memoria
PACKET_SIZE = 9000  # Tamaño de paquete jumbo

# Configuración de ROI
ROI_WIDTH = 640  # Reducir resolución si es necesario
ROI_HEIGHT = 640
```

---

**Desarrollado por**: Ernesto Sánchez Céspedes/Controla  
**Versión**: 2.0.0  
**Última actualización**: Septiembre 2025
