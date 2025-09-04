# Análisis del Módulo de Segmentación de Piezas

## 📊 Umbrales Actuales

### 1. **Umbral de Confianza**
- **Valor actual**: `0.55` (55%)
- **Ubicación**: Constructor del `SegmentadorPiezasCoples`
- **Función**: Filtra detecciones con confianza menor al 55%
- **Aplicación**: Se aplica antes del NMS

### 2. **Umbral de IoU (Intersection over Union)**
- **Valor actual**: `0.45` (45%)
- **Ubicación**: Método `_aplicar_nms()`
- **Función**: Elimina detecciones superpuestas durante NMS
- **Aplicación**: Se aplica después del filtro de confianza

### 3. **Umbral de Máscara**
- **Valor actual**: `0.5` (50%)
- **Ubicación**: Método `_generar_mascara_prototipos()`
- **Función**: Convierte máscaras continuas a binarias
- **Aplicación**: Se aplica al generar máscaras finales

## 🔍 Análisis de Resultados Actuales

### Datos de la Última Ejecución:
- **Pieza detectada**: 1
- **Confianza**: 69.88%
- **BBox**: (0, 79) a (639, 639) - Área: 357,740 píxeles
- **Máscara**: 344,553 píxeles activos (96.3% del BBox)
- **Dimensiones máscara**: 639x559 píxeles

## ⚠️ Problemas Identificados

### 1. **Falta de Filtros de Tamaño**
- No hay umbral mínimo de área para máscaras
- No hay umbral mínimo de dimensiones (ancho/alto)
- Máscaras muy pequeñas pueden ser ruido

### 2. **Falta de Filtros de Calidad**
- No hay validación de la forma de la máscara
- No hay filtro de densidad de píxeles
- No hay validación de cobertura del BBox

## 🛠️ Propuestas de Mejora

### 1. **Filtros de Tamaño**
```python
# Umbrales propuestos
MIN_AREA_MASCARA = 1000        # Mínimo 1000 píxeles
MIN_ANCHO_MASCARA = 20         # Mínimo 20 píxeles de ancho
MIN_ALTO_MASCARA = 20          # Mínimo 20 píxeles de alto
MIN_AREA_BBOX = 500            # Mínimo 500 píxeles en BBox
```

### 2. **Filtros de Calidad**
```python
# Umbrales de calidad propuestos
MIN_COBERTURA_BBOX = 0.3       # Mínimo 30% de cobertura del BBox
MIN_DENSIDAD_MASCARA = 0.1     # Mínimo 10% de densidad en la máscara
MAX_RATIO_ASPECTO = 10.0       # Máximo ratio de aspecto 10:1
```

### 3. **Filtros de Forma**
```python
# Validación de forma
MIN_COMPACIDAD = 0.1           # Mínima compacidad (área/perímetro²)
MAX_FRAGMENTACION = 0.5        # Máxima fragmentación permitida
```

## 📈 Configuración Recomendada

### Para Piezas de Coples:
- **Confianza mínima**: 0.6 (60%) - Más estricto
- **IoU threshold**: 0.4 (40%) - Menos agresivo
- **Área mínima**: 2000 píxeles - Filtra ruido
- **Dimensiones mínimas**: 30x30 píxeles
- **Cobertura mínima**: 40% del BBox

### Para Defectos (referencia):
- **Confianza mínima**: 0.55 (55%) - Actual
- **IoU threshold**: 0.45 (45%) - Actual
- **Área mínima**: 100 píxeles - Más permisivo
- **Dimensiones mínimas**: 10x10 píxeles
