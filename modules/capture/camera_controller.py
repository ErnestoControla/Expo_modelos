"""
Controlador de cámara GigE para captura de imágenes de coples
Maneja la configuración, captura y buffering de imágenes de alta resolución
"""

import cv2
import time
import numpy as np
import ctypes
import threading
from threading import Event, Lock
from queue import Queue
import sys
import os

# Importar configuración y utilidades
from config import CameraConfig, StatsConfig, GlobalConfig

# Obtener el código de soporte común para el GigE-V Framework
sys.path.append(os.path.dirname(__file__) + "/" + GlobalConfig.GIGEV_COMMON_PATH)

try:
    import pygigev
    from pygigev import GevPixelFormats as GPF
    GIGEV_AVAILABLE = True
except ImportError:
    print("⚠️ Advertencia: pygigev no disponible, usando OpenCV como fallback")
    GIGEV_AVAILABLE = False


class CamaraTiempoOptimizada:
    """
    Controlador optimizado de cámara GigE para captura de imágenes de coples.
    
    Características:
    - Captura asíncrona continua con doble buffer
    - Optimizado para resolución alta (1280x1024)
    - Procesamiento en tiempo real con mínima latencia
    - Gestión automática de memoria
    - Estadísticas de rendimiento en tiempo real
    """
    
    def __init__(self, ip=None):
        """
        Inicializa el controlador de cámara.
        
        Args:
            ip (str, optional): Dirección IP de la cámara. Si no se proporciona, usa la configuración por defecto.
        """
        self.ip = ip or CameraConfig.DEFAULT_IP
        self.handle = None
        self.buffer_addresses = None
        self.frame_count = 0
        self.camIndex = -1
        
        # Parámetros de configuración desde config.py
        self.exposure_time = CameraConfig.EXPOSURE_TIME
        self.framerate = CameraConfig.FRAMERATE
        self.packet_size = CameraConfig.PACKET_SIZE
        self.num_buffers = CameraConfig.NUM_BUFFERS
        self.gain = CameraConfig.GAIN
        
        # Configuración del ROI
        self.roi_width = CameraConfig.ROI_WIDTH
        self.roi_height = CameraConfig.ROI_HEIGHT
        self.roi_offset_x = CameraConfig.ROI_OFFSET_X
        self.roi_offset_y = CameraConfig.ROI_OFFSET_Y
        
        # Sistema de doble buffer asíncrono optimizado
        self.write_buffer_idx = 0    # Buffer donde se está escribiendo actualmente
        self.read_buffer_idx = 1     # Buffer listo para lectura
        
        # Almacenamiento de frames procesados
        self.processed_frames = [None] * 2  # Solo necesitamos 2 slots
        self.frame_ready = [False] * 2      # Estado de cada frame
        self.frame_timestamps = [0] * 2     # Timestamps de captura
        
        # Control de sincronización optimizado
        self.buffer_lock = Lock()           # Lock mínimo para cambios de índices
        self.frame_ready_event = Event()    # Señal de frame listo
        self.capture_thread = None          # Thread de captura continua
        self.capture_active = False         # Control del thread
        
        # Estadísticas de rendimiento
        self.capture_times = Queue(maxsize=StatsConfig.CAPTURE_TIMES_QUEUE_SIZE)
        self.processing_times = Queue(maxsize=StatsConfig.PROCESSING_TIMES_QUEUE_SIZE)
        self.total_frames_captured = 0
        self.start_time = 0
        
        # Información de payload
        self.payload_size = None
        self.pixel_format = None
        
        # Fallback a OpenCV si no hay GigE
        self.use_opencv_fallback = not GIGEV_AVAILABLE
        if self.use_opencv_fallback:
            self.cap = None

    def configurar_camara(self):
        """
        Configura parámetros de la cámara una sola vez.
        
        Returns:
            bool: True si la configuración fue exitosa
        """
        try:
            if self.use_opencv_fallback:
                return self._configurar_opencv_fallback()
            
            # Inicializar API GigE
            pygigev.GevApiInitialize()
            
            # Encontrar cámara por IP
            self.camIndex = self._encontrar_camara_por_ip()
            if self.camIndex == -1:
                print(f"❌ No se encontró cámara en IP: {self.ip}")
                return False
            
            # Abrir cámara
            self.handle = pygigev.GevOpenCameraByIndex(self.camIndex)
            if not self.handle:
                print(f"❌ Error abriendo cámara en índice {self.camIndex}")
                return False
            
            # Configurar parámetros de cámara
            self._configurar_parametros_camara()
            
            # Configurar buffers
            self._configurar_buffers()
            
            # Configurar callbacks
            self._configurar_callbacks()
            
            print(f"✅ Cámara configurada correctamente en IP: {self.ip}")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando cámara: {e}")
            return False

    def _configurar_opencv_fallback(self):
        """Configura OpenCV como fallback si no hay GigE disponible"""
        try:
            # Intentar abrir cámara webcam como fallback
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("❌ No se pudo abrir cámara webcam como fallback")
                return False
            
            # Configurar parámetros básicos
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.roi_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.roi_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.framerate)
            
            print("✅ Cámara OpenCV configurada como fallback")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando fallback OpenCV: {e}")
            return False

    def _encontrar_camara_por_ip(self):
        """Encuentra el índice de la cámara por IP"""
        try:
            num_cameras = pygigev.GevGetCameraCount()
            print(f"🔍 Buscando cámara en IP: {self.ip}")
            print(f"   Cámaras disponibles: {num_cameras}")
            
            for i in range(num_cameras):
                camera_info = pygigev.GevGetCameraInfo(i)
                if camera_info and camera_info.ipAddr == self.ip:
                    print(f"   ✅ Cámara encontrada en índice {i}")
                    return i
            
            print(f"   ❌ No se encontró cámara en IP: {self.ip}")
            return -1
            
        except Exception as e:
            print(f"❌ Error buscando cámara: {e}")
            return -1

    def _configurar_parametros_camara(self):
        """Configura parámetros específicos de la cámara"""
        try:
            # Configurar ROI
            pygigev.GevSetIntValue(self.handle, "Width", self.roi_width)
            pygigev.GevSetIntValue(self.handle, "Height", self.roi_height)
            pygigev.GevSetIntValue(self.handle, "OffsetX", self.roi_offset_x)
            pygigev.GevSetIntValue(self.handle, "OffsetY", self.roi_offset_y)
            
            # Configurar exposición y ganancia
            pygigev.GevSetIntValue(self.handle, "ExposureTime", self.exposure_time)
            pygigev.GevSetFloatValue(self.handle, "Gain", self.gain)
            
            # Configurar framerate
            pygigev.GevSetFloatValue(self.handle, "AcquisitionFrameRate", self.framerate)
            
            # Configurar tamaño de paquete
            pygigev.GevSetIntValue(self.handle, "GevSCPSPacketSize", self.packet_size)
            
            print("   ✅ Parámetros de cámara configurados")
            
        except Exception as e:
            print(f"   ⚠️ Error configurando parámetros: {e}")

    def _configurar_buffers(self):
        """Configura buffers de memoria para captura"""
        try:
            # Obtener información del payload
            self.payload_size = pygigev.GevGetIntValue(self.handle, "PayloadSize")
            self.pixel_format = pygigev.GevGetEnumValue(self.handle, "PixelFormat")
            
            print(f"   📊 Payload: {self.payload_size} bytes, Pixel: {self.pixel_format}")
            
            # Configurar buffers
            pygigev.GevSetIntValue(self.handle, "StreamBufferHandlingMode", 1)
            pygigev.GevSetIntValue(self.handle, "StreamBufferCountManual", self.num_buffers)
            
            print("   ✅ Buffers configurados")
            
        except Exception as e:
            print(f"   ⚠️ Error configurando buffers: {e}")

    def _configurar_callbacks(self):
        """Configura callbacks para captura asíncrona"""
        try:
            # Configurar callback de frame
            pygigev.GevSetImageEventCallback(self.handle, self._on_frame_received)
            
            print("   ✅ Callbacks configurados")
            
        except Exception as e:
            print(f"   ⚠️ Error configurando callbacks: {e}")

    def _on_frame_received(self, handle, buffer_address, buffer_size, user_data):
        """Callback llamado cuando se recibe un frame"""
        try:
            with self.buffer_lock:
                # Cambiar índices de buffer
                self.read_buffer_idx = self.write_buffer_idx
                self.write_buffer_idx = (self.write_buffer_idx + 1) % 2
                
                # Procesar frame recibido
                frame_data = ctypes.cast(buffer_address, ctypes.POINTER(ctypes.c_ubyte * buffer_size))
                frame_array = np.frombuffer(frame_data.contents, dtype=np.uint8)
                
                # Convertir a imagen OpenCV
                frame = frame_array.reshape((self.roi_height, self.roi_width, -1))
                
                # Almacenar frame procesado
                self.processed_frames[self.read_buffer_idx] = frame.copy()
                self.frame_ready[self.read_buffer_idx] = True
                self.frame_timestamps[self.read_buffer_idx] = time.time()
                
                # Señalar que hay frame listo
                self.frame_ready_event.set()
                
                # Actualizar estadísticas
                self.total_frames_captured += 1
                
        except Exception as e:
            print(f"⚠️ Error en callback de frame: {e}")

    def iniciar_captura_continua(self):
        """
        Inicia la captura continua de frames.
        
        Returns:
            bool: True si la captura se inició correctamente
        """
        try:
            if self.use_opencv_fallback:
                return True  # OpenCV ya está capturando continuamente
            
            # Iniciar captura
            pygigev.GevStartAcquisition(self.handle)
            
            # Iniciar thread de captura
            self.capture_active = True
            self.capture_thread = threading.Thread(target=self._thread_captura_continua)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            self.start_time = time.time()
            print("✅ Captura continua iniciada")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando captura continua: {e}")
            return False

    def _thread_captura_continua(self):
        """Thread para captura continua de frames"""
        try:
            while self.capture_active:
                # Esperar frame
                if self.frame_ready_event.wait(timeout=0.1):
                    self.frame_ready_event.clear()
                    
                    # Procesar frame si es necesario
                    time.sleep(0.001)  # Pequeña pausa para no saturar CPU
                    
        except Exception as e:
            print(f"⚠️ Error en thread de captura: {e}")

    def obtener_frame_instantaneo(self):
        """
        Obtiene un frame instantáneo de la cámara.
        
        Returns:
            tuple: (frame, tiempo_acceso, timestamp) o (None, 0, 0) si hay error
        """
        try:
            if self.use_opencv_fallback:
                return self._obtener_frame_opencv()
            
            start_time = time.time()
            
            # Esperar frame listo
            if not self.frame_ready_event.wait(timeout=CameraConfig.FRAME_TIMEOUT):
                return None, 0, 0
            
            with self.buffer_lock:
                if not self.frame_ready[self.read_buffer_idx]:
                    return None, 0, 0
                
                # Obtener frame
                frame = self.processed_frames[self.read_buffer_idx].copy()
                timestamp = self.frame_timestamps[self.read_buffer_idx]
                
                # Marcar como no listo
                self.frame_ready[self.read_buffer_idx] = False
            
            tiempo_acceso = (time.time() - start_time) * 1000
            
            # Actualizar estadísticas
            if self.capture_times.qsize() < StatsConfig.CAPTURE_TIMES_QUEUE_SIZE:
                self.capture_times.put(tiempo_acceso)
            
            return frame, tiempo_acceso, timestamp
            
        except Exception as e:
            print(f"⚠️ Error obteniendo frame: {e}")
            return None, 0, 0

    def _obtener_frame_opencv(self):
        """Obtiene frame usando OpenCV como fallback"""
        try:
            start_time = time.time()
            
            ret, frame = self.cap.read()
            if not ret:
                return None, 0, 0
            
            # Redimensionar si es necesario
            if frame.shape[:2] != (self.roi_height, self.roi_width):
                frame = cv2.resize(frame, (self.roi_width, self.roi_height))
            
            tiempo_acceso = (time.time() - start_time) * 1000
            timestamp = time.time()
            
            # Actualizar estadísticas
            if self.capture_times.qsize() < StatsConfig.CAPTURE_TIMES_QUEUE_SIZE:
                self.capture_times.put(tiempo_acceso)
            
            return frame, tiempo_acceso, timestamp
            
        except Exception as e:
            print(f"⚠️ Error obteniendo frame OpenCV: {e}")
            return None, 0, 0

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas de rendimiento de la cámara.
        
        Returns:
            dict: Estadísticas de la cámara
        """
        try:
            # Calcular estadísticas de tiempo de captura
            capture_times_list = list(self.capture_times.queue)
            tiempo_captura = {}
            if capture_times_list:
                tiempo_captura = {
                    'promedio': np.mean(capture_times_list),
                    'std': np.std(capture_times_list),
                    'min': np.min(capture_times_list),
                    'max': np.max(capture_times_list)
                }
            
            # Calcular estadísticas de tiempo de procesamiento
            processing_times_list = list(self.processing_times.queue)
            tiempo_procesamiento = {}
            if processing_times_list:
                tiempo_procesamiento = {
                    'promedio': np.mean(processing_times_list),
                    'std': np.std(processing_times_list),
                    'min': np.min(processing_times_list),
                    'max': np.max(processing_times_list)
                }
            
            # Calcular FPS real
            fps_real = 0
            if self.start_time > 0:
                tiempo_total = time.time() - self.start_time
                if tiempo_total > 0:
                    fps_real = self.total_frames_captured / tiempo_total
            
            return {
                'fps_real': fps_real,
                'frames_totales': self.total_frames_captured,
                'buffers_listos': sum(self.frame_ready),
                'tiempo_captura': tiempo_captura,
                'tiempo_procesamiento': tiempo_procesamiento,
                'ip_camara': self.ip,
                'resolucion': f"{self.roi_width}x{self.roi_height}",
                'framerate_config': self.framerate,
                'exposure_time': self.exposure_time,
                'gain': self.gain
            }
            
        except Exception as e:
            print(f"⚠️ Error obteniendo estadísticas: {e}")
            return {}

    def mostrar_configuracion(self):
        """Muestra la configuración actual de la cámara."""
        print(f"\n📷 CONFIGURACIÓN DE CÁMARA:")
        print(f"   IP: {self.ip}")
        print(f"   Resolución: {self.roi_width}x{self.roi_height}")
        print(f"   ROI Offset: ({self.roi_offset_x}, {self.roi_offset_y})")
        print(f"   Framerate: {self.framerate} FPS")
        print(f"   Exposición: {self.exposure_time} μs")
        print(f"   Ganancia: {self.gain}")
        print(f"   Buffers: {self.num_buffers}")
        print(f"   Protocolo: {'GigE' if not self.use_opencv_fallback else 'OpenCV (fallback)'}")

    def liberar(self):
        """Libera todos los recursos de la cámara."""
        try:
            print("🧹 Liberando recursos de cámara...")
            
            # Detener captura continua
            self.capture_active = False
            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=CameraConfig.SHUTDOWN_TIMEOUT)
            
            if self.use_opencv_fallback:
                if self.cap:
                    self.cap.release()
                    self.cap = None
            else:
                # Liberar recursos GigE
                if self.handle:
                    try:
                        pygigev.GevStopAcquisition(self.handle)
                        pygigev.GevCloseCamera(self.handle)
                    except:
                        pass
                    self.handle = None
                
                # Finalizar API
                try:
                    pygigev.GevApiTerminate()
                except:
                    pass
            
            print("✅ Recursos de cámara liberados")
            
        except Exception as e:
            print(f"⚠️ Error liberando recursos: {e}")
