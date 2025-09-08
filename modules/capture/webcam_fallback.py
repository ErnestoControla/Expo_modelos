"""
Sistema de Fallback para Webcam
Proporciona una alternativa cuando no se encuentra la cámara GigE
"""

import cv2
import numpy as np
import time
from typing import Optional, Tuple
import threading
from queue import Queue, Empty
import logging

class WebcamFallback:
    """
    Controlador de webcam como fallback para la cámara GigE
    """
    
    def __init__(self, device_id: int = 0, width: int = 640, height: int = 640):
        """
        Inicializa el controlador de webcam
        
        Args:
            device_id: ID del dispositivo de cámara (0, 1, 2, etc.)
            width: Ancho de la imagen
            height: Alto de la imagen
        """
        self.device_id = device_id
        self.width = width
        self.height = height
        
        # Estado de la cámara
        self.cap = None
        self.inicializado = False
        self.capturando = False
        
        # Thread de captura
        self.capture_thread = None
        self.frame_queue = Queue(maxsize=2)
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        
        # Estadísticas
        self.total_frames_captured = 0
        self.start_time = 0
        
    def detectar_webcams_disponibles(self) -> list:
        """
        Detecta todas las webcams disponibles en el sistema
        
        Returns:
            list: Lista de IDs de dispositivos disponibles
        """
        webcams_disponibles = []
        
        print("🔍 Buscando webcams disponibles...")
        
        # Probar hasta 10 dispositivos
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # Intentar leer un frame para verificar que funciona
                ret, frame = cap.read()
                if ret and frame is not None:
                    webcams_disponibles.append(i)
                    print(f"✅ Webcam encontrada en dispositivo {i}")
                cap.release()
            else:
                cap.release()
                
        if not webcams_disponibles:
            print("❌ No se encontraron webcams disponibles")
        else:
            print(f"📷 Total de webcams encontradas: {len(webcams_disponibles)}")
            
        return webcams_disponibles
    
    def inicializar(self, device_id: Optional[int] = None) -> bool:
        """
        Inicializa la webcam
        
        Args:
            device_id: ID del dispositivo (si None, usa self.device_id)
            
        Returns:
            bool: True si se inicializó correctamente
        """
        if device_id is not None:
            self.device_id = device_id
            
        try:
            print(f"📷 Inicializando webcam en dispositivo {self.device_id}...")
            
            # Crear objeto VideoCapture
            self.cap = cv2.VideoCapture(self.device_id)
            
            if not self.cap.isOpened():
                print(f"❌ No se pudo abrir la webcam en dispositivo {self.device_id}")
                return False
            
            # Configurar resolución
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            # Configurar FPS
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Verificar configuración
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"✅ Webcam configurada:")
            print(f"   📐 Resolución: {actual_width}x{actual_height}")
            print(f"   🎬 FPS: {actual_fps:.1f}")
            
            # Probar captura
            ret, frame = self.cap.read()
            if not ret or frame is None:
                print("❌ Error en captura de prueba")
                return False
            
            self.inicializado = True
            self.start_time = time.time()
            
            print("✅ Webcam inicializada correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando webcam: {e}")
            return False
    
    def iniciar_captura_continua(self) -> bool:
        """
        Inicia la captura continua en un thread separado
        
        Returns:
            bool: True si se inició correctamente
        """
        if not self.inicializado:
            print("❌ Webcam no inicializada")
            return False
            
        if self.capturando:
            print("⚠️ Captura ya está activa")
            return True
            
        try:
            self.capturando = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            print("✅ Captura continua iniciada")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando captura continua: {e}")
            self.capturando = False
            return False
    
    def _capture_loop(self):
        """Loop de captura en thread separado"""
        while self.capturando and self.cap is not None:
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    # Redimensionar si es necesario
                    if frame.shape[:2] != (self.height, self.width):
                        frame = cv2.resize(frame, (self.width, self.height))
                    
                    # Actualizar frame más reciente
                    with self.frame_lock:
                        self.latest_frame = frame.copy()
                    
                    # Agregar a cola (sin bloquear)
                    try:
                        self.frame_queue.put_nowait(frame.copy())
                    except:
                        # Cola llena, remover frame más antiguo
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put_nowait(frame.copy())
                        except:
                            pass
                    
                    self.total_frames_captured += 1
                else:
                    time.sleep(0.01)  # Pequeña pausa si no hay frame
                    
            except Exception as e:
                print(f"⚠️ Error en captura: {e}")
                time.sleep(0.1)
    
    def obtener_frame_instantaneo(self) -> Tuple[Optional[np.ndarray], float, float]:
        """
        Obtiene el frame más reciente
        
        Returns:
            tuple: (frame, tiempo_acceso_ms, timestamp)
        """
        if not self.inicializado:
            return None, 0, 0
            
        start_time = time.time()
        
        with self.frame_lock:
            if self.latest_frame is not None:
                frame = self.latest_frame.copy()
                tiempo_acceso = (time.time() - start_time) * 1000
                timestamp = time.time()
                return frame, tiempo_acceso, timestamp
        
        return None, 0, 0
    
    def obtener_frame_sincrono(self) -> Tuple[Optional[np.ndarray], float, float]:
        """
        Obtiene un frame directamente (síncrono)
        
        Returns:
            tuple: (frame, tiempo_acceso_ms, timestamp)
        """
        if not self.inicializado or self.cap is None:
            return None, 0, 0
            
        start_time = time.time()
        
        try:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                # Redimensionar si es necesario
                if frame.shape[:2] != (self.height, self.width):
                    frame = cv2.resize(frame, (self.width, self.height))
                
                tiempo_acceso = (time.time() - start_time) * 1000
                timestamp = time.time()
                return frame, tiempo_acceso, timestamp
        except Exception as e:
            print(f"⚠️ Error en captura síncrona: {e}")
        
        return None, 0, 0
    
    def detener_captura_continua(self):
        """Detiene la captura continua"""
        if self.capturando:
            self.capturando = False
            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=2.0)
            print("🛑 Captura continua detenida")
    
    def liberar_recursos(self):
        """Libera todos los recursos de la webcam"""
        self.detener_captura_continua()
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
        # Limpiar cola
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except:
                break
                
        self.inicializado = False
        print("✅ Recursos de webcam liberados")
    
    def obtener_estadisticas(self) -> dict:
        """
        Obtiene estadísticas de la webcam
        
        Returns:
            dict: Estadísticas de rendimiento
        """
        if not self.inicializado:
            return {}
            
        tiempo_transcurrido = time.time() - self.start_time if self.start_time > 0 else 0
        fps_promedio = self.total_frames_captured / tiempo_transcurrido if tiempo_transcurrido > 0 else 0
        
        return {
            "dispositivo": self.device_id,
            "resolucion": f"{self.width}x{self.height}",
            "frames_capturados": self.total_frames_captured,
            "tiempo_transcurrido": tiempo_transcurrido,
            "fps_promedio": fps_promedio,
            "capturando": self.capturando,
            "inicializado": self.inicializado
        }


def detectar_mejor_webcam() -> Optional[int]:
    """
    Detecta la mejor webcam disponible
    
    Returns:
        int: ID del dispositivo de la mejor webcam, o None si no hay ninguna
    """
    webcam_fallback = WebcamFallback()
    webcams_disponibles = webcam_fallback.detectar_webcams_disponibles()
    
    if not webcams_disponibles:
        return None
    
    # Por ahora, devolver la primera disponible
    # En el futuro se podría implementar lógica para seleccionar la mejor
    return webcams_disponibles[0]


if __name__ == "__main__":
    # Prueba del sistema de webcam
    print("🧪 Probando sistema de webcam fallback...")
    
    # Detectar webcams
    webcam_id = detectar_mejor_webcam()
    
    if webcam_id is not None:
        print(f"📷 Usando webcam en dispositivo {webcam_id}")
        
        # Inicializar webcam
        webcam = WebcamFallback(device_id=webcam_id)
        if webcam.inicializar():
            print("✅ Webcam inicializada correctamente")
            
            # Probar captura
            frame, tiempo, timestamp = webcam.obtener_frame_sincrono()
            if frame is not None:
                print(f"📸 Frame capturado: {frame.shape}, tiempo: {tiempo:.2f}ms")
                
                # Mostrar frame
                cv2.imshow("Webcam Test", frame)
                cv2.waitKey(2000)  # Mostrar por 2 segundos
                cv2.destroyAllWindows()
            else:
                print("❌ No se pudo capturar frame")
            
            # Liberar recursos
            webcam.liberar_recursos()
        else:
            print("❌ Error inicializando webcam")
    else:
        print("❌ No se encontraron webcams disponibles")
