import whisper
import torch
import json
from typing import Dict, Any

def get_available_models() -> Dict[str, Any]:
    """
    Obtener lista de modelos disponibles directamente desde Whisper
    """
    return whisper.available_models()

def get_model_info():
    """
    Obtener información detallada de cada modelo
    """
    # Información conocida de los modelos (desde la documentación oficial)
    model_specs = {
        "tiny.en": {
            "parameters": "39 M",
            "vram_required": "~1 GB",
            "relative_speed": "~32x",
            "english_only": True,
            "size_mb": 39
        },
        "tiny": {
            "parameters": "39 M", 
            "vram_required": "~1 GB",
            "relative_speed": "~32x",
            "english_only": False,
            "size_mb": 39
        },
        "base.en": {
            "parameters": "74 M",
            "vram_required": "~1 GB", 
            "relative_speed": "~16x",
            "english_only": True,
            "size_mb": 74
        },
        "base": {
            "parameters": "74 M",
            "vram_required": "~1 GB",
            "relative_speed": "~16x", 
            "english_only": False,
            "size_mb": 74
        },
        "small.en": {
            "parameters": "244 M",
            "vram_required": "~2 GB",
            "relative_speed": "~6x",
            "english_only": True,
            "size_mb": 244
        },
        "small": {
            "parameters": "244 M",
            "vram_required": "~2 GB", 
            "relative_speed": "~6x",
            "english_only": False,
            "size_mb": 244
        },
        "medium.en": {
            "parameters": "769 M",
            "vram_required": "~5 GB",
            "relative_speed": "~2x",
            "english_only": True,
            "size_mb": 769
        },
        "medium": {
            "parameters": "769 M",
            "vram_required": "~5 GB",
            "relative_speed": "~2x",
            "english_only": False,
            "size_mb": 769
        },
        "large-v1": {
            "parameters": "1550 M",
            "vram_required": "~10 GB", 
            "relative_speed": "1x",
            "english_only": False,
            "size_mb": 1550
        },
        "large-v2": {
            "parameters": "1550 M",
            "vram_required": "~10 GB",
            "relative_speed": "1x", 
            "english_only": False,
            "size_mb": 1550
        },
        "large-v3": {
            "parameters": "1550 M",
            "vram_required": "~10 GB",
            "relative_speed": "1x",
            "english_only": False,
            "size_mb": 1550
        },
        "large": {
            "parameters": "1550 M",
            "vram_required": "~10 GB",
            "relative_speed": "1x",
            "english_only": False,
            "size_mb": 1550
        },
        "large-v3-turbo": {
            "parameters": "809 M",
            "vram_required": "~6 GB",
            "relative_speed": "~8x",
            "english_only": False,
            "size_mb": 809
        },
        "turbo": {
            "parameters": "809 M", 
            "vram_required": "~6 GB",
            "relative_speed": "~8x",
            "english_only": False,
            "size_mb": 809
        }
    }
    
    return model_specs

def check_system_compatibility():
    """
    Verificar compatibilidad del sistema
    """
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        return {
            "cuda": True,
            "gpu_name": gpu_name,
            "gpu_memory_gb": round(gpu_memory, 1)
        }
    else:
        return {
            "cuda": False,
            "gpu_name": "CPU Only",
            "gpu_memory_gb": 0
        }

def get_recommended_models(gpu_memory_gb: float):
    """
    Recomendar modelos basados en la memoria GPU disponible
    """
    if gpu_memory_gb >= 12:
        return ["large", "large-v3", "turbo"]
    elif gpu_memory_gb >= 8:
        return ["medium", "turbo"]
    elif gpu_memory_gb >= 4:
        return ["small", "base"]
    else:
        return ["tiny", "base"]

def print_models_info():
    """
    Mostrar información completa de modelos
    """
    print("🎯 MODELOS WHISPER DISPONIBLES")
    print("=" * 80)
    
    # Obtener información del sistema
    system_info = check_system_compatibility()
    print(f"💻 Sistema: {system_info['gpu_name']}")
    if system_info['cuda']:
        print(f"🎮 Memoria GPU: {system_info['gpu_memory_gb']} GB")
    print()
    
    # Obtener modelos disponibles
    available_models = get_available_models()
    model_specs = get_model_info()
    
    print(f"📋 Modelos disponibles: {len(available_models)}")
    print()
    
    # Mostrar cada modelo
    for i, model_name in enumerate(sorted(available_models), 1):
        specs = model_specs.get(model_name, {})
        
        print(f"{i:2d}. {model_name}")
        print(f"    📊 Parámetros: {specs.get('parameters', 'N/A')}")
        print(f"    💾 Tamaño: {specs.get('size_mb', 'N/A')} MB")
        print(f"    🎮 VRAM requerida: {specs.get('vram_required', 'N/A')}")
        print(f"    ⚡ Velocidad relativa: {specs.get('relative_speed', 'N/A')}")
        print(f"    🌍 Solo inglés: {'Sí' if specs.get('english_only', False) else 'No'}")
        
        # Indicar compatibilidad
        if system_info['cuda']:
            vram_req = specs.get('vram_required', '').replace('~', '').replace(' GB', '').replace(' ', '')
            try:
                vram_needed = float(vram_req) if vram_req.replace('.', '').isdigit() else 0
                if vram_needed <= system_info['gpu_memory_gb']:
                    print(f"    ✅ Compatible con tu GPU")
                else:
                    print(f"    ⚠️  Podría ser lento (necesita más VRAM)")
            except:
                print(f"    ❓ Compatibilidad desconocida")
        
        print()
    
    # Recomendaciones
    if system_info['cuda']:
        recommended = get_recommended_models(system_info['gpu_memory_gb'])
        print("🎯 RECOMENDADOS PARA TU SISTEMA:")
        for model in recommended:
            print(f"   ✨ {model}")
        print()
    
    print("💡 GUÍA DE SELECCIÓN:")
    print("   🚀 Para velocidad máxima: tiny, base")
    print("   ⚖️  Para balance velocidad/precisión: small, turbo")
    print("   🎯 Para máxima precisión: medium, large, large-v3")
    print("   🌍 Para solo inglés: modelos terminados en '.en'")

def get_model_by_name(model_name: str):
    """
    Obtener información específica de un modelo
    """
    available = get_available_models()
    specs = get_model_info()
    
    if model_name not in available:
        print(f"❌ Modelo '{model_name}' no encontrado")
        print(f"Modelos disponibles: {', '.join(sorted(available))}")
        return None
    
    spec = specs.get(model_name, {})
    
    print(f"📋 INFORMACIÓN DEL MODELO: {model_name}")
    print("=" * 50)
    print(f"📊 Parámetros: {spec.get('parameters', 'N/A')}")
    print(f"💾 Tamaño: {spec.get('size_mb', 'N/A')} MB") 
    print(f"🎮 VRAM requerida: {spec.get('vram_required', 'N/A')}")
    print(f"⚡ Velocidad relativa: {spec.get('relative_speed', 'N/A')}")
    print(f"🌍 Solo inglés: {'Sí' if spec.get('english_only', False) else 'No'}")
    
    return spec

def main():
    import sys
    
    if len(sys.argv) > 1:
        # Mostrar info de modelo específico
        model_name = sys.argv[1]
        get_model_by_name(model_name)
    else:
        # Mostrar todos los modelos
        print_models_info()

if __name__ == "__main__":
    main()