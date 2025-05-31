import torch
import whisper

print("=== Verificación del entorno ===")
print(f"CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Dispositivo CUDA: {torch.cuda.get_device_name(0)}")
    print(f"Memoria GPU disponible: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

print(f"Versión de PyTorch: {torch.__version__}")

# Cargar modelo pequeño para prueba
try:
    model = whisper.load_model("base")
    print("Whisper cargado correctamente")
except Exception as e:
    print(f"Error cargando Whisper: {e}")