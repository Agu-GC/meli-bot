#!/bin/bash
set -e  # Detiene el script ante cualquier error

if [ -f ".env" ]; then
    source .env
else
    echo "❌ No se encontró el archivo .env"
    exit 1
fi

# =============================================
# 1. VERIFICACIÓN E INSTALACIÓN DE OLLAMA
# =============================================
echo "🔍 Verificando instalación de Ollama..."

if [[ ! -f "/usr/local/bin/ollama" && ! -f "/Applications/Ollama.app/Contents/Resources/ollama" ]]; then
    echo "⚙️ Ollama no está instalado. Instalando..."
    brew install ollama || {
        echo "❌ Error: No se pudo instalar Ollama con Homebrew. Por favor, instálalo manualmente."
        exit 1
    }
    echo "✅ Ollama instalado correctamente"
fi

# =============================================
# 2. INICIO DEL SERVICIO
# =============================================
echo "🚀 Iniciando servicio Ollama..."
export OLLAMA_USE_METAL=1
export OLLAMA_FLASH_ATTENTION=1

if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "🔌 Iniciando Ollama en segundo plano..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    
    timeout=30
    while [ $timeout -gt 0 ]; do
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            break
        fi
        sleep 1
        ((timeout--))
    done
    
    if [ $timeout -eq 0 ]; then
        echo "❌ Error: Timeout al iniciar Ollama. Ver logs en /tmp/ollama.log"
        echo "ℹ️ Intenta iniciar Ollama manualmente: ollama serve"
        exit 1
    fi
else
    echo "✅ Ollama ya está en ejecución"
fi

# =============================================
# 3. DESCARGAR MODELO 
# =============================================
echo "📥 Descargando modelo $OLLAMA_MODEL ..."
ollama pull $OLLAMA_MODEL || {
    echo "⚠️ Falló la descarga automática, intentando con modelo por defecto..."
    ollama pull phi3
}

# =============================================
# 4. EJECUTAR DOCKER COMPOSE
# =============================================
echo "🐳 Iniciando Docker Compose..."
docker-compose up --build