"""
Configuración del sistema de análisis de coples
Contiene todas las constantes y parámetros configurables
"""

import os

# ==================== CONFIGURACIÓN DE CÁMARA ====================
class CameraConfig:
    """Configuración de la cámara GigE"""
    
    # Conexión
    DEFAULT_IP = "172.16.1.21"
    MAX_CAMERAS = 16
    
    # Resolución nativa de la cámara
    NATIVE_WIDTH = 4112
    NATIVE_HEIGHT = 2176
    
    # Parámetros de captura optimizados para resolución estándar
    EXPOSURE_TIME = 20000      # 20ms - tiempo de exposición optimizado
    FRAMERATE = 10.0          # 10 FPS - reducido para menor carga CPU
    PACKET_SIZE = 9000        # Tamaño de paquete jumbo
    NUM_BUFFERS = 2           # Solo 2 buffers para minimizar memoria
    GAIN = 2.0               # Ganancia mínima para mejor calidad
    
    # Configuración del ROI
    ROI_WIDTH = 640
    ROI_HEIGHT = 640
    ROI_OFFSET_X = 1736      # Centrado horizontalmente: (4112 - 640) / 2
    ROI_OFFSET_Y = 768       # Centrado verticalmente: (2176 - 640) / 2
    
    # Timeouts (en segundos)
    FRAME_TIMEOUT = 0.1       # 100ms timeout para frames
    STARTUP_TIMEOUT = 5.0     # 5s timeout para primer frame
    SHUTDOWN_TIMEOUT = 2.0    # 2s timeout para cerrar thread

# ==================== CONFIGURACIÓN DE MODELOS ====================
class ModelsConfig:
    """Configuración de los modelos ONNX"""
    
    # Directorio de modelos
    MODELS_DIR = "Modelos"
    
    # Modelo de clasificación
    CLASSIFICATION_MODEL = "CopleClasDef2C1V.onnx"
    CLASSIFICATION_CLASSES = "clases_CopleClasDef2C1V.txt"
    
    # Modelos futuros
    DETECTION_DEFECTS_MODEL = "CopleDetDef1C2V.onnx"
    DETECTION_PARTS_MODEL = "CopleDetPZ1C1V.onnx"
    SEGMENTATION_DEFECTS_MODEL = "CopleSegDef1C8V.onnx"
    SEGMENTATION_PARTS_MODEL = "CopleSegPz1C1V.onnx"
    
    # Parámetros de inferencia
    INPUT_SIZE = 640          # Resolución del modelo (640x640)
    CONFIDENCE_THRESHOLD = 0.3
    MAX_DETECTIONS = 10
    
    # Configuración ONNX
    INTRA_OP_THREADS = 2
    INTER_OP_THREADS = 2
    PROVIDERS = ['CPUExecutionProvider']

# ==================== CONFIGURACIÓN DE VISUALIZACIÓN ====================
class VisualizationConfig:
    """Configuración de visualización y colores"""
    
    # Colores para clasificación (BGR format)
    ACCEPTED_COLOR = (0, 255, 0)        # Verde para "Aceptado"
    REJECTED_COLOR = (0, 0, 255)        # Rojo para "Rechazado"
    TEXT_COLOR = (255, 255, 255)        # Blanco para texto
    BACKGROUND_COLOR = (0, 0, 0)        # Negro para fondo
    
    # Parámetros de visualización
    FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
    FONT_SCALE = 1.0
    FONT_THICKNESS = 2
    TEXT_PADDING = 10
    TEXT_POSITION = (10, 30)            # Posición (x, y) del texto

# ==================== CONFIGURACIÓN DE ARCHIVOS ====================
class FileConfig:
    """Configuración de archivos y directorios"""
    
    # Directorios
    OUTPUT_DIR = "Salida_cople"
    
    # Formatos de archivo
    IMAGE_FORMAT = ".jpg"
    JSON_FORMAT = ".json"
    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
    
    # Nombres de archivo
    FILENAME_TEMPLATE = "cople_clasificacion_{timestamp}_#{count}{ext}"

# ==================== CONFIGURACIÓN DE ESTADÍSTICAS ====================
class StatsConfig:
    """Configuración de estadísticas y métricas"""
    
    # Tamaños de colas para estadísticas
    CAPTURE_TIMES_QUEUE_SIZE = 100
    PROCESSING_TIMES_QUEUE_SIZE = 100
    INFERENCE_TIMES_QUEUE_SIZE = 100

# ==================== CONFIGURACIÓN GLOBAL ====================
class GlobalConfig:
    """Configuración global del sistema"""
    
    # Rutas comunes
    GIGEV_COMMON_PATH = "../gigev_common"
    
    # Límites de memoria
    BUFFER_MARGIN = 8192  # Margen extra para buffers
    
    # Configuración del sistema
    DEBUG_MODE = True
    SAVE_ORIGINAL_IMAGES = True
    
    @classmethod
    def ensure_output_dir(cls):
        """Asegura que el directorio de salida existe"""
        if not os.path.exists(FileConfig.OUTPUT_DIR):
            os.makedirs(FileConfig.OUTPUT_DIR)
            print(f"📁 Directorio de salida creado: {FileConfig.OUTPUT_DIR}")

# ==================== CONFIGURACIÓN DE DESARROLLO ====================
class DevConfig:
    """Configuración para desarrollo y debugging"""
    
    # Guardar resultados intermedios
    SAVE_INTERMEDIATE_RESULTS = True
    SAVE_DEBUG_IMAGES = True
    
    # Logging detallado
    VERBOSE_LOGGING = True
    SHOW_TIMING_DETAILS = True
