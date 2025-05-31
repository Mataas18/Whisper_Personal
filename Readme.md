# 🎙️ Transcriptor Whisper en Tiempo Real

Un sistema avanzado de transcripción de audio en tiempo real utilizando OpenAI Whisper, con funcionalidades inteligentes como detección de palabras clave, análisis de confianza y configuración de calidad de audio.

## 📋 Descripción del Proyecto

Este proyecto permite transcribir audio en tiempo real directamente desde el micrófono usando los modelos de Whisper de OpenAI. Incluye características avanzadas como:

- **🎤 Grabación manual controlada**: Control total sobre cuándo empezar y parar
- **🔍 Detección de palabras clave**: Identifica automáticamente términos importantes
- **📊 Análisis de confianza**: Evalúa la precisión de cada segmento transcrito
- **⚙️ Configuración de calidad**: Ajuste de calidad de audio para optimizar precisión vs velocidad
- **🗂️ Gestión de archivos**: Guarda transcripciones en texto y JSON con metadatos
- **🎮 Interfaz intuitiva**: Menús interactivos con navegación por teclado

## 🔧 Requisitos del Sistema

### Hardware Recomendado
- **GPU**: NVIDIA RTX 2060 o superior (recomendado RTX 3060+)
- **RAM**: 8 GB mínimo, 16 GB recomendado
- **Almacenamiento**: 2 GB libres para modelos
- **Micrófono**: Cualquier micrófono USB o integrado

### Software
- **SO**: Windows 10/11, Linux, macOS
- **Python**: 3.8 - 3.11
- **CUDA**: 11.8 o 12.1 (para aceleración GPU)

## 📦 Instalación

### 1. Crear entorno Conda

```bash
# Crear entorno con Python 3.10
conda create -n whisper-env python=3.10

# Activar entorno
conda activate whisper-env
```

### 2. Instalar dependencias principales

```bash

# PyTorch con soporte CUDA
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# OpenAI Whisper
pip install openai-whisper

# Dependencias de audio
conda install -c conda-forge pyaudio sounddevice scipy

# Procesamiento de datos
conda install numpy pandas

# Control de teclado
pip install keyboard
```

### 3. Verificar instalación

```bash
# Verificar CUDA
python -c "import torch; print('CUDA disponible:', torch.cuda.is_available())"

# Verificar Whisper
python -c "import whisper; print('Modelos disponibles:', len(whisper.available_models()))"
```

## 📁 Estructura del Proyecto

```
whisper-project/
├── audio/                      # 🎵 Archivos de audio grabados
│   ├── grabacion_YYYYMMDD_HHMMSS.wav
│   └── temp_recording_*.wav
├── output/                     # 📄 Transcripciones generadas
│   ├── transcripcion_YYYYMMDD_HHMMSS.txt
│   └── transcripcion_YYYYMMDD_HHMMSS.json
├── scripts/                    # 🐍 Scripts del proyecto
│   ├── transcribe_realtime.py  # Script principal
│   ├── show_models.py          # Información de modelos
│   └── simple_record.py        # Grabador alternativo
├── notebooks/                  # 📓 Jupyter notebooks (opcional)
├── models/                     # 🤖 Modelos descargados automáticamente
├── test_setup.py              # ✅ Script de verificación
├── environment.yml             # 📋 Configuración del entorno
└── README.md                   # 📖 Este archivo
```

### Descripción de Directorios

- **`audio/`**: Almacena todas las grabaciones de audio en formato WAV
- **`output/`**: Contiene las transcripciones en formato texto y JSON con metadatos
- **`scripts/`**: Scripts principales del proyecto y utilidades
- **`models/`**: Whisper descarga automáticamente los modelos aquí
- **`notebooks/`**: Para análisis de datos y experimentación (opcional)

## 🚀 Uso del Programa

### Ejecución Principal

```bash
# Activar entorno
conda activate whisper-env

# Ejecutar transcriptor
python scripts/transcribe_realtime.py

# Con parámetros específicos
python scripts/transcribe_realtime.py base es
python scripts/transcribe_realtime.py medium en
```

### Menú Principal

Al ejecutar el programa verás:

```
🎙️  TRANSCRIPTOR EN TIEMPO REAL - WHISPER
============================================================
📊 Configuración actual:
   • Modelo: base
   • Idioma: es
   • Calidad audio: medium (16000Hz)
============================================================
1️⃣  Iniciar transcripción
2️⃣  Configurar ajustes
3️⃣  Ver información de modelos
4️⃣  Salir del programa
```

### Controles de Grabación

- **ENTER**: Iniciar grabación
- **ESPACIO**: Parar grabación y transcribir
- **ESC**: Volver al menú anterior/salir

## 🎯 Funcionalidades Principales

### 1. Transcripción Inteligente
- Transcripción de audio a texto en tiempo real
- Soporte para múltiples idiomas
- Timestamps precisos para cada segmento

### 2. Detección de Palabras Clave
Detecta automáticamente términos importantes como:
- `importante`, `urgente`, `crítico`
- `decisión`, `problema`, `solución`
- `fecha`, `plazo`, `reunión`
- `presupuesto`, `coste`, `precio`

### 3. Análisis de Confianza
- **🟢 Alta confianza**: Transcripción muy precisa
- **🟡 Media confianza**: Revisar recomendado
- **🔴 Baja confianza**: Verificación necesaria

### 4. Configuración de Calidad
- **Low (8kHz)**: Rápido, archivos pequeños
- **Medium (16kHz)**: Balance recomendado
- **High (44kHz)**: Máxima calidad
- **Ultra (48kHz)**: Calidad profesional

## 🤖 Modelos Disponibles

| Modelo | Tamaño | Velocidad | Calidad | Recomendado para |
|--------|--------|-----------|---------|------------------|
| tiny   | 39 MB  | ~32x      | ⭐⭐     | Pruebas rápidas |
| base   | 74 MB  | ~16x      | ⭐⭐⭐    | Uso general |
| small  | 244 MB | ~6x       | ⭐⭐⭐⭐   | Balance óptimo |
| medium | 769 MB | ~2x       | ⭐⭐⭐⭐⭐  | Alta precisión |
| large  | 1550 MB| 1x        | ⭐⭐⭐⭐⭐⭐ | Máxima calidad |
| turbo  | 809 MB | ~8x       | ⭐⭐⭐⭐⭐  | Rápido y preciso |

### Recomendaciones por Hardware
- **RTX 3060+**: Cualquier modelo
- **RTX 2060**: medium o inferior
- **Solo CPU**: tiny o base

## 📊 Archivos de Salida

### Archivo de Texto (.txt)
```
Fecha: 2025-05-31 17:46:23
Modelo: base
Idioma: es
Calidad de audio: medium (16000Hz)
--------------------------------------------------
TRANSCRIPCIÓN:
Esta es una reunión importante para discutir el presupuesto...

--------------------------------------------------
PALABRAS CLAVE DETECTADAS:
• IMPORTANTE: Esta es una reunión importante
• PRESUPUESTO: discutir el presupuesto del próximo trimestre

--------------------------------------------------
ANÁLISIS DE CONFIANZA:
[0.0s-2.1s] 🟢 Alta: Esta es una reunión importante
[2.1s-4.5s] 🟡 Media: para discutir el presupuesto
```

### Archivo JSON (.json)
```json
{
  "timestamp": "2025-05-31T17:46:23",
  "model": "base",
  "language": "es",
  "audio_quality": "medium",
  "text": "Esta es una reunión importante...",
  "keywords": [...],
  "confidence_analysis": [...]
}
```

## 🔧 Solución de Problemas

### GPU no se detecta
```bash
# Verificar CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Reinstalar PyTorch si es necesario
conda uninstall pytorch torchvision torchaudio
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

### Problemas de audio
```bash
# Verificar dispositivos de audio
python -c "import sounddevice as sd; print(sd.query_devices())"

# Reinstalar pyaudio si es necesario
conda uninstall pyaudio
conda install -c conda-forge pyaudio
```

### Errores de permisos de micrófono
- **Windows**: Configuración → Privacidad → Micrófono
- **macOS**: Preferencias del Sistema → Seguridad → Micrófono
- **Linux**: Verificar grupo `audio`

## 🎓 Scripts Adicionales

### Ver modelos disponibles
```bash
python scripts/show_models.py
python scripts/show_models.py base  # Info específica
```

### Grabador simple alternativo
```bash
python scripts/simple_record.py 10  # Grabar 10 segundos
python scripts/simple_record.py     # Modo interactivo
```

## 📈 Consejos de Rendimiento

1. **Usar modelo apropiado**: `base` para uso general, `large` para máxima precisión
2. **Optimizar calidad**: `medium` es suficiente para la mayoría de casos
3. **Micrófono cerca**: 15-30 cm de distancia óptima
4. **Ambiente silencioso**: Reduce ruido de fondo para mejor precisión
5. **Hablar claramente**: Pausas naturales mejoran la segmentación
