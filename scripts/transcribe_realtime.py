import whisper
import pyaudio
import wave
import threading
import time
import os
from datetime import datetime
import keyboard

class RealtimeTranscriber:
    def __init__(self, model_size="base", language="es"):
        self.model_size = model_size
        self.language = language
        self.model = None
        self.is_recording = False
        self.audio_frames = []
        
        # Configuración de audio
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
    def load_model(self):
        """Cargar modelo de Whisper"""
        print(f"Cargando modelo {self.model_size}...")
        self.model = whisper.load_model(self.model_size)
        print("Modelo cargado correctamente!")
        
    def start_recording(self):
        """Iniciar grabación"""
        self.is_recording = True
        self.audio_frames = []
        
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        print("🎤 Grabando... (Presiona ESPACIO para parar y transcribir, ESC para salir)")
        
        while self.is_recording:
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.audio_frames.append(data)
            except Exception as e:
                print(f"Error en grabación: {e}")
                break
                
    def stop_recording(self):
        """Detener grabación"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            
    def save_audio(self, filename):
        """Guardar audio grabado"""
        os.makedirs("audio", exist_ok=True)
        filepath = f"audio/{filename}"
        
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.audio_frames))
        wf.close()
        
        return filepath
        
    def transcribe_audio(self, audio_path):
        """Transcribir audio"""
        print("🔄 Transcribiendo...")
        result = self.model.transcribe(audio_path, language=self.language)
        return result["text"]
        
    def save_transcription(self, text, filename):
        """Guardar transcripción"""
        os.makedirs("output", exist_ok=True)
        filepath = f"output/{filename}.txt"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Modelo: {self.model_size}\n")
            f.write(f"Idioma: {self.language}\n")
            f.write("-" * 50 + "\n")
            f.write(text)
            
        return filepath
        
    def run_continuous(self):
        """Modo continuo - grabar, transcribir, repetir"""
        self.load_model()
        session_num = 1
        last_transcription = ""
        last_transcription_file = ""
        
        print("\n" + "="*60)
        print("🎙️  TRANSCRIPTOR EN TIEMPO REAL")
        print("="*60)
        print("Controles durante grabación:")
        print("  ESPACIO: Parar grabación y transcribir")
        print("  ESC: Salir")
        print("="*60)
        
        try:
            while True:
                print(f"\n--- SESIÓN {session_num} ---")
                
                # Si hay transcripción previa, mostrar menú
                if session_num > 1:
                    choice = self.show_session_menu()
                    if choice == "nueva":
                        pass  # Continúa con nueva grabación
                    elif choice == "mostrar":
                        self.show_last_transcription(last_transcription, last_transcription_file)
                        continue  # Volver al menú
                    elif choice == "salir":
                        print("\n👋 ¡Hasta luego!")
                        return
                
                print("🎤 Presiona ENTER para empezar a grabar...")
                
                # Esperar ENTER para empezar
                while True:
                    if keyboard.is_pressed('enter'):
                        break
                    elif keyboard.is_pressed('esc'):
                        print("\n👋 ¡Hasta luego!")
                        return
                    time.sleep(0.1)
                
                # Empezar grabación en hilo separado
                recording_thread = threading.Thread(target=self.start_recording)
                recording_thread.start()
                
                print("🔴 GRABANDO... (ESPACIO para parar, ESC para salir)")
                
                # Esperar ESPACIO para parar
                while self.is_recording:
                    if keyboard.is_pressed('space'):
                        self.stop_recording()
                        break
                    elif keyboard.is_pressed('esc'):
                        self.stop_recording()
                        print("\n👋 ¡Hasta luego!")
                        return
                    time.sleep(0.1)
                
                recording_thread.join()
                
                if len(self.audio_frames) > 0:
                    # Guardar audio
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    audio_filename = f"grabacion_{timestamp}.wav"
                    audio_path = self.save_audio(audio_filename)
                    print(f"💾 Audio guardado: {audio_path}")
                    
                    # Transcribir
                    try:
                        transcription = self.transcribe_audio(audio_path)
                        
                        print("\n" + "="*50)
                        print("📝 TRANSCRIPCIÓN:")
                        print("="*50)
                        print(transcription)
                        print("="*50)
                        
                        # Guardar transcripción
                        trans_filename = f"transcripcion_{timestamp}"
                        trans_path = self.save_transcription(transcription, trans_filename)
                        print(f"💾 Transcripción guardada: {trans_path}")
                        
                        # Guardar para mostrar en menú
                        last_transcription = transcription
                        last_transcription_file = trans_path
                        
                    except Exception as e:
                        print(f"❌ Error en transcripción: {e}")
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
        print("3️⃣  Salir del programa")
        print("-" * 50)
        print("Elige una opción (1/2/3)...")
        
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
                
            elif keyboard.is_pressed('3') or keyboard.is_pressed('esc'):
                print("✅ Salir seleccionado")
                # Esperar a que se suelte la tecla
                while keyboard.is_pressed('3') or keyboard.is_pressed('esc'):
                    time.sleep(0.1)
                return "salir"
            
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
    
    transcriber = RealtimeTranscriber(model_size, language)
    transcriber.run_continuous()

if __name__ == "__main__":
    main()