# Sistema de Análisis de Coples

Sistema modular para análisis automático de coples utilizando modelos de machine learning ONNX y captura de imágenes con cámara GigE.

## 🎯 Características

- **Captura de imágenes** con cámara GigE optimizada para alta resolución
- **Clasificación automática** de coples (Aceptado/Rechazado)
- **Procesamiento en tiempo real** con mínima latencia
- **Sistema modular** preparado para futuras expansiones
- **Fallback automático** a OpenCV si no hay cámara GigE disponible
- **Guardado automático** de imágenes y metadatos en formato JSON

## 🏗️ Arquitectura del Sistema

```
Expo_modelos/
├── main.py                 # Punto de entrada principal
├── config.py               # Configuración del sistema
├── utils.py                # Utilidades comunes
├── requirements.txt        # Dependencias del proyecto
├── modules/                # Módulos del sistema
│   ├── capture/            # Módulo de captura
│   │   ├── camera_controller.py
│   ├── classification/     # Módulo de clasificación
│   │   ├── inference_engine.py
│   │   └── image_processor.py
│   ├── detection/          # Módulo de detección (futuro)
│   └── segmentation/       # Módulo de segmentación (futuro)
├── Modelos/                # Modelos ONNX
│   ├── CopleClasDef2C1V.onnx
│   ├── clases_CopleClasDef2C1V.txt
│   └── [otros modelos futuros...]
└── Salida_cople/           # Directorio de salida
```

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
cd /ruta/a/tu/proyecto
git clone <url-del-repositorio>
cd Expo_modelos
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Verificar modelos
Asegúrate de que los archivos del modelo estén en el directorio `Modelos/`:
- `CopleClasDef2C1V.onnx` - Modelo de clasificación
- `clases_CopleClasDef2C1V.txt` - Archivo de clases

## 📷 Configuración de Cámara

### Cámara GigE (Recomendado)
El sistema está configurado para usar cámaras GigE con la siguiente configuración por defecto:
- **IP**: 172.16.1.21
- **Resolución nativa**: 4112x2176
- **ROI activo**: 640x640 (centrado)
- **Framerate**: 10 FPS
- **Exposición**: 20ms

Para cambiar la configuración, edita `config.py` en la sección `CameraConfig`.

### Fallback OpenCV
Si no hay cámara GigE disponible, el sistema automáticamente usará la cámara webcam como fallback.

## 🎮 Uso del Sistema

### Ejecutar el sistema
```bash
python main.py
```

### Comandos disponibles
- **ENTER** - Capturar imagen y clasificar coples
- **'v'** - Solo ver frame (sin clasificar)
- **'s'** - Mostrar estadísticas del sistema
- **'c'** - Mostrar configuración completa
- **'t'** - Cambiar umbral de confianza
- **'q'** - Salir del sistema

### Flujo de trabajo
1. **Inicialización**: El sistema configura la cámara y carga el modelo
2. **Captura**: Se obtiene una imagen de la cámara
3. **Clasificación**: La imagen se procesa con el modelo ONNX
4. **Resultado**: Se muestra la clase predicha y la confianza
5. **Guardado**: Se guarda la imagen anotada y un archivo JSON con metadatos

## 📊 Salida del Sistema

### Imágenes
- **Formato**: JPG
- **Ubicación**: `Salida_cople/`
- **Anotaciones**: Etiqueta de clase con color (Verde=Aceptado, Rojo=Rechazado)
- **Información adicional**: Confianza, tiempos de procesamiento

### Metadatos JSON
```json
{
  "archivo_imagen": "cople_clasificacion_20241201_143022_#1.jpg",
  "clase_predicha": "Aceptado",
  "confianza": 0.95,
  "tiempo_captura_ms": 15.2,
  "tiempo_inferencia_ms": 45.8,
  "tiempo_total_ms": 61.0,
  "timestamp": "2024-12-01T14:30:22.123456",
  "modelo": "CopleClasDef2C1V.onnx",
  "resolucion": {
    "ancho": 1280,
    "alto": 1024,
    "canales": 3
  }
}
```

## 🔧 Configuración Avanzada

### Parámetros del modelo
Edita `config.py` para ajustar:
- Umbral de confianza
- Tamaño de entrada del modelo (640x640)
- Proveedores ONNX
- Configuración de threads

### Parámetros de cámara
- Tiempo de exposición
- Framerate
- Tamaño de ROI
- Configuración de buffers

### Configuración del ROI
El sistema utiliza un ROI (Region of Interest) de 640x640 píxeles centrado en la imagen nativa de 4112x2176:
- **Resolución nativa**: 4112x2176 píxeles
- **ROI activo**: 640x640 píxeles
- **Offset X**: 1736 píxeles (centrado horizontalmente)
- **Offset Y**: 768 píxeles (centrado verticalmente)
- **Área de captura**: Centro de la imagen para máxima calidad

### Visualización
- Colores de etiquetas
- Posición de texto
- Tamaño de fuente
- Información de debug

## 🚧 Módulos Futuros

El sistema está diseñado para expandirse con:

### 1. Detección de Defectos
- **Modelo**: `CopleDetDef1C2V.onnx`
- **Función**: Detectar y localizar defectos específicos en coples

### 2. Detección de Piezas
- **Modelo**: `CopleDetPZ1C1V.onnx`
- **Función**: Identificar y contar piezas individuales

### 3. Segmentación de Defectos
- **Modelo**: `CopleSegDef1C8V.onnx`
- **Función**: Crear máscaras de segmentación para defectos

### 4. Segmentación de Piezas
- **Modelo**: `CopleSegPz1C1V.onnx`
- **Función**: Segmentar y analizar piezas individuales

## 🐛 Solución de Problemas

### Error: "ONNX Runtime no disponible"
```bash
pip install onnxruntime
```

### Error: "No se encontró cámara en IP"
- Verifica la conexión de red
- Confirma la IP de la cámara
- Revisa la configuración en `config.py`

### Error: "Modelo no encontrado"
- Verifica que el archivo `.onnx` esté en `Modelos/`
- Confirma que el archivo de clases existe
- Revisa permisos de archivo

### Rendimiento lento
- Reduce la resolución de entrada
- Ajusta el framerate de la cámara
- Optimiza la configuración de threads ONNX

## 📈 Monitoreo y Estadísticas

El sistema proporciona estadísticas en tiempo real:
- **FPS de cámara**
- **Tiempos de captura**
- **Tiempos de inferencia**
- **Número de frames procesados**
- **Uso de memoria**

## 🤝 Contribución

Para contribuir al proyecto:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa los cambios
4. Agrega tests si es necesario
5. Envía un pull request

## 📄 Licencia

Este proyecto está bajo la licencia [especificar licencia].

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar la documentación técnica

---

**Desarrollado por**: [Tu Nombre/Organización]  
**Versión**: 1.0.0  
**Última actualización**: Diciembre 2024
