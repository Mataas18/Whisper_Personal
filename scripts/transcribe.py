import whisper
import sys
import os

def transcribe_audio(audio_path, model_size="base", language=None):
    """
    Transcribir archivo de audio usando Whisper
    """
    print(f"Cargando modelo {model_size}...")
    model = whisper.load_model(model_size)
    
    print(f"Transcribiendo: {audio_path}")
    result = model.transcribe(audio_path, language=language)
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python transcribe.py <archivo_audio> [modelo] [idioma]")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else "base"
    language = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(audio_file):
        print(f"Error: No se encuentra el archivo {audio_file}")
        sys.exit(1)
    
    result = transcribe_audio(audio_file, model_size, language)
    
    print("\n=== TRANSCRIPCIÓN ===")
    print(result["text"])
    
    # Guardar transcripción
    output_file = f"output/{os.path.basename(audio_file)}.txt"
    os.makedirs("output", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result["text"])
    
    print(f"\nTranscripción guardada en: {output_file}")