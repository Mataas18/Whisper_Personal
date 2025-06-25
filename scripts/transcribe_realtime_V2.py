import whisper
import pyaudio
import wave
import threading
import time
import os
from datetime import datetime
import keyboard
import numpy as np
import json
import re

class RealtimeTranscriber:
    def __init__(self, model_size="base", language="es"):
        self.model_size = model_size
        self.language = language
        self.model = None
        self.is_recording = False
        self.audio_frames = []
        
        # Obtener la ruta raíz del proyecto (un nivel arriba de scripts)
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Configuración de audio (mejorada)
        self.audio_quality = "ultra"  # low, medium, high, ultra
        self.setup_audio_config()
        
        # Palabras clave importantes (personalizables)
        self.keywords = [
            "importante", "urgente", "crítico", "clave", "fundamental",
            "decisión", "problema", "solución", "acción", "tarea",
            "fecha", "plazo", "deadline", "reunión", "contactar",
            "presupuesto", "coste", "precio", "dinero", "euro",
            "nombre", "teléfono", "email", "dirección"
        ]
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
    def setup_audio_config(self):
        """Configurar calidad de audio"""
        quality_configs = {
            "low": {"rate": 8000, "chunk": 512},
            "medium": {"rate": 16000, "chunk": 1024},
            "high": {"rate": 44100, "chunk": 2048},
            "ultra": {"rate": 48000, "chunk": 4096}
        }
        
        config = quality_configs.get(self.audio_quality, quality_configs["medium"])
        self.CHUNK = config["chunk"]
        self.RATE = config["rate"]
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        
    def detect_silence(self, audio_data):
        """Detectar silencio en los datos de audio - CORREGIDO"""
        if not self.silence_detection:
            return False
            
        # Convertir bytes a numpy array
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calcular RMS (Root Mean Square) para detectar volumen
        rms = np.sqrt(np.mean(audio_np**2))
        
        # Normalizar RMS a escala 0-1
        # Para int16, el rango máximo es -32768 a 32767
        normalized_rms = rms / 32768.0
        
        # DEBUG: Mostrar nivel de audio actual (opcional)
        # print(f"\rNivel audio: {normalized_rms:.4f} | Umbral: {self.silence_threshold}", end="")
        
        return normalized_rms < self.silence_threshold
        
    def extract_keywords(self, text):
        """Extraer palabras clave del texto"""
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                # Encontrar contexto (frase completa)
                sentences = re.split(r'[.!?]+', text)
                for sentence in sentences:
                    if keyword.lower() in sentence.lower():
                        found_keywords.append({
                            "keyword": keyword,
                            "context": sentence.strip(),
                            "position": text_lower.find(keyword.lower())
                        })
        
        return found_keywords
        
    def analyze_confidence(self, result):
        """Analizar confianza de cada segmento"""
        segments_info = []
        
        if hasattr(result, 'segments') and result.segments:
            for segment in result.segments:
                segment_info = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "confidence": getattr(segment, 'avg_logprob', 0),
                    "no_speech_prob": getattr(segment, 'no_speech_prob', 0)
                }
                
                # Clasificar confianza
                confidence = segment_info["confidence"]
                if confidence > -0.5:
                    confidence_level = "🟢 Alta"
                elif confidence > -1.0:
                    confidence_level = "🟡 Media"
                else:
                    confidence_level = "🔴 Baja"
                    
                segment_info["confidence_level"] = confidence_level
                segments_info.append(segment_info)
        
        return segments_info
        
    def load_model(self):
        """Cargar modelo de Whisper"""
        print(f"Cargando modelo {self.model_size}...")
        self.model = whisper.load_model(self.model_size)
        print("Modelo cargado correctamente!")
        
    def start_recording(self):
        """Iniciar grabación manual (sin detección automática de silencio)"""
        self.is_recording = True
        self.audio_frames = []
        
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        print(f"🎤 Grabando... (Calidad: {self.audio_quality}, {self.RATE}Hz)")
        print("🔴 GRABACIÓN ACTIVA - Presiona ESPACIO para parar, ESC para salir")
        
        while self.is_recording:
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.audio_frames.append(data)
                        
            except Exception as e:
                print(f"\nError en grabación: {e}")
                break
                
    def stop_recording(self):
        """Detener grabación"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            
    def save_audio(self, filename):
        """Guardar audio grabado con validación mejorada"""
        # Crear carpeta audio en la raíz del proyecto
        audio_dir = os.path.join(self.project_root, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        filepath = os.path.join(audio_dir, filename)
        
        try:
            wf = wave.open(filepath, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()
            
            # VALIDACIÓN MEJORADA DEL ARCHIVO
            print(f"📊 Validando archivo de audio...")
            
            # Verificar que el archivo existe
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"El archivo no se creó correctamente: {filepath}")
            
            # Verificar el tamaño del archivo
            file_size = os.path.getsize(filepath)
            print(f"   • Tamaño del archivo: {file_size} bytes")
            
            if file_size < 1000:  # Menos de 1KB
                print("   ⚠️  ADVERTENCIA: Archivo muy pequeño, puede estar vacío")
            
            # Verificar que se puede leer como WAV
            try:
                with wave.open(filepath, 'rb') as test_wav:
                    frames = test_wav.getnframes()
                    sample_rate = test_wav.getframerate()
                    channels = test_wav.getnchannels()
                    duration = frames / sample_rate
                    
                    print(f"   • Duración: {duration:.2f} segundos")
                    print(f"   • Sample rate: {sample_rate} Hz")
                    print(f"   • Canales: {channels}")
                    print(f"   • Frames: {frames}")
                    
                    if duration < 0.1:
                        print("   ⚠️  ADVERTENCIA: Duración muy corta")
                        
            except Exception as wav_error:
                print(f"   ❌ ERROR: No se puede leer como archivo WAV válido: {wav_error}")
                raise
            
            # Verificar permisos de lectura
            if not os.access(filepath, os.R_OK):
                print(f"   ❌ ERROR: No hay permisos de lectura para el archivo")
                raise PermissionError(f"Sin permisos de lectura: {filepath}")
            
            print(f"   ✅ Archivo válido y listo para transcripción")
            
        except Exception as e:
            print(f"❌ Error al guardar audio: {e}")
            raise
        
        return filepath
        
    def transcribe_audio(self, audio_path):
        """Transcribir audio con diagnóstico mejorado"""
        print("🔄 Transcribiendo...")
        
        # DIAGNÓSTICO PREVIO A LA TRANSCRIPCIÓN
        print(f"🔍 Diagnóstico del archivo:")
        print(f"   • Ruta: {audio_path}")
        print(f"   • Existe: {os.path.exists(audio_path)}")
        print(f"   • Ruta absoluta: {os.path.abspath(audio_path)}")
        print(f"   • Directorio de trabajo: {os.getcwd()}")
        
        if os.path.exists(audio_path):
            print(f"   • Tamaño: {os.path.getsize(audio_path)} bytes")
            print(f"   • Permisos de lectura: {os.access(audio_path, os.R_OK)}")
        
        # Verificar que el modelo está cargado
        if self.model is None:
            print("❌ ERROR: El modelo no está cargado")
            raise RuntimeError("Modelo no cargado")
        
        try:
            # Intentar cargar el archivo antes de la transcripción
            print("🔄 Verificando carga del archivo...")
            
            # Usar ruta absoluta para evitar problemas
            abs_path = os.path.abspath(audio_path)
            print(f"   • Usando ruta absoluta: {abs_path}")
            
            # Verificar que Whisper puede acceder al archivo
            import librosa
            try:
                # Intentar cargar con librosa (que usa Whisper internamente)
                y, sr = librosa.load(abs_path, sr=None)
                print(f"   • Carga con librosa exitosa: {len(y)} samples, {sr} Hz")
            except Exception as librosa_error:
                print(f"   ❌ Error con librosa: {librosa_error}")
                # Intentar con una copia temporal
                print("   🔄 Intentando crear copia temporal...")
                temp_path = abs_path.replace('.wav', '_temp.wav')
                import shutil
                shutil.copy2(abs_path, temp_path)
                abs_path = temp_path
                print(f"   • Usando archivo temporal: {abs_path}")
            
            # Transcribir con configuración robusta
            result = self.model.transcribe(
                abs_path,
                language=self.language,
                word_timestamps=True,
                verbose=True,  # Activar verbose para más información
                condition_on_previous_text=False,  # Evitar condicionamiento previo
                fp16=False  # Desactivar FP16 para mayor compatibilidad
            )
            
            # Limpiar archivo temporal si se creó
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
                print("   🗑️  Archivo temporal eliminado")
            
            return result
            
        except Exception as e:
            print(f"❌ Error detallado en transcripción:")
            print(f"   • Tipo de error: {type(e).__name__}")
            print(f"   • Mensaje: {str(e)}")
            print(f"   • Archivo problemático: {audio_path}")
            
            # Información adicional del sistema
            print(f"🔧 Información del sistema:")
            print(f"   • Python: {os.sys.version}")
            print(f"   • Directorio actual: {os.getcwd()}")
            print(f"   • Whisper instalado: {hasattr(whisper, '__version__')}")
            
            # Sugerencias de solución
            print(f"💡 Posibles soluciones:")
            print(f"   1. Verifica que ffmpeg esté instalado y en PATH")
            print(f"   2. Intenta con calidad de audio 'medium' o 'low'")
            print(f"   3. Verifica permisos de la carpeta de audio")
            print(f"   4. Reinicia el programa")
            
            raise
        
    def save_transcription(self, text, filename, keywords=None, confidence_info=None):
        """Guardar transcripción con información adicional"""
        # Crear carpeta output en la raíz del proyecto
        output_dir = os.path.join(self.project_root, "output", filename)
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.txt")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Modelo: {self.model_size}\n")
            f.write(f"Idioma: {self.language}\n")
            f.write(f"Calidad de audio: {self.audio_quality} ({self.RATE}Hz)\n")
            f.write("-" * 50 + "\n")
            f.write("TRANSCRIPCIÓN:\n")
            f.write(text)
            f.write("\n\n")
            
            # Añadir palabras clave si se encontraron
            if keywords:
                f.write("-" * 50 + "\n")
                f.write("PALABRAS CLAVE DETECTADAS:\n")
                for kw in keywords:
                    f.write(f"• {kw['keyword'].upper()}: {kw['context']}\n")
                f.write("\n")
            
            # Añadir información de confianza
            if confidence_info:
                f.write("-" * 50 + "\n")
                f.write("ANÁLISIS DE CONFIANZA:\n")
                for segment in confidence_info:
                    f.write(f"[{segment['start']:.1f}s-{segment['end']:.1f}s] {segment['confidence_level']}: {segment['text']}\n")
                f.write("\n")
        
        # Guardar también en JSON para análisis posterior
        json_filepath = os.path.join(output_dir, f"{filename}.json")
        data = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model_size,
            "language": self.language,
            "audio_quality": self.audio_quality,
            "text": text,
            "keywords": keywords or [],
            "confidence_analysis": confidence_info or []
        }
        
        with open(json_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
        
    def show_main_menu(self):
        """Mostrar menú principal al iniciar"""
        print("\n" + "="*60)
        print("🎙️  TRANSCRIPTOR EN TIEMPO REAL - WHISPER")
        print("="*60)
        print(f"📊 Configuración actual:")
        print(f"   • Modelo: {self.model_size}")
        print(f"   • Idioma: {self.language}")
        print(f"   • Calidad audio: {self.audio_quality} ({self.RATE}Hz)")
        print("="*60)
        print("1️⃣  Iniciar transcripción")
        print("2️⃣  Configurar ajustes")
        print("3️⃣  Ver información de modelos")
        print("4️⃣  Salir del programa")
        print("-" * 60)
        print("Elige una opción (1/2/3/4)...")
        
        while True:
            if keyboard.is_pressed('1'):
                while keyboard.is_pressed('1'): time.sleep(0.1)
                print("✅ Iniciando modo transcripción...")
                return "transcribe"
                
            elif keyboard.is_pressed('2'):
                while keyboard.is_pressed('2'): time.sleep(0.1)
                print("✅ Abriendo configuración...")
                return "config"
                
            elif keyboard.is_pressed('3'):
                while keyboard.is_pressed('3'): time.sleep(0.1)
                print("✅ Mostrando información de modelos...")
                return "models"
                
            elif keyboard.is_pressed('4') or keyboard.is_pressed('esc'):
                while keyboard.is_pressed('4') or keyboard.is_pressed('esc'): time.sleep(0.1)
                print("✅ Saliendo del programa...")
                return "exit"
            
            time.sleep(0.1)
    
    def show_model_info(self):
        """Mostrar información de modelos disponibles"""
        print("\n" + "="*60)
        print("📋 MODELOS WHISPER DISPONIBLES")
        print("="*60)
        
        model_info = {
            "tiny": {"size": "39 MB", "speed": "~32x", "quality": "⭐⭐"},
            "base": {"size": "74 MB", "speed": "~16x", "quality": "⭐⭐⭐"},
            "small": {"size": "244 MB", "speed": "~6x", "quality": "⭐⭐⭐⭐"},
            "medium": {"size": "769 MB", "speed": "~2x", "quality": "⭐⭐⭐⭐⭐"},
            "large-v1": {"size": "1550 MB", "speed": "1x", "quality": "⭐⭐⭐⭐⭐⭐"},
            "large-v2": {"size": "1550 MB", "speed": "1x", "quality": "⭐⭐⭐⭐⭐⭐"},
            "large-v3": {"size": "1550 MB", "speed": "1x", "quality": "⭐⭐⭐⭐⭐⭐"},
            "turbo": {"size": "809 MB", "speed": "~8x", "quality": "⭐⭐⭐⭐⭐"}
        }
        
        for model, info in model_info.items():
            current = " ← ACTUAL" if model == self.model_size else ""
            print(f"🔸 {model:8} | {info['size']:8} | {info['speed']:4} | {info['quality']} {current}")
        
        print("-" * 60)
        print("💡 Recomendaciones:")
        print("   🚀 Para velocidad: tiny, base")
        print("   ⚖️  Balance: small, turbo")
        print("   🎯 Máxima calidad: medium, large")
        print("   🎮 Tu RTX 3060: Cualquier modelo funciona bien")
        
        print("\nPresiona ENTER para volver al menú principal...")
        while True:
            if keyboard.is_pressed('enter'):
                while keyboard.is_pressed('enter'): time.sleep(0.1)
                break
            time.sleep(0.1)
    def run_continuous(self):
        """Flujo principal del programa"""
        # Mostrar menú principal primero
        while True:
            choice = self.show_main_menu()
            
            if choice == "transcribe":
                self.start_transcription_mode()
            elif choice == "config":
                self.show_config_menu()
            elif choice == "models":
                self.show_model_info()
            elif choice == "exit":
                print("\n👋 ¡Hasta luego!")
                return
    
    def start_transcription_mode(self):
        """Modo de transcripción (el código anterior)"""
        # Cargar modelo solo cuando se necesite
        if self.model is None:
            self.load_model()
        
        session_num = 1
        last_transcription = ""
        last_transcription_file = ""
        
        print("\n" + "="*60)
        print("🎙️  MODO TRANSCRIPCIÓN ACTIVADO")
        print("="*60)
        print("Controles durante grabación:")
        print("  ESPACIO: Parar grabación y transcribir")
        print("  ESC: Volver al menú principal")
        print("="*60)
        
        try:
            while True:
                print(f"\n--- SESIÓN {session_num} ---")
                
                # Si hay transcripción previa, mostrar menú de sesión
                if session_num > 1:
                    choice = self.show_session_menu()
                    if choice == "nueva":
                        pass  # Continúa con nueva grabación
                    elif choice == "mostrar":
                        self.show_last_transcription(last_transcription, last_transcription_file)
                        continue  # Volver al menú
                    elif choice == "config":
                        self.show_config_menu()
                        continue  # Volver al menú
                    elif choice == "menu_principal":
                        return  # Volver al menú principal
                    elif choice == "salir":
                        print("\n👋 ¡Hasta luego!")
                        exit()
                
                print("🎤 Presiona ENTER para empezar a grabar...")
                
                # Esperar ENTER para empezar
                start_recording = False
                while not start_recording:
                    if keyboard.is_pressed('enter'):
                        start_recording = True
                    elif keyboard.is_pressed('esc'):
                        return  # Volver al menú principal
                    time.sleep(0.1)
                
                # Empezar grabación en hilo separado
                recording_thread = threading.Thread(target=self.start_recording)
                recording_thread.start()
                
                # Esperar ESPACIO para parar o ESC para salir
                while self.is_recording:
                    if keyboard.is_pressed('space'):
                        self.stop_recording()
                        break
                    elif keyboard.is_pressed('esc'):
                        self.stop_recording()
                        recording_thread.join()
                        return  # Volver al menú principal
                    time.sleep(0.1)
                
                recording_thread.join()
                
                if len(self.audio_frames) > 0:
                    # Guardar audio
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    audio_filename = f"grabacion_{timestamp}.wav"
                    
                    try:
                        audio_path = self.save_audio(audio_filename)
                        print(f"💾 Audio guardado: {audio_path}")
                        
                        # Transcribir
                        result = self.transcribe_audio(audio_path)
                        transcription = result["text"]
                        
                        # Análisis de palabras clave
                        keywords = self.extract_keywords(transcription)
                        
                        # Análisis de confianza
                        confidence_info = self.analyze_confidence(result)
                        
                        print("\n" + "="*50)
                        print("📝 TRANSCRIPCIÓN:")
                        print("="*50)
                        print(transcription)
                        
                        # Mostrar palabras clave si se encontraron
                        if keywords:
                            print("\n" + "🔍 PALABRAS CLAVE DETECTADAS:")
                            print("-" * 30)
                            for kw in keywords[:5]:  # Mostrar solo las primeras 5
                                print(f"🔑 {kw['keyword'].upper()}: {kw['context']}")
                        
                        # Mostrar análisis de confianza
                        if confidence_info:
                            print(f"\n📊 ANÁLISIS DE CONFIANZA:")
                            print("-" * 30)
                            for segment in confidence_info[:3]:  # Mostrar solo los primeros 3
                                print(f"{segment['confidence_level']} [{segment['start']:.1f}s]: {segment['text'][:50]}...")
                        
                        print("="*50)
                        
                        # Guardar transcripción con toda la información
                        trans_filename = f"transcripcion_{timestamp}"
                        trans_path = self.save_transcription(transcription, trans_filename, keywords, confidence_info)
                        print(f"💾 Transcripción guardada: {trans_path}")
                        
                        # Guardar para mostrar en menú
                        last_transcription = transcription
                        last_transcription_file = trans_path
                        
                    except Exception as e:
                        print(f"❌ Error en el proceso: {e}")
                        last_transcription = ""
                        last_transcription_file = ""
                else:
                    print("⚠️  No se grabó audio")
                    last_transcription = ""
                    last_transcription_file = ""
                
                session_num += 1
                time.sleep(1)  # Pausa pequeña
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
        finally:
            self.cleanup()
    
    def show_session_menu(self):
        """Mostrar menú entre sesiones"""
        print("\n" + "="*50)
        print("📋 ¿QUÉ QUIERES HACER?")
        print("="*50)
        print("1️⃣  Iniciar nueva grabación")
        print("2️⃣  Ver última transcripción")
        print("3️⃣  Configurar ajustes")
        print("4️⃣  Volver al menú principal")
        print("5️⃣  Salir del programa")
        print("-" * 50)
        print("Elige una opción (1/2/3/4/5)...")
        
        option_selected = False
        
        while not option_selected:
            # Detectar teclas con control de estado
            if keyboard.is_pressed('1'):
                print("✅ Nueva grabación seleccionada")
                # Esperar a que se suelte la tecla
                while keyboard.is_pressed('1'):
                    time.sleep(0.1)
                return "nueva"
                
            elif keyboard.is_pressed('2'):
                print("✅ Mostrar transcripción seleccionada")
                # Esperar a que se suelte la tecla
                while keyboard.is_pressed('2'):
                    time.sleep(0.1)
                return "mostrar"
                
            elif keyboard.is_pressed('3'):
                print("✅ Configuración seleccionada")
                # Esperar a que se suelte la tecla
                while keyboard.is_pressed('3'):
                    time.sleep(0.1)
                return "config"
                
            elif keyboard.is_pressed('4'):
                print("✅ Volver al menú principal")
                # Esperar a que se suelte la tecla
                while keyboard.is_pressed('4'):
                    time.sleep(0.1)
                return "menu_principal"
                
            elif keyboard.is_pressed('5') or keyboard.is_pressed('esc'):
                print("✅ Salir seleccionado")
                # Esperar a que se suelte la tecla
                while keyboard.is_pressed('5') or keyboard.is_pressed('esc'):
                    time.sleep(0.1)
                return "salir"
            
            time.sleep(0.1)
    
    def show_config_menu(self):
        """Mostrar menú de configuración"""
        while True:
            print("\n" + "="*50)
            print("⚙️  CONFIGURACIÓN")
            print("="*50)
            print(f"1️⃣  Modelo Whisper: {self.model_size}")
            print(f"2️⃣  Calidad de audio: {self.audio_quality} ({self.RATE}Hz)")
            print(f"3️⃣  Gestionar palabras clave ({len(self.keywords)} actuales)")
            print("4️⃣  Volver al menú principal")
            print("-" * 50)
            print("Elige una opción (1-4)...")
            
            while True:
                if keyboard.is_pressed('1'):
                    while keyboard.is_pressed('1'): time.sleep(0.1)
                    self.change_model()
                    break
                elif keyboard.is_pressed('2'):
                    while keyboard.is_pressed('2'): time.sleep(0.1)
                    self.change_audio_quality()
                    break
                elif keyboard.is_pressed('3'):
                    while keyboard.is_pressed('3'): time.sleep(0.1)
                    self.manage_keywords()
                    break
                elif keyboard.is_pressed('4') or keyboard.is_pressed('esc'):
                    while keyboard.is_pressed('4') or keyboard.is_pressed('esc'): time.sleep(0.1)
                    return
                time.sleep(0.1)
    
    def change_model(self):
        """Cambiar modelo de Whisper"""
        models = ["tiny", "base", "small", "medium", "large-v1", "large-v2", "large-v3", "turbo"]
        
        print("\n" + "="*50)
        print("🧠 SELECCIONAR MODELO WHISPER")
        print("="*50)
        print("Modelos disponibles (compatibles con español):")
        
        for i, model in enumerate(models, 1):
            current = " ← ACTUAL" if model == self.model_size else ""
            size_info = {
                "tiny": "39 MB - Muy rápido",
                "base": "74 MB - Equilibrado", 
                "small": "244 MB - Buena calidad",
                "medium": "769 MB - Alta calidad",
                "large-v1": "1550 MB - Máxima calidad v1",
                "large-v2": "1550 MB - Máxima calidad v2",
                "large-v3": "1550 MB - Máxima calidad v3 (recomendado)",
                "turbo": "809 MB - Rápido y buena calidad"
            }
            print(f"{i}️⃣  {model:10} ({size_info[model]}){current}")
        
        print("9️⃣  Cancelar")
        print("-" * 50)
        print("Elige un modelo (1-9)...")
        
        while True:
            for i, model in enumerate(models, 1):
                if keyboard.is_pressed(str(i)):
                    while keyboard.is_pressed(str(i)): time.sleep(0.1)
                    
                    if model != self.model_size:
                        old_model = self.model_size
                        self.model_size = model
                        
                        # Si ya había un modelo cargado, necesitamos recargarlo
                        if self.model is not None:
                            print(f"🔄 Cambiando de {old_model} a {model}...")
                            print("⚠️  Se recargará el modelo en la próxima transcripción")
                            self.model = None  # Forzar recarga
                        
                        print(f"✅ Modelo cambiado a: {model}")
                    else:
                        print(f"ℹ️  Ya estás usando el modelo {model}")
                    
                    time.sleep(1.5)
                    return
            
            if keyboard.is_pressed('9') or keyboard.is_pressed('esc'):
                while keyboard.is_pressed('9') or keyboard.is_pressed('esc'): time.sleep(0.1)
                print("❌ Cambio de modelo cancelado")
                time.sleep(1)
                return
            
            time.sleep(0.1)

    def change_audio_quality(self):
        """Cambiar calidad de audio"""
        qualities = ["low", "medium", "high", "ultra"]
        current_index = qualities.index(self.audio_quality)
        next_index = (current_index + 1) % len(qualities)
        
        self.audio_quality = qualities[next_index]
        self.setup_audio_config()
        
        print(f"✅ Calidad cambiada a: {self.audio_quality} ({self.RATE}Hz)")
        time.sleep(1)
    
    def manage_keywords(self):
        """Gestionar palabras clave"""
        print("\n🔑 PALABRAS CLAVE ACTUALES:")
        for i, kw in enumerate(self.keywords[:10], 1):
            print(f"{i:2d}. {kw}")
        if len(self.keywords) > 10:
            print(f"    ... y {len(self.keywords) - 10} más")
        
        print("\nPresiona ENTER para continuar...")
        while True:
            if keyboard.is_pressed('enter'):
                while keyboard.is_pressed('enter'): time.sleep(0.1)
                break
            time.sleep(0.1)
    
    def show_last_transcription(self, transcription, file_path):
        """Mostrar la última transcripción"""
        print("\n" + "="*60)
        print("📄 ÚLTIMA TRANSCRIPCIÓN")
        print("="*60)
        
        if transcription:
            print(transcription)
            print("-" * 60)
            print(f"📁 Archivo: {file_path}")
        else:
            print("⚠️  No hay transcripción disponible")
        
        print("="*60)
        print("Presiona ENTER para volver al menú...")
        
        # Esperar ENTER específicamente
        key_pressed = False
        while not key_pressed:
            if keyboard.is_pressed('enter'):
                # Esperar a que se suelte la tecla
                while keyboard.is_pressed('enter'):
                    time.sleep(0.1)
                key_pressed = True
            time.sleep(0.1)
            
    def cleanup(self):
        """Limpiar recursos"""
        if self.stream:
            self.stream.close()
        self.audio.terminate()

def main():
    import sys
    
    # Argumentos opcionales
    if len(sys.argv) == 1:
        # Sin argumentos
        model_size = "base"
        language = "es"
    elif len(sys.argv) == 2:
        # Un argumento: puede ser modelo o idioma
        arg = sys.argv[1]
        if arg in ['tiny', 'base', 'small', 'medium', 'large', 'large-v1', 'large-v2', 'large-v3', 'turbo']:
            model_size = arg
            language = "es"
        else:
            model_size = "base"
            language = arg
    else:
        # Dos o más argumentos: modelo e idioma
        model_size = sys.argv[1]
        language = sys.argv[2]
    
    print(f"Configuración: Modelo={model_size}, Idioma={language}")
    
    # VERIFICACIÓN INICIAL DEL SISTEMA
    print("\n🔧 Verificando dependencias del sistema...")
    
    # Verificar ffmpeg
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg encontrado y funcionando")
        else:
            print("⚠️  FFmpeg encontrado pero puede tener problemas")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print("❌ FFmpeg NO encontrado o no funciona")
        print("💡 Instala FFmpeg desde: https://ffmpeg.org/download.html")
        print("   Y asegúrate de que esté en tu PATH del sistema")
        
        response = input("\n¿Quieres continuar de todos modos? (s/n): ")
        if response.lower() not in ['s', 'sí', 'si', 'y', 'yes']:
            print("👋 Saliendo del programa...")
            return
    
    # Verificar librosa
    try:
        import librosa
        print("✅ Librosa disponible")
    except ImportError:
        print("⚠️  Librosa no encontrado, instalando...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'librosa'], check=True)
            print("✅ Librosa instalado correctamente")
        except subprocess.CalledProcessError:
            print("❌ Error instalando librosa")
    
    # Verificar permisos de escritura
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            tmp.write(b"test")
        print("✅ Permisos de escritura OK")
    except Exception as e:
        print(f"❌ Problemas con permisos de escritura: {e}")
    
    print("🚀 Iniciando transcriptor...")
    
    transcriber = RealtimeTranscriber(model_size, language)
    transcriber.run_continuous()

if __name__ == "__main__":
    main()